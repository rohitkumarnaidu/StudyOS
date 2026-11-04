"""Tests for OpenAIProvider."""

from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from studyos_api.ai.providers.openai_provider import OpenAIProvider
from studyos_api.ai.types import ChatMessage, CompletionRequest


class TestOpenAIProviderInit:
    def test_provider_id(self):
        client = AsyncMock()
        provider = OpenAIProvider(
            client, api_key="sk-test", base_url="https://api.openai.com/v1", default_model="gpt-4"
        )
        assert provider.provider_id == "openai"

    def test_base_url_strips_trailing_slash(self):
        client = AsyncMock()
        provider = OpenAIProvider(
            client, api_key="sk-test", base_url="https://api.openai.com/v1/", default_model="gpt-4"
        )
        assert provider._base == "https://api.openai.com/v1"

    def test_headers(self):
        client = AsyncMock()
        provider = OpenAIProvider(
            client, api_key="sk-test", base_url="https://api.openai.com/v1", default_model="gpt-4"
        )
        headers = provider._headers()
        assert headers["Authorization"] == "Bearer sk-test"
        assert headers["Content-Type"] == "application/json"

    def test_model_from_request(self):
        client = AsyncMock()
        provider = OpenAIProvider(
            client, api_key="sk-test", base_url="https://api.openai.com/v1", default_model="gpt-4"
        )
        req = CompletionRequest(messages=[], model="gpt-3.5-turbo")
        assert provider._model(req) == "gpt-3.5-turbo"

    def test_model_fallback_to_default(self):
        client = AsyncMock()
        provider = OpenAIProvider(
            client, api_key="sk-test", base_url="https://api.openai.com/v1", default_model="gpt-4"
        )
        req = CompletionRequest(messages=[])
        assert provider._model(req) == "gpt-4"


class TestOpenAIProviderComplete:
    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_success(self):
        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": "Hello world"}, "finish_reason": "stop"}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
                },
            )
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(
                messages=[ChatMessage(role="user", content="Hi")], temperature=0.5, max_tokens=100
            )
            result = await provider.complete(req)

        assert result.text == "Hello world"
        assert result.provider_id == "openai"
        assert result.model == "gpt-4"
        assert result.finish_reason == "stop"
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 20
        assert result.usage.total_tokens == 30
        assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_with_default_max_tokens(self):
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": "Hi"}, "finish_reason": "stop"}],
                    "usage": {},
                },
            )
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(
                messages=[ChatMessage(role="user", content="Hi")], max_tokens=None
            )
            result = await provider.complete(req)

        assert result.text == "Hi"
        assert result.usage.total_tokens == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_empty_choices(self):
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "choices": [],
                    "usage": {},
                },
            )
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")])
            result = await provider.complete(req)

        assert result.text == ""

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_http_error(self):
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(500)
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")])
            with pytest.raises(httpx.HTTPStatusError):
                await provider.complete(req)


class TestOpenAIProviderStream:
    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_success(self):
        sse_data = (
            'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n'
            'data: {"choices": [{"delta": {"content": " world"}}]}\n\n'
            'data: {"usage": {"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15}}\n\n'
            "data: [DONE]\n\n"
        )

        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=sse_data)
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], stream=True)
            chunks = []
            async for chunk in provider.complete_stream(req):
                chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0].delta == "Hello"
        assert chunks[0].done is False
        assert chunks[1].delta == " world"
        assert chunks[2].done is True
        assert chunks[2].usage is not None
        assert chunks[2].usage.total_tokens == 15
        assert route.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_with_max_tokens(self):
        sse_data = 'data: {"choices": [{"delta": {"content": "Hi"}}]}\n\ndata: [DONE]\n\n'

        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=sse_data)
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(
                messages=[ChatMessage(role="user", content="Hi")], stream=True, max_tokens=50
            )
            chunks = []
            async for chunk in provider.complete_stream(req):
                chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[-1].done is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_skips_non_data_lines(self):
        sse_data = (
            "some random line\n\n"
            'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n'
            "data: [DONE]\n\n"
        )

        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=sse_data)
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], stream=True)
            chunks = []
            async for chunk in provider.complete_stream(req):
                chunks.append(chunk)

        assert len(chunks) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_handles_invalid_json(self):
        sse_data = (
            "data: {invalid json}\n\n"
            'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n'
            "data: [DONE]\n\n"
        )

        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=sse_data)
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], stream=True)
            chunks = []
            async for chunk in provider.complete_stream(req):
                chunks.append(chunk)

        assert len(chunks) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_default_usage_when_missing(self):
        sse_data = 'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\ndata: [DONE]\n\n'

        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, text=sse_data)
        )

        async with httpx.AsyncClient() as client:
            provider = OpenAIProvider(
                client,
                api_key="sk-test",
                base_url="https://api.openai.com/v1",
                default_model="gpt-4",
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], stream=True)
            chunks = []
            async for chunk in provider.complete_stream(req):
                chunks.append(chunk)

        assert chunks[-1].done is True
        assert chunks[-1].usage is not None
        assert chunks[-1].usage.total_tokens == 0
