"""Tests for AI base provider."""

import asyncio

from studyos_api.ai.providers.base import AbstractLLMProvider
from studyos_api.ai.types import (
    ChatMessage,
    CompletionRequest,
    CompletionResult,
    TokenUsage,
)


class ConcreteProvider(AbstractLLMProvider):
    """Concrete implementation for testing."""

    @property
    def provider_id(self) -> str:
        return "test-provider"

    async def complete(self, req: CompletionRequest) -> CompletionResult:
        return CompletionResult(
            text="Test response",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            provider_id=self.provider_id,
            model="test-model",
        )


class TestAbstractLLMProvider:
    def test_provider_id(self):
        provider = ConcreteProvider()
        assert provider.provider_id == "test-provider"

    def test_supports_streaming_default(self):
        provider = ConcreteProvider()
        assert provider.supports_streaming() is True

    def test_complete_stream_fallback(self):
        provider = ConcreteProvider()
        req = CompletionRequest(messages=[ChatMessage(role="user", content="test")])
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:

            async def collect_stream():
                chunks = []
                async for chunk in provider.complete_stream(req):
                    chunks.append(chunk)
                return chunks

            chunks = loop.run_until_complete(collect_stream())
        finally:
            loop.close()
        assert len(chunks) == 1
        assert chunks[0].delta == "Test response"
        assert chunks[0].done is True
        assert chunks[0].provider_id == "test-provider"


class TestConcreteProvider:
    def test_complete(self):
        provider = ConcreteProvider()
        req = CompletionRequest(messages=[ChatMessage(role="user", content="test")])
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(provider.complete(req))
        finally:
            loop.close()
        assert result.text == "Test response"
        assert result.provider_id == "test-provider"
        assert result.model == "test-model"
        assert result.usage.total_tokens == 15
