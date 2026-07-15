"""Retry with exponential backoff + orchestrated fallback across providers."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence

import structlog

from studyos_api.ai.protocols import LLMProvider
from studyos_api.ai.types import CompletionRequest, CompletionResult, StreamChunk
from studyos_api.core.config import Settings

logger = structlog.get_logger(__name__)


async def retry_async[T](
    fn: Callable[[], Awaitable[T]],
    *,
    max_attempts: int,
    base_delay: float,
    label: str,
) -> T:
    last: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return await fn()
        except Exception as exc:
            last = exc
            if attempt == max_attempts - 1:
                break
            delay = base_delay * (2**attempt)
            logger.warning(
                "ai.retry",
                label=label,
                attempt=attempt + 1,
                max_attempts=max_attempts,
                delay_s=delay,
                error=str(exc),
            )
            await asyncio.sleep(delay)
    assert last is not None
    raise last


class FallbackOrchestrator:
    """Try primary provider with retries, then each fallback in order."""

    def __init__(
        self,
        *,
        settings: Settings,
        ordered_providers: Sequence[LLMProvider],
    ) -> None:
        if not ordered_providers:
            msg = "At least one LLM provider is required"
            raise ValueError(msg)
        self._settings = settings
        self._ordered = list(ordered_providers)

    async def complete(self, req: CompletionRequest) -> CompletionResult:
        errors: list[str] = []
        for prov in self._ordered:
            label = f"{prov.provider_id}:{req.model or 'default'}"
            bound = prov

            async def _once(p: LLMProvider = bound) -> CompletionResult:
                return await p.complete(req)

            try:
                return await retry_async(
                    _once,
                    max_attempts=self._settings.ai_max_retries + 1,
                    base_delay=self._settings.ai_retry_base_seconds,
                    label=label,
                )
            except Exception as exc:
                errors.append(f"{prov.provider_id}:{exc!s}")
                logger.warning("ai.provider_failed", provider=prov.provider_id, error=str(exc))
        msg = "; ".join(errors) or "all providers failed"
        raise RuntimeError(msg)

    async def complete_stream(self, req: CompletionRequest) -> AsyncIterator[StreamChunk]:
        for prov in self._ordered:
            if not prov.supports_streaming():
                continue
            try:
                async for chunk in prov.complete_stream(req):
                    yield StreamChunk(
                        delta=chunk.delta,
                        done=chunk.done,
                        usage=chunk.usage,
                        provider_id=chunk.provider_id or prov.provider_id,
                        model=chunk.model or req.model,
                    )
                return
            except Exception as exc:
                logger.warning("ai.stream_failed", provider=prov.provider_id, error=str(exc))
        text = await self.complete(req)
        yield StreamChunk(
            delta=text.text,
            done=True,
            usage=text.usage,
            provider_id=text.provider_id,
            model=text.model,
        )
