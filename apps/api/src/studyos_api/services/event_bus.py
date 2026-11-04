"""Event bus service — Redis Streams-based event publishing and consuming."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

import structlog

from studyos_api.services.event_types import StudyOSEvent

if TYPE_CHECKING:
    from redis.asyncio import Redis

logger = structlog.get_logger(__name__)

_STREAM_NAME = "studyos:events"
_DLQ_NAME = "studyos:events:dead_letter"
_PROCESSED_KEY = "studyos:events:processed"
_MAX_STREAM_LENGTH = 100_000
_MAX_DLQ_LENGTH = 10_000

EventHandler = Callable[[StudyOSEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Redis Streams-based event bus with dead letter queue and idempotency."""

    def __init__(self, redis: Redis | None = None) -> None:
        self._redis = redis
        self._handlers: dict[str, list[EventHandler]] = {}
        self._consumer_groups: dict[str, str] = {}

    async def publish(self, event: StudyOSEvent) -> str | None:
        """Publish an event to the stream. Returns message ID or None if Redis unavailable."""
        if self._redis is None:
            logger.debug("event_bus.no_redis", event_type=event.event_type)
            return None

        if await self._is_duplicate(event):
            logger.debug("event_bus.duplicate", event_id=str(event.event_id))
            return None

        try:
            data = event.to_dict()
            message_id = await self._redis.xadd(
                _STREAM_NAME,
                data,
                maxlen=_MAX_STREAM_LENGTH,
                approximate=True,
            )
            logger.info("event_bus.published", event_type=event.event_type, message_id=message_id)
            return message_id
        except Exception:
            logger.exception("event_bus.publish_failed", event_type=event.event_type)
            return None

    async def consume(
        self,
        group_name: str,
        consumer_name: str,
        batch_size: int = 10,
        timeout_ms: int = 5000,
    ) -> list[tuple[str, dict[str, str]]]:
        """Consume events from the stream using a consumer group."""
        if self._redis is None:
            return []

        await self._ensure_consumer_group(group_name)

        try:
            messages = await self._redis.xreadgroup(
                group_name,
                consumer_name,
                {_STREAM_NAME: ">"},
                count=batch_size,
                block=timeout_ms,
            )
            if not messages:
                return []

            result = []
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    result.append(
                        (
                            msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                            {
                                k.decode() if isinstance(k, bytes) else k: v.decode()
                                if isinstance(v, bytes)
                                else v
                                for k, v in fields.items()
                            },
                        )
                    )
            return result
        except Exception:
            logger.exception("event_bus.consume_failed", group=group_name)
            return []

    async def acknowledge(self, group_name: str, message_id: str) -> None:
        """Acknowledge a processed message."""
        if self._redis is None:
            return
        try:
            await self._redis.xack(_STREAM_NAME, group_name, message_id)
        except Exception:
            logger.exception("event_bus.ack_failed", message_id=message_id)

    async def move_to_dlq(self, event: StudyOSEvent, error: str) -> None:
        """Move a failed event to the dead letter queue."""
        if self._redis is None:
            return
        try:
            data = event.to_dict()
            data["dlq_error"] = error
            data["dlq_timestamp"] = str(__import__("datetime").datetime.now().isoformat())
            await self._redis.xadd(
                _DLQ_NAME,
                data,
                maxlen=_MAX_DLQ_LENGTH,
                approximate=True,
            )
            logger.warning("event_bus.dlq", event_type=event.event_type, error=error)
        except Exception:
            logger.exception("event_bus.dlq_failed")

    async def get_dlq_count(self) -> int:
        """Get the number of messages in the dead letter queue."""
        if self._redis is None:
            return 0
        try:
            return await self._redis.xlen(_DLQ_NAME)
        except Exception:
            return 0

    async def retry_dlq_message(self, message_id: str) -> bool:
        """Retry a message from the dead letter queue."""
        if self._redis is None:
            return False
        try:
            messages = await self._redis.xrange(_DLQ_NAME, min=message_id, max=message_id)
            if not messages:
                return False

            _, fields = messages[0]
            decoded_fields = {
                k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v
                for k, v in fields.items()
            }
            event = StudyOSEvent.from_dict(decoded_fields)
            await self.publish(event)
            await self._redis.xdel(_DLQ_NAME, message_id)
            logger.info("event_bus.dlq_retried", message_id=message_id)
            return True
        except Exception:
            logger.exception("event_bus.dlq_retry_failed")
            return False

    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register an event handler for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: StudyOSEvent) -> None:
        """Dispatch an event to all registered handlers."""
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            return

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.exception(
                    "event_bus.handler_failed",
                    event_type=event.event_type,
                    handler=handler.__name__,
                    error=str(e),
                )
                await self.move_to_dlq(event, str(e))

    async def get_pending_count(self, group_name: str) -> int:
        """Get the number of pending messages for a consumer group."""
        if self._redis is None:
            return 0
        try:
            info = await self._redis.xinfo_groups(_STREAM_NAME)
            for group in info:
                if group["name"] == group_name:
                    return group.get("pending", 0)
            return 0
        except Exception:
            return 0

    async def get_stream_length(self) -> int:
        """Get the current stream length."""
        if self._redis is None:
            return 0
        try:
            return await self._redis.xlen(_STREAM_NAME)
        except Exception:
            return 0

    async def _ensure_consumer_group(self, group_name: str) -> None:
        if group_name in self._consumer_groups:
            return
        try:
            await self._redis.xgroup_create(_STREAM_NAME, group_name, id="0", mkstream=True)
            self._consumer_groups[group_name] = group_name
            logger.info("event_bus.group_created", group=group_name)
        except Exception:
            logger.debug("event_bus.group_exists", group=group_name)
            self._consumer_groups[group_name] = group_name

    async def _is_duplicate(self, event: StudyOSEvent) -> bool:
        if event.idempotency_key is None:
            return False
        if self._redis is None:
            return False
        try:
            key = f"{_PROCESSED_KEY}:{event.idempotency_key}"
            added = await self._redis.set(key, "1", nx=True, ex=3600)
            return not added
        except Exception:
            return False


_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _bus
    if _bus is None:
        from studyos_api.services import cache

        redis = cache._client if hasattr(cache, "_client") and cache._client else None
        _bus = EventBus(redis=redis)
    return _bus


def reset_event_bus() -> None:
    """Reset the global event bus instance (for testing)."""
    global _bus
    _bus = None
