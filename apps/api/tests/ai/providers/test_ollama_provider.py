"""Tests for OllamaProvider."""

from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from studyos_api.ai.providers.ollama import OllamaProvider
from studyos_api.ai.types import ChatMessage, CompletionRequest


class TestOllamaProviderInit:
    def test_provider_id(self):
        client = AsyncMock()
        provider = OllamaProvider(client, base_url="http://localhost:11434", default_model="llama3")
        assert provider.provider_id == "ollama"

    def test_base_url_strips_trailing_slash(self):
        client = AsyncMock()
        provider = OllamaProvider(
            client, base_url="http://localhost:11434/", default_model="llama3"
        )
        assert provider._base == "http://localhost:11434"

    def test_model_from_request(self):
        client = AsyncMock()
        provider = OllamaProvider(client, base_url="http://localhost:11434", default_model="llama3")
        req = CompletionRequest(messages=[], model="mistral")
        assert provider._model(req) == "mistral"

    def test_model_fallback_to_default(self):
        client = AsyncMock()
        provider = OllamaProvider(client, base_url="http://localhost:11434", default_model="llama3")
        req = CompletionRequest(messages=[])
        assert provider._model(req) == "llama3"

    def test_payload_with_max_tokens(self):
        client = AsyncMock()
        provider = OllamaProvider(client, base_url="http://localhost:11434", default_model="llama3")
        req = CompletionRequest(
            messages=[ChatMessage(role="user", content="Hi")], temperature=0.5, max_tokens=100
        )
        payload = provider._payload(req, stream=False)
        assert payload["model"] == "llama3"
        assert payload["stream"] is False
        assert payload["options"]["temperature"] == 0.5
        assert payload["options"]["num_predict"] == 100

    def test_payload_without_max_tokens(self):
        client = AsyncMock()
        provider = OllamaProvider(client, base_url="http://localhost:11434", default_model="llama3")
        req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], max_tokens=None)
        payload = provider._payload(req, stream=True)
        assert "num_predict" not in payload["options"]
        assert payload["stream"] is True


class TestOllamaProviderComplete:
    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_success(self):
        respx.post("http://localhost:11434/api/chat").mock(
            return_value=httpx.Response(
                200,
                json={
                    "message": {"content": "Hello from Ollama"},
                    "done": True,
                    "prompt_eval_count": 10,
                    "eval_count": 20,
                },
            )
        )

        async with httpx.AsyncClient() as client:
            provider = OllamaProvider(
                client, base_url="http://localhost:11434", default_model="llama3"
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")])
            result = await provider.complete(req)

        assert result.text == "Hello from Ollama"
        assert result.provider_id == "ollama"
        assert result.model == "llama3"
        assert result.finish_reason == "stop"
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 20
        assert result.usage.total_tokens == 30

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_estimates_tokens_when_eval_count_zero(self):
        respx.post("http://localhost:11434/api/chat").mock(
            return_value=httpx.Response(
                200,
                json={
                    "message": {"content": "Hello there"},
                    "done": True,
                    "prompt_eval_count": 5,
                    "eval_count": 0,
                },
            )
        )

        async with httpx.AsyncClient() as client:
            provider = OllamaProvider(
                client, base_url="http://localhost:11434", default_model="llama3"
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")])
            result = await provider.complete(req)

        assert result.text == "Hello there"
        assert result.usage.completion_tokens >= 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_no_done_flag(self):
        respx.post("http://localhost:11434/api/chat").mock(
            return_value=httpx.Response(
                200,
                json={
                    "message": {"content": "Partial"},
                    "done": False,
                    "prompt_eval_count": 5,
                    "eval_count": 10,
                },
            )
        )

        async with httpx.AsyncClient() as client:
            provider = OllamaProvider(
                client, base_url="http://localhost:11434", default_model="llama3"
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")])
            result = await provider.complete(req)

        assert result.finish_reason is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_empty_message(self):
        respx.post("http://localhost:11434/api/chat").mock(
            return_value=httpx.Response(
                200,
                json={
                    "message": None,
                    "done": True,
                    "prompt_eval_count": 0,
                    "eval_count": 0,
                },
            )
        )

        async with httpx.AsyncClient() as client:
            provider = OllamaProvider(
                client, base_url="http://localhost:11434", default_model="llama3"
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")])
            result = await provider.complete(req)

        assert result.text == ""

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_http_error(self):
        respx.post("http://localhost:11434/api/chat").mock(return_value=httpx.Response(500))

        async with httpx.AsyncClient() as client:
            provider = OllamaProvider(
                client, base_url="http://localhost:11434", default_model="llama3"
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")])
            with pytest.raises(httpx.HTTPStatusError):
                await provider.complete(req)


class TestOllamaProviderStream:
    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_success(self):
        lines = (
            '{"message": {"content": "Hel"}, "done": false}\n'
            '{"message": {"content": "Hello"}, "done": false}\n'
            '{"message": {"content": "Hello world"}, "done": true, "prompt_eval_count": 5, "eval_count": 10}\n'
        )

        respx.post("http://localhost:11434/api/chat").mock(
            return_value=httpx.Response(200, text=lines)
        )

        async with httpx.AsyncClient() as client:
            provider = OllamaProvider(
                client, base_url="http://localhost:11434", default_model="llama3"
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], stream=True)
            chunks = []
            async for chunk in provider.complete_stream(req):
                chunks.append(chunk)

        assert any(c.delta == "Hel" for c in chunks)
        assert any(c.done is True for c in chunks)
        done_chunk = [c for c in chunks if c.done][0]
        assert done_chunk.usage is not None
        assert done_chunk.usage.total_tokens == 15

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_skips_empty_lines(self):
        lines = (
            "\n"
            '{"message": {"content": "Hi"}, "done": true, "prompt_eval_count": 1, "eval_count": 2}\n'
        )

        respx.post("http://localhost:11434/api/chat").mock(
            return_value=httpx.Response(200, text=lines)
        )

        async with httpx.AsyncClient() as client:
            provider = OllamaProvider(
                client, base_url="http://localhost:11434", default_model="llama3"
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], stream=True)
            chunks = []
            async for chunk in provider.complete_stream(req):
                chunks.append(chunk)

        assert len(chunks) >= 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_stream_handles_invalid_json(self):
        lines = (
            "invalid json\n"
            '{"message": {"content": "Hi"}, "done": true, "prompt_eval_count": 1, "eval_count": 2}\n'
        )

        respx.post("http://localhost:11434/api/chat").mock(
            return_value=httpx.Response(200, text=lines)
        )

        async with httpx.AsyncClient() as client:
            provider = OllamaProvider(
                client, base_url="http://localhost:11434", default_model="llama3"
            )
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], stream=True)
            chunks = []
            async for chunk in provider.complete_stream(req):
                chunks.append(chunk)

        assert len(chunks) >= 1
