"""Tests for AI retry logic and fallback orchestrator."""

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest

from studyos_api.ai.retry import FallbackOrchestrator, retry_async
from studyos_api.ai.types import (
    ChatMessage,
    CompletionRequest,
    CompletionResult,
    StreamChunk,
    TokenUsage,
)
from studyos_api.core.config import Settings, get_settings


class MockProvider:
    """Test double for LLMProvider protocol."""

    def __init__(
        self,
        provider_id: str = "mock",
        complete_result: CompletionResult | None = None,
        complete_error: Exception | None = None,
        stream_chunks: list[StreamChunk] | None = None,
        stream_error: Exception | None = None,
        supports_streaming: bool = True,
    ) -> None:
        self.provider_id = provider_id
        self._result = complete_result
        self._error = complete_error
        self._stream_chunks = stream_chunks or []
        self._stream_error = stream_error
        self._supports_streaming = supports_streaming
        self.call_count = 0

    async def complete(self, req: CompletionRequest) -> CompletionResult:
        self.call_count += 1
        if self._error:
            raise self._error
        if self._result:
            return self._result
        return CompletionResult(
            text="mock response",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            provider_id=self.provider_id,
            model=req.model or "mock-model",
        )

    def supports_streaming(self) -> bool:
        return self._supports_streaming

    async def complete_stream(self, req: CompletionRequest) -> AsyncIterator[StreamChunk]:
        if self._stream_error:
            raise self._stream_error
        for chunk in self._stream_chunks:
            yield chunk


@pytest.fixture()
def settings() -> Settings:
    s = get_settings()
    s.ai_max_retries = 2
    s.ai_retry_base_seconds = 0.01
    return s


class TestRetryAsync:
    @pytest.mark.asyncio
    async def test_succeeds_on_first_attempt(self) -> None:
        fn = AsyncMock(return_value="ok")
        result = await retry_async(fn, max_attempts=3, base_delay=0.01, label="test")
        assert result == "ok"
        fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_retries_on_failure_then_succeeds(self) -> None:
        fn = AsyncMock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])
        result = await retry_async(fn, max_attempts=3, base_delay=0.01, label="test")
        assert result == "success"
        assert fn.call_count == 3

    @pytest.mark.asyncio
    async def test_raises_after_max_attempts(self) -> None:
        fn = AsyncMock(side_effect=RuntimeError("always fails"))
        with pytest.raises(RuntimeError, match="always fails"):
            await retry_async(fn, max_attempts=2, base_delay=0.01, label="test")
        assert fn.call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_single_attempt(self) -> None:
        fn = AsyncMock(side_effect=ValueError("fail"))
        with pytest.raises(ValueError):
            await retry_async(fn, max_attempts=1, base_delay=0.01, label="test")
        assert fn.call_count == 1


class TestFallbackOrchestrator:
    @pytest.mark.asyncio
    async def test_primary_succeeds(self, settings: Settings) -> None:
        primary = MockProvider(provider_id="primary")
        orch = FallbackOrchestrator(settings=settings, ordered_providers=[primary])

        req = CompletionRequest(messages=[ChatMessage(role="user", content="hello")])
        result = await orch.complete(req)

        assert result.text == "mock response"
        assert result.provider_id == "primary"
        assert primary.call_count == 1

    @pytest.mark.asyncio
    async def test_fallback_on_primary_failure(self, settings: Settings) -> None:
        primary = MockProvider(
            provider_id="primary",
            complete_error=ConnectionError("timeout"),
        )
        fallback = MockProvider(provider_id="fallback")
        orch = FallbackOrchestrator(settings=settings, ordered_providers=[primary, fallback])

        req = CompletionRequest(messages=[ChatMessage(role="user", content="hello")])
        result = await orch.complete(req)

        assert result.text == "mock response"
        assert result.provider_id == "fallback"
        assert primary.call_count > 0
        assert fallback.call_count == 1

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises(self, settings: Settings) -> None:
        primary = MockProvider(
            provider_id="primary",
            complete_error=ConnectionError("timeout"),
        )
        fallback = MockProvider(
            provider_id="fallback",
            complete_error=RuntimeError("error"),
        )
        orch = FallbackOrchestrator(settings=settings, ordered_providers=[primary, fallback])

        req = CompletionRequest(messages=[ChatMessage(role="user", content="hello")])
        with pytest.raises(RuntimeError, match="primary:timeout.*fallback:error"):
            await orch.complete(req)

    @pytest.mark.asyncio
    async def test_requires_at_least_one_provider(self, settings: Settings) -> None:
        with pytest.raises(ValueError, match="At least one LLM provider"):
            FallbackOrchestrator(settings=settings, ordered_providers=[])

    @pytest.mark.asyncio
    async def test_streaming_primary_succeeds(self, settings: Settings) -> None:
        chunks = [
            StreamChunk(delta="Hello", done=False),
            StreamChunk(delta=" world", done=True),
        ]
        primary = MockProvider(provider_id="primary", stream_chunks=chunks)
        orch = FallbackOrchestrator(settings=settings, ordered_providers=[primary])

        req = CompletionRequest(messages=[ChatMessage(role="user", content="hi")], stream=True)
        collected: list[StreamChunk] = []
        async for chunk in orch.complete_stream(req):
            collected.append(chunk)

        assert len(collected) == 2
        assert collected[0].delta == "Hello"
        assert collected[1].delta == " world"
        assert collected[1].done is True

    @pytest.mark.asyncio
    async def test_streaming_fallback_on_failure(self, settings: Settings) -> None:
        primary = MockProvider(
            provider_id="primary",
            stream_error=ConnectionError("stream timeout"),
            complete_result=CompletionResult(
                text="fallback response",
                usage=TokenUsage(5, 10, 15),
                provider_id="primary",
                model="test",
            ),
        )
        orch = FallbackOrchestrator(settings=settings, ordered_providers=[primary])

        req = CompletionRequest(messages=[ChatMessage(role="user", content="hi")], stream=True)
        collected: list[StreamChunk] = []
        async for chunk in orch.complete_stream(req):
            collected.append(chunk)

        assert len(collected) == 1
        assert collected[0].delta == "fallback response"
        assert collected[0].done is True

    @pytest.mark.asyncio
    async def test_streaming_skips_non_streaming_provider(self, settings: Settings) -> None:
        non_streaming = MockProvider(
            provider_id="batch-only",
            supports_streaming=False,
            complete_result=CompletionResult(
                text="batch response",
                usage=TokenUsage(5, 10, 15),
                provider_id="batch-only",
                model="test",
            ),
        )
        orch = FallbackOrchestrator(settings=settings, ordered_providers=[non_streaming])

        req = CompletionRequest(messages=[ChatMessage(role="user", content="hi")], stream=True)
        collected: list[StreamChunk] = []
        async for chunk in orch.complete_stream(req):
            collected.append(chunk)

        assert len(collected) == 1
        assert collected[0].delta == "batch response"
