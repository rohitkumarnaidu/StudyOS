"""Event consumer service — background event processing with retry logic."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any
from collections.abc import Callable, Coroutine

import structlog

from studyos_api.services.event_bus import EventBus, get_event_bus
from studyos_api.services.event_types import StudyOSEvent

if TYPE_CHECKING:
    pass

logger = structlog.get_logger(__name__)

_MAX_RETRIES = 3
_RETRY_DELAY_SECONDS = 5
_POLL_INTERVAL_SECONDS = 1


class EventConsumer:
    """Background event consumer that processes events from the stream."""

    def __init__(
        self,
        event_bus: EventBus | None = None,
        group_name: str = "default",
        consumer_name: str = "worker-1",
    ) -> None:
        self._bus = event_bus or get_event_bus()
        self._group_name = group_name
        self._consumer_name = consumer_name
        self._running = False
        self._handlers: dict[str, Callable[[StudyOSEvent], Coroutine[Any, Any, None]]] = {}
        self._processed_count = 0
        self._error_count = 0

    def register(self, event_type: str, handler: Callable[[StudyOSEvent], Coroutine[Any, Any, None]]) -> None:
        """Register a handler for an event type."""
        self._handlers[event_type] = handler
        self._bus.register_handler(event_type, handler)

    async def start(self, batch_size: int = 10) -> None:
        """Start consuming events from the stream."""
        self._running = True
        logger.info(
            "event_consumer.started",
            group=self._group_name,
            consumer=self._consumer_name,
        )

        while self._running:
            try:
                messages = await self._bus.consume(
                    self._group_name,
                    self._consumer_name,
                    batch_size=batch_size,
                )

                if not messages:
                    await asyncio.sleep(_POLL_INTERVAL_SECONDS)
                    continue

                for msg_id, fields in messages:
                    await self._process_message(msg_id, fields)

            except Exception:
                logger.exception("event_consumer.loop_error")
                await asyncio.sleep(_POLL_INTERVAL_SECONDS * 2)

    async def stop(self) -> None:
        """Stop the consumer."""
        self._running = False
        logger.info("event_consumer.stopped", processed=self._processed_count, errors=self._error_count)

    async def _process_message(self, msg_id: str, fields: dict[str, str]) -> None:
        try:
            event = StudyOSEvent.from_dict(fields)
            await self._bus.dispatch(event)
            await self._bus.acknowledge(self._group_name, msg_id)
            self._processed_count += 1
        except Exception as e:
            self._error_count += 1
            logger.exception("event_consumer.process_failed", msg_id=msg_id)
            try:
                event = StudyOSEvent.from_dict(fields)
                await self._bus.move_to_dlq(event, str(e))
                await self._bus.acknowledge(self._group_name, msg_id)
            except Exception:
                logger.exception("event_consumer.dlq_move_failed")

    @property
    def stats(self) -> dict[str, int]:
        return {
            "processed": self._processed_count,
            "errors": self._error_count,
        }


class RetryableEventConsumer(EventConsumer):
    """Event consumer with automatic retry logic for failed handlers."""

    def __init__(
        self,
        event_bus: EventBus | None = None,
        group_name: str = "default",
        consumer_name: str = "worker-1",
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        super().__init__(event_bus, group_name, consumer_name)
        self._max_retries = max_retries
        self._retry_counts: dict[str, int] = {}

    async def _process_message(self, msg_id: str, fields: dict[str, str]) -> None:
        event = StudyOSEvent.from_dict(fields)
        retry_key = str(event.event_id)
        current_retries = self._retry_counts.get(retry_key, 0)

        if current_retries >= self._max_retries:
            await self._bus.move_to_dlq(event, f"max_retries_exceeded:{self._max_retries}")
            await self._bus.acknowledge(self._group_name, msg_id)
            self._retry_counts.pop(retry_key, None)
            return

        try:
            await self._bus.dispatch(event)
            await self._bus.acknowledge(self._group_name, msg_id)
            self._processed_count += 1
            self._retry_counts.pop(retry_key, None)
        except Exception:
            self._retry_counts[retry_key] = current_retries + 1
            self._error_count += 1
            delay = _RETRY_DELAY_SECONDS * (2 ** current_retries)
            logger.warning(
                "event_consumer.retry_scheduled",
                event_type=event.event_type,
                retry=current_retries + 1,
                max=self._max_retries,
                delay=delay,
            )
            await asyncio.sleep(delay)
            await self._process_message(msg_id, fields)
