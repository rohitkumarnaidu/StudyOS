"""Tests for Redis Streams event bus."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from studyos_api.services.event_bus import EventBus, get_event_bus, reset_event_bus
from studyos_api.services.event_types import (
    EventCategory,
    EventPriority,
    StudyOSEvent,
)


@pytest.fixture(autouse=True)
def reset_bus():
    reset_event_bus()
    yield
    reset_event_bus()


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.xadd = AsyncMock(return_value="1234567890-0")
    redis.xreadgroup = AsyncMock(return_value=[])
    redis.xack = AsyncMock()
    redis.xgroup_create = AsyncMock()
    redis.xinfo_groups = AsyncMock(return_value=[])
    redis.xlen = AsyncMock(return_value=0)
    redis.set = AsyncMock(return_value=True)
    redis.xrange = AsyncMock(return_value=[])
    redis.xdel = AsyncMock(return_value=1)
    return redis


@pytest.fixture
def event_bus(mock_redis):
    return EventBus(redis=mock_redis)


def make_event(event_type="study.completed", **kwargs):
    return StudyOSEvent(
        event_type=event_type,
        category=kwargs.get("category", EventCategory.STUDY),
        profile_id=kwargs.get("profile_id", uuid4()),
        payload=kwargs.get("payload", {}),
        priority=kwargs.get("priority", EventPriority.NORMAL),
        idempotency_key=kwargs.get("idempotency_key"),
    )


class TestEventBusPublish:
    @pytest.mark.asyncio
    async def test_publish_event(self, event_bus, mock_redis):
        event = make_event()
        msg_id = await event_bus.publish(event)
        assert msg_id is not None
        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args
        assert call_args[0][0] == "studyos:events"

    @pytest.mark.asyncio
    async def test_publish_without_redis(self):
        bus = EventBus(redis=None)
        event = make_event()
        result = await bus.publish(event)
        assert result is None

    @pytest.mark.asyncio
    async def test_publish_duplicate(self, event_bus, mock_redis):
        mock_redis.set = AsyncMock(return_value=False)
        event = make_event(idempotency_key="dup-key")
        result = await event_bus.publish(event)
        assert result is None
        mock_redis.xadd.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_without_idempotency_key(self, event_bus, mock_redis):
        event = make_event()
        result = await event_bus.publish(event)
        assert result is not None
        mock_redis.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_failed(self, event_bus, mock_redis):
        mock_redis.xadd = AsyncMock(side_effect=Exception("Redis error"))
        event = make_event()
        result = await event_bus.publish(event)
        assert result is None


class TestEventBusConsume:
    @pytest.mark.asyncio
    async def test_consume_no_redis(self):
        bus = EventBus(redis=None)
        result = await bus.consume("group", "consumer")
        assert result == []

    @pytest.mark.asyncio
    async def test_consume_creates_group(self, event_bus, mock_redis):
        mock_redis.xreadgroup = AsyncMock(return_value=[])
        await event_bus.consume("test-group", "consumer-1")
        mock_redis.xgroup_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_returns_messages(self, event_bus, mock_redis):
        mock_redis.xreadgroup = AsyncMock(
            return_value=[
                (
                    b"studyos:events",
                    [
                        (
                            b"1234567890-0",
                            {
                                b"event_type": b"study.completed",
                                b"category": b"study",
                                b"profile_id": str(uuid4()),
                                b"payload": b"{}",
                                b"priority": b"normal",
                            },
                        )
                    ],
                )
            ]
        )
        await event_bus.consume("test-group", "consumer-1")
        mock_redis.xreadgroup.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_empty_result(self, event_bus, mock_redis):
        mock_redis.xreadgroup = AsyncMock(return_value=[])
        result = await event_bus.consume("test-group", "consumer-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_consume_handles_existing_group(self, event_bus, mock_redis):
        mock_redis.xgroup_create = AsyncMock(side_effect=Exception("BUSYGROUP"))
        mock_redis.xreadgroup = AsyncMock(return_value=[])
        result = await event_bus.consume("existing-group", "consumer-1")
        assert result == []

    @pytest.mark.asyncio
    async def test_consume_with_custom_batch_size(self, event_bus, mock_redis):
        mock_redis.xreadgroup = AsyncMock(return_value=[])
        await event_bus.consume("group", "consumer", batch_size=25)
        call_args = mock_redis.xreadgroup.call_args
        assert call_args[1]["count"] == 25

    @pytest.mark.asyncio
    async def test_consume_with_custom_timeout(self, event_bus, mock_redis):
        mock_redis.xreadgroup = AsyncMock(return_value=[])
        await event_bus.consume("group", "consumer", timeout_ms=10000)
        call_args = mock_redis.xreadgroup.call_args
        assert call_args[1]["block"] == 10000


class TestEventBusAcknowledge:
    @pytest.mark.asyncio
    async def test_acknowledge(self, event_bus, mock_redis):
        await event_bus.acknowledge("group", "1234567890-0")
        mock_redis.xack.assert_called_once_with(
            "studyos:events", "group", "1234567890-0"
        )

    @pytest.mark.asyncio
    async def test_acknowledge_no_redis(self):
        bus = EventBus(redis=None)
        await bus.acknowledge("group", "1234567890-0")


class TestEventBusDLQ:
    @pytest.mark.asyncio
    async def test_move_to_dlq(self, event_bus, mock_redis):
        event = make_event()
        await event_bus.move_to_dlq(event, "handler failed")
        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args
        assert call_args[0][0] == "studyos:events:dead_letter"
        assert "dlq_error" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_move_to_dlq_no_redis(self):
        bus = EventBus(redis=None)
        event = make_event()
        await bus.move_to_dlq(event, "error")

    @pytest.mark.asyncio
    async def test_get_dlq_count(self, event_bus, mock_redis):
        mock_redis.xlen = AsyncMock(return_value=5)
        count = await event_bus.get_dlq_count()
        assert count == 5

    @pytest.mark.asyncio
    async def test_get_dlq_count_no_redis(self):
        bus = EventBus(redis=None)
        count = await bus.get_dlq_count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_retry_dlq_message(self, event_bus, mock_redis):
        profile_id = uuid4()
        event_id = uuid4()
        mock_redis.xrange = AsyncMock(
            return_value=[
                (
                    b"1234567890-0",
                    {
                        b"event_id": str(event_id),
                        b"event_type": b"study.completed",
                        b"category": b"study",
                        b"profile_id": str(profile_id),
                        b"payload": b"{}",
                        b"priority": b"normal",
                    },
                )
            ]
        )
        mock_redis.xdel = AsyncMock(return_value=1)
        result = await event_bus.retry_dlq_message("1234567890-0")
        assert result is True
        mock_redis.xdel.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_dlq_message_not_found(self, event_bus, mock_redis):
        mock_redis.xrange = AsyncMock(return_value=[])
        result = await event_bus.retry_dlq_message("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_retry_dlq_message_no_redis(self):
        bus = EventBus(redis=None)
        result = await bus.retry_dlq_message("1234567890-0")
        assert result is False


class TestEventBusDispatch:
    @pytest.mark.asyncio
    async def test_dispatch_to_handler(self, event_bus):
        handler_called = False

        async def handler(event):
            nonlocal handler_called
            handler_called = True

        event_bus.register_handler("study.completed", handler)
        event = make_event("study.completed")
        await event_bus.dispatch(event)
        assert handler_called

    @pytest.mark.asyncio
    async def test_dispatch_no_handlers(self, event_bus):
        event = make_event("study.completed")
        await event_bus.dispatch(event)

    @pytest.mark.asyncio
    async def test_dispatch_handler_failure(self, event_bus, mock_redis):
        async def failing_handler(event):
            raise ValueError("Handler error")

        event_bus.register_handler("study.completed", failing_handler)
        event = make_event("study.completed")
        await event_bus.dispatch(event)
        mock_redis.xadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_multiple_handlers(self, event_bus):
        call_count = 0

        async def handler1(event):
            nonlocal call_count
            call_count += 1

        async def handler2(event):
            nonlocal call_count
            call_count += 1

        event_bus.register_handler("quiz.finished", handler1)
        event_bus.register_handler("quiz.finished", handler2)
        event = make_event("quiz.finished", category=EventCategory.QUIZ)
        await event_bus.dispatch(event)
        assert call_count == 2


class TestEventBusStats:
    @pytest.mark.asyncio
    async def test_get_pending_count(self, event_bus, mock_redis):
        mock_redis.xinfo_groups = AsyncMock(
            return_value=[{"name": "test-group", "pending": 15}]
        )
        count = await event_bus.get_pending_count("test-group")
        assert count == 15

    @pytest.mark.asyncio
    async def test_get_pending_count_no_group(self, event_bus, mock_redis):
        mock_redis.xinfo_groups = AsyncMock(
            return_value=[{"name": "other-group", "pending": 5}]
        )
        count = await event_bus.get_pending_count("test-group")
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_pending_count_no_redis(self):
        bus = EventBus(redis=None)
        count = await bus.get_pending_count("group")
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_stream_length(self, event_bus, mock_redis):
        mock_redis.xlen = AsyncMock(return_value=1500)
        length = await event_bus.get_stream_length()
        assert length == 1500

    @pytest.mark.asyncio
    async def test_get_stream_length_no_redis(self):
        bus = EventBus(redis=None)
        length = await bus.get_stream_length()
        assert length == 0


class TestEventBusIdempotency:
    @pytest.mark.asyncio
    async def test_is_duplicate_new_key(self, event_bus, mock_redis):
        mock_redis.set = AsyncMock(return_value=True)
        event = make_event(idempotency_key="new-key")
        result = await event_bus._is_duplicate(event)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_duplicate_existing_key(self, event_bus, mock_redis):
        mock_redis.set = AsyncMock(return_value=False)
        event = make_event(idempotency_key="existing-key")
        result = await event_bus._is_duplicate(event)
        assert result is True

    @pytest.mark.asyncio
    async def test_is_duplicate_no_key(self, event_bus, mock_redis):
        event = make_event()
        result = await event_bus._is_duplicate(event)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_duplicate_no_redis(self):
        bus = EventBus(redis=None)
        event = make_event(idempotency_key="some-key")
        result = await bus._is_duplicate(event)
        assert result is False


class TestGetEventBus:
    def test_get_event_bus_creates_instance(self):
        reset_event_bus()
        bus = get_event_bus()
        assert isinstance(bus, EventBus)

    def test_get_event_bus_returns_same_instance(self):
        reset_event_bus()
        bus1 = get_event_bus()
        bus2 = get_event_bus()
        assert bus1 is bus2
