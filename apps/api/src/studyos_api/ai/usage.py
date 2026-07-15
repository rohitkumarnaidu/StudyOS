"""Token usage recording — in-process ring buffer + structlog (swap for warehouse)."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass

import structlog

from studyos_api.ai.protocols import UsageSink
from studyos_api.ai.types import TokenUsage

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class UsageEvent:
    provider_id: str
    model: str
    usage: TokenUsage
    request_id: str | None
    user_sub: str | None


class InMemoryUsageStore(UsageSink):
    """Bounded in-memory store for dashboards / tests; not durable across restarts."""

    def __init__(self, *, max_events: int = 5000) -> None:
        self._events: deque[UsageEvent] = deque(maxlen=max_events)
        self._lock = asyncio.Lock()

    async def record(
        self,
        *,
        provider_id: str,
        model: str,
        usage: TokenUsage,
        request_id: str | None,
        user_sub: str | None,
    ) -> None:
        ev = UsageEvent(
            provider_id=provider_id,
            model=model,
            usage=usage,
            request_id=request_id,
            user_sub=user_sub,
        )
        async with self._lock:
            self._events.append(ev)
        logger.info(
            "ai.usage",
            provider=provider_id,
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            request_id=request_id,
            user_sub=user_sub,
        )

    async def recent(self, *, limit: int = 50) -> list[UsageEvent]:
        async with self._lock:
            return list(self._events)[-limit:]


class LoggingUsageSink(UsageSink):
    """Structured logs only (no retention)."""

    async def record(
        self,
        *,
        provider_id: str,
        model: str,
        usage: TokenUsage,
        request_id: str | None,
        user_sub: str | None,
    ) -> None:
        logger.info(
            "ai.usage",
            provider=provider_id,
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            request_id=request_id,
            user_sub=user_sub,
        )


class CompositeUsageSink(UsageSink):
    def __init__(self, *sinks: UsageSink) -> None:
        self._sinks = sinks

    async def record(
        self,
        *,
        provider_id: str,
        model: str,
        usage: TokenUsage,
        request_id: str | None,
        user_sub: str | None,
    ) -> None:
        for s in self._sinks:
            await s.record(
                provider_id=provider_id,
                model=model,
                usage=usage,
                request_id=request_id,
                user_sub=user_sub,
            )
