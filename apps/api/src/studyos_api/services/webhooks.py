"""Webhook delivery system — signature verification, retry logic, event schema."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class WebhookEvent:
    """Represents a webhook event to be delivered."""

    event_type: str
    payload: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    delivery_id: str = ""
    attempts: int = 0
    max_attempts: int = 5
    next_retry_at: float = 0.0

    def to_json(self) -> str:
        return json.dumps(
            {
                "id": self.delivery_id,
                "event": self.event_type,
                "timestamp": self.timestamp,
                "data": self.payload,
            }
        )


def generate_signature(payload: str, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook payload."""
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook payload signature using constant-time comparison."""
    expected = generate_signature(payload, secret)
    return hmac.compare_digest(expected, signature)


def compute_backoff(attempt: int, base_seconds: float = 1.0, max_seconds: float = 300.0) -> float:
    """Exponential backoff with jitter for webhook retries."""
    import random

    delay = min(base_seconds * (2**attempt), max_seconds)
    jitter = random.uniform(0, delay * 0.1)  # noqa: S311 (jitter doesn't need crypto security)
    return delay + jitter


class WebhookDeliveryService:
    """Manages webhook event delivery with retries and signature verification."""

    def __init__(self, secret: str) -> None:
        self._secret = secret
        self._pending: list[WebhookEvent] = []
        self._delivered: list[WebhookEvent] = []
        self._failed: list[WebhookEvent] = []

    def queue_event(self, event_type: str, payload: dict[str, Any]) -> WebhookEvent:
        """Queue a new webhook event for delivery."""
        import uuid

        event = WebhookEvent(
            event_type=event_type,
            payload=payload,
            delivery_id=str(uuid.uuid4()),
        )
        self._pending.append(event)
        logger.info("webhook.queued", event_type=event_type, delivery_id=event.delivery_id)
        return event

    async def deliver(self, event: WebhookEvent, endpoint_url: str, http_client: Any) -> bool:
        """Attempt to deliver a webhook event to the given endpoint."""
        event.attempts += 1
        payload = event.to_json()
        signature = generate_signature(payload, self._secret)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": f"sha256={signature}",
            "X-Webhook-Event": event.event_type,
            "X-Webhook-Delivery-Id": event.delivery_id,
            "X-Webhook-Timestamp": str(int(event.timestamp)),
        }

        try:
            response = await http_client.post(
                endpoint_url,
                content=payload,
                headers=headers,
                timeout=10.0,
            )

            if 200 <= response.status_code < 300:
                self._pending.remove(event)
                self._delivered.append(event)
                logger.info(
                    "webhook.delivered",
                    delivery_id=event.delivery_id,
                    attempts=event.attempts,
                    status_code=response.status_code,
                )
                return True

            logger.warning(
                "webhook.failed",
                delivery_id=event.delivery_id,
                attempts=event.attempts,
                status_code=response.status_code,
            )

        except Exception as e:
            logger.error(
                "webhook.error",
                delivery_id=event.delivery_id,
                attempts=event.attempts,
                error=str(e),
            )

        if event.attempts >= event.max_attempts:
            self._pending.remove(event)
            self._failed.append(event)
            logger.error(
                "webhook.exhausted",
                delivery_id=event.delivery_id,
                total_attempts=event.attempts,
            )
            return False

        event.next_retry_at = time.time() + compute_backoff(event.attempts)
        return False

    async def process_pending(self, endpoint_url: str, http_client: Any) -> int:
        """Process all pending webhook events that are due for retry."""
        now = time.time()
        due_events = [e for e in self._pending if e.next_retry_at <= now]
        delivered_count = 0

        for event in due_events:
            success = await self.deliver(event, endpoint_url, http_client)
            if success:
                delivered_count += 1

        return delivered_count

    def get_stats(self) -> dict[str, int]:
        """Return delivery statistics."""
        return {
            "pending": len(self._pending),
            "delivered": len(self._delivered),
            "failed": len(self._failed),
        }
