"""Tests for event consumer services."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from studyos_api.services.event_bus import EventBus
from studyos_api.services.event_consumer import EventConsumer, RetryableEventConsumer
from studyos_api.services.event_types import (
    EventCategory,
    EventPriority,
    StudyOSEvent,
)


@pytest.fixture
def mock_event_bus():
    bus = AsyncMock(spec=EventBus)
    bus.consume = AsyncMock(return_value=[])
    bus.acknowledge = AsyncMock()
    bus.dispatch = AsyncMock()
    bus.move_to_dlq = AsyncMock()
    bus.register_handler = MagicMock()
    return bus


def make_event(event_type="study.completed", **kwargs):
    return StudyOSEvent(
        event_type=event_type,
        category=kwargs.get("category", EventCategory.STUDY),
        profile_id=kwargs.get("profile_id", uuid4()),
        payload=kwargs.get("payload", {}),
        priority=kwargs.get("priority", EventPriority.NORMAL),
        idempotency_key=kwargs.get("idempotency_key"),
    )


class TestEventConsumer:
    def test_init(self, mock_event_bus):
        consumer = EventConsumer(event_bus=mock_event_bus)
        assert consumer._running is False
        assert consumer._handlers == {}
        assert consumer._processed_count == 0
        assert consumer._error_count == 0

    def test_register_handler(self, mock_event_bus):
        consumer = EventConsumer(event_bus=mock_event_bus)

        async def handler(event):
            pass

        consumer.register("study.completed", handler)
        assert "study.completed" in consumer._handlers
        mock_event_bus.register_handler.assert_called_once_with(
            "study.completed", handler
        )

    @pytest.mark.asyncio
    async def test_start_empty_stream(self, mock_event_bus):
        consumer = EventConsumer(event_bus=mock_event_bus)
        mock_event_bus.consume = AsyncMock(return_value=[])

        async def stop_after_delay():
            import asyncio
            await asyncio.sleep(0.1)
            await consumer.stop()

        import asyncio
        await asyncio.gather(consumer.start(), stop_after_delay())
        assert consumer._running is False

    @pytest.mark.asyncio
    async def test_process_message_success(self, mock_event_bus):
        consumer = EventConsumer(event_bus=mock_event_bus)
        profile_id = uuid4()
        fields = {
            "event_id": str(uuid4()),
            "event_type": "study.completed",
            "category": "study",
            "profile_id": str(profile_id),
            "payload": "{}",
            "priority": "normal",
        }

        await consumer._process_message("1234567890-0", fields)
        mock_event_bus.dispatch.assert_called_once()
        mock_event_bus.acknowledge.assert_called_once_with("default", "1234567890-0")
        assert consumer._processed_count == 1

    @pytest.mark.asyncio
    async def test_process_message_failure_moves_to_dlq(self, mock_event_bus):
        consumer = EventConsumer(event_bus=mock_event_bus)
        mock_event_bus.dispatch = AsyncMock(side_effect=Exception("Handler failed"))
        profile_id = uuid4()
        fields = {
            "event_id": str(uuid4()),
            "event_type": "study.completed",
            "category": "study",
            "profile_id": str(profile_id),
            "payload": "{}",
            "priority": "normal",
        }

        await consumer._process_message("1234567890-0", fields)
        mock_event_bus.move_to_dlq.assert_called_once()
        mock_event_bus.acknowledge.assert_called_once_with("default", "1234567890-0")
        assert consumer._error_count == 1

    @pytest.mark.asyncio
    async def test_stats(self, mock_event_bus):
        consumer = EventConsumer(event_bus=mock_event_bus)
        consumer._processed_count = 10
        consumer._error_count = 2
        assert consumer.stats == {"processed": 10, "errors": 2}

    @pytest.mark.asyncio
    async def test_stop(self, mock_event_bus):
        consumer = EventConsumer(event_bus=mock_event_bus)
        consumer._running = True
        await consumer.stop()
        assert consumer._running is False

    @pytest.mark.asyncio
    async def test_custom_group_and_consumer_name(self, mock_event_bus):
        consumer = EventConsumer(
            event_bus=mock_event_bus,
            group_name="analytics",
            consumer_name="worker-2",
        )
        assert consumer._group_name == "analytics"
        assert consumer._consumer_name == "worker-2"


class TestRetryableEventConsumer:
    def test_init(self, mock_event_bus):
        consumer = RetryableEventConsumer(event_bus=mock_event_bus)
        assert consumer._max_retries == 3
        assert consumer._retry_counts == {}

    def test_init_custom_max_retries(self, mock_event_bus):
        consumer = RetryableEventConsumer(
            event_bus=mock_event_bus, max_retries=5
        )
        assert consumer._max_retries == 5

    @pytest.mark.asyncio
    async def test_process_message_success_resets_retry_count(self, mock_event_bus):
        consumer = RetryableEventConsumer(event_bus=mock_event_bus)
        profile_id = uuid4()
        event_id = uuid4()
        fields = {
            "event_id": str(event_id),
            "event_type": "study.completed",
            "category": "study",
            "profile_id": str(profile_id),
            "payload": "{}",
            "priority": "normal",
        }

        await consumer._process_message("1234567890-0", fields)
        mock_event_bus.dispatch.assert_called_once()
        mock_event_bus.acknowledge.assert_called_once()
        assert consumer._processed_count == 1
        assert str(event_id) not in consumer._retry_counts

    @pytest.mark.asyncio
    async def test_process_message_failure_retries(self, mock_event_bus):
        consumer = RetryableEventConsumer(
            event_bus=mock_event_bus, max_retries=2
        )
        call_count = 0

        async def fail_twice_then_succeed(event):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Handler failed")

        mock_event_bus.dispatch = AsyncMock(side_effect=fail_twice_then_succeed)
        profile_id = uuid4()
        event_id = uuid4()
        fields = {
            "event_id": str(event_id),
            "event_type": "study.completed",
            "category": "study",
            "profile_id": str(profile_id),
            "payload": "{}",
            "priority": "normal",
        }

        with patch("studyos_api.services.event_consumer.asyncio.sleep", new_callable=AsyncMock):
            await consumer._process_message("1234567890-0", fields)

        assert call_count == 2
        assert consumer._processed_count == 1
        assert str(event_id) not in consumer._retry_counts

    @pytest.mark.asyncio
    async def test_process_message_exceeds_max_retries_moves_to_dlq(self, mock_event_bus):
        consumer = RetryableEventConsumer(
            event_bus=mock_event_bus, max_retries=1
        )
        mock_event_bus.dispatch = AsyncMock(side_effect=Exception("Handler failed"))
        profile_id = uuid4()
        event_id = uuid4()
        fields = {
            "event_id": str(event_id),
            "event_type": "study.completed",
            "category": "study",
            "profile_id": str(profile_id),
            "payload": "{}",
            "priority": "normal",
        }

        consumer._retry_counts[str(event_id)] = 1
        await consumer._process_message("1234567890-0", fields)
        mock_event_bus.move_to_dlq.assert_called_once()
        mock_event_bus.acknowledge.assert_called_once()
        assert str(event_id) not in consumer._retry_counts

    @pytest.mark.asyncio
    async def test_retry_delay_exponential(self, mock_event_bus):
        consumer = RetryableEventConsumer(
            event_bus=mock_event_bus, max_retries=3
        )
        profile_id = uuid4()
        event_id = uuid4()
        fields = {
            "event_id": str(event_id),
            "event_type": "study.completed",
            "category": "study",
            "profile_id": str(profile_id),
            "payload": "{}",
            "priority": "normal",
        }

        call_count = 0

        async def fail_once_then_succeed(event):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("fail")

        mock_event_bus.dispatch = AsyncMock(side_effect=fail_once_then_succeed)

        with patch("studyos_api.services.event_consumer.asyncio.sleep", new_callable=AsyncMock):
            await consumer._process_message("1234567890-0", fields)

        assert call_count == 2
        assert consumer._processed_count == 1
        assert str(event_id) not in consumer._retry_counts

    @pytest.mark.asyncio
    async def test_successful_retry_clears_count(self, mock_event_bus):
        consumer = RetryableEventConsumer(
            event_bus=mock_event_bus, max_retries=3
        )
        profile_id = uuid4()
        event_id = uuid4()
        fields = {
            "event_id": str(event_id),
            "event_type": "study.completed",
            "category": "study",
            "profile_id": str(profile_id),
            "payload": "{}",
            "priority": "normal",
        }

        await consumer._process_message("1234567890-0", fields)
        assert consumer._processed_count == 1
        assert str(event_id) not in consumer._retry_counts
