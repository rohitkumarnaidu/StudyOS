"""Tests for webhook delivery system."""

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.services.webhooks import (
    WebhookDeliveryService,
    WebhookEvent,
    compute_backoff,
    generate_signature,
    verify_signature,
)


class TestGenerateSignature:
    def test_generates_hmac_sha256(self) -> None:
        sig = generate_signature('{"event": "test"}', "secret123")
        assert len(sig) == 64  # SHA256 hex length
        assert sig == generate_signature('{"event": "test"}', "secret123")

    def test_different_payloads_different_signatures(self) -> None:
        sig1 = generate_signature('{"a": 1}', "secret")
        sig2 = generate_signature('{"a": 2}', "secret")
        assert sig1 != sig2

    def test_different_secrets_different_signatures(self) -> None:
        sig1 = generate_signature("payload", "secret1")
        sig2 = generate_signature("payload", "secret2")
        assert sig1 != sig2


class TestVerifySignature:
    def test_valid_signature(self) -> None:
        payload = '{"event": "test"}'
        secret = "mysecret"
        sig = generate_signature(payload, secret)
        assert verify_signature(payload, sig, secret) is True

    def test_invalid_signature(self) -> None:
        assert verify_signature("payload", "invalid_sig", "secret") is False

    def test_wrong_secret(self) -> None:
        payload = '{"event": "test"}'
        sig = generate_signature(payload, "correct")
        assert verify_signature(payload, sig, "wrong") is False


class TestComputeBackoff:
    def test_base_delay(self) -> None:
        delay = compute_backoff(0, base_seconds=1.0, max_seconds=300.0)
        assert 1.0 <= delay <= 1.1  # base + up to 10% jitter

    def test_exponential_growth(self) -> None:
        d1 = compute_backoff(0, base_seconds=1.0, max_seconds=300.0)
        d2 = compute_backoff(1, base_seconds=1.0, max_seconds=300.0)
        d3 = compute_backoff(2, base_seconds=1.0, max_seconds=300.0)
        assert d2 > d1
        assert d3 > d2

    def test_respects_max(self) -> None:
        delay = compute_backoff(20, base_seconds=1.0, max_seconds=300.0)
        assert delay <= 300.0 + 30.0  # max + 10% jitter

    def test_custom_base(self) -> None:
        delay = compute_backoff(0, base_seconds=5.0, max_seconds=300.0)
        assert 5.0 <= delay <= 5.5


class TestWebhookEvent:
    def test_to_json(self) -> None:
        event = WebhookEvent(
            event_type="user.created",
            payload={"user_id": "123"},
            timestamp=1700000000.0,
            delivery_id="abc-123",
        )
        import json
        data = json.loads(event.to_json())
        assert data["id"] == "abc-123"
        assert data["event"] == "user.created"
        assert data["timestamp"] == 1700000000.0
        assert data["data"] == {"user_id": "123"}

    def test_default_timestamp(self) -> None:
        event = WebhookEvent(event_type="test", payload={})
        assert event.timestamp > 0

    def test_default_values(self) -> None:
        event = WebhookEvent(event_type="test", payload={})
        assert event.attempts == 0
        assert event.max_attempts == 5
        assert event.next_retry_at == 0.0
        assert event.delivery_id == ""


class TestWebhookDeliveryService:
    @pytest.fixture
    def service(self) -> WebhookDeliveryService:
        return WebhookDeliveryService(secret="test-secret")

    def test_queue_event(self, service: WebhookDeliveryService) -> None:
        event = service.queue_event("user.created", {"user_id": "123"})
        assert event.event_type == "user.created"
        assert event.payload == {"user_id": "123"}
        assert event.delivery_id != ""
        assert service.get_stats()["pending"] == 1

    def test_queue_multiple_events(self, service: WebhookDeliveryService) -> None:
        service.queue_event("event1", {})
        service.queue_event("event2", {})
        assert service.get_stats()["pending"] == 2

    @pytest.mark.asyncio
    async def test_deliver_success(self, service: WebhookDeliveryService) -> None:
        event = service.queue_event("test.event", {"key": "val"})
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        result = await service.deliver(event, "https://example.com/webhook", mock_client)

        assert result is True
        assert service.get_stats()["delivered"] == 1
        assert service.get_stats()["pending"] == 0
        assert event.attempts == 1

    @pytest.mark.asyncio
    async def test_deliver_failure(self, service: WebhookDeliveryService) -> None:
        event = service.queue_event("test.event", {"key": "val"})
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        result = await service.deliver(event, "https://example.com/webhook", mock_client)

        assert result is False
        assert event.attempts == 1
        assert event.next_retry_at > 0

    @pytest.mark.asyncio
    async def test_deliver_network_error(self, service: WebhookDeliveryService) -> None:
        event = service.queue_event("test.event", {"key": "val"})
        mock_client = AsyncMock()
        mock_client.post.side_effect = ConnectionError("timeout")

        result = await service.deliver(event, "https://example.com/webhook", mock_client)

        assert result is False
        assert event.attempts == 1

    @pytest.mark.asyncio
    async def test_deliver_max_attempts_exhausted(self, service: WebhookDeliveryService) -> None:
        event = service.queue_event("test.event", {})
        event.attempts = 4  # One more attempt will exhaust
        event.max_attempts = 5
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        result = await service.deliver(event, "https://example.com/webhook", mock_client)

        assert result is False
        assert service.get_stats()["failed"] == 1
        assert service.get_stats()["pending"] == 0

    @pytest.mark.asyncio
    async def test_deliver_201_accepted(self, service: WebhookDeliveryService) -> None:
        event = service.queue_event("test.event", {})
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        result = await service.deliver(event, "https://example.com/webhook", mock_client)

        assert result is True

    @pytest.mark.asyncio
    async def test_process_pending(self, service: WebhookDeliveryService) -> None:
        event = service.queue_event("test.event", {})
        event.next_retry_at = 0  # Due now
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        delivered = await service.process_pending("https://example.com/webhook", mock_client)

        assert delivered == 1
        assert service.get_stats()["delivered"] == 1

    @pytest.mark.asyncio
    async def test_process_pending_not_due(self, service: WebhookDeliveryService) -> None:
        event = service.queue_event("test.event", {})
        event.next_retry_at = time.time() + 3600  # Not due
        mock_client = AsyncMock()

        delivered = await service.process_pending("https://example.com/webhook", mock_client)

        assert delivered == 0
        mock_client.post.assert_not_called()

    def test_get_stats(self, service: WebhookDeliveryService) -> None:
        service.queue_event("e1", {})
        service.queue_event("e2", {})
        stats = service.get_stats()
        assert stats == {"pending": 2, "delivered": 0, "failed": 0}

    def test_signature_headers(self, service: WebhookDeliveryService) -> None:
        """Verify that deliver sets correct signature headers."""
        event = service.queue_event("test.event", {"data": 1})
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        import asyncio
        asyncio.run(
            service.deliver(event, "https://example.com/webhook", mock_client)
        )

        call_kwargs = mock_client.post.call_args[1]
        headers = call_kwargs["headers"]
        assert "X-Webhook-Signature" in headers
        assert headers["X-Webhook-Signature"].startswith("sha256=")
        assert headers["X-Webhook-Event"] == "test.event"
        assert headers["X-Webhook-Delivery-Id"] == event.delivery_id
