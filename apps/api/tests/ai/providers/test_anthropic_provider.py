"""Tests for AnthropicProvider."""

from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from studyos_api.ai.providers.anthropic_provider import AnthropicProvider, _split_system
from studyos_api.ai.types import ChatMessage, CompletionRequest


class TestSplitSystem:
    def test_no_system_messages(self):
        msgs = [ChatMessage(role="user", content="Hello")]
        system, out = _split_system(msgs)
        assert system == ""
        assert out == [{"role": "user", "content": "Hello"}]

    def test_with_system_message(self):
        msgs = [
            ChatMessage(role="system", content="You are helpful"),
            ChatMessage(role="user", content="Hello"),
        ]
        system, out = _split_system(msgs)
        assert system == "You are helpful"
        assert out == [{"role": "user", "content": "Hello"}]

    def test_multiple_system_messages(self):
        msgs = [
            ChatMessage(role="system", content="Part 1"),
            ChatMessage(role="system", content="Part 2"),
            ChatMessage(role="user", content="Hello"),
        ]
        system, out = _split_system(msgs)
        assert system == "Part 1\n\nPart 2"

    def test_ignores_non_user_assistant(self):
        msgs = [
            ChatMessage(role="system", content="System"),
            ChatMessage(role="user", content="Hello"),
        ]
        system, out = _split_system(msgs)
        assert len(out) == 1
        assert out[0]["role"] == "user"


class TestAnthropicProviderInit:
    def test_provider_id(self):
        client = AsyncMock()
        provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
        assert provider.provider_id == "anthropic"

    def test_base_url_strips_trailing_slash(self):
        client = AsyncMock()
        provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com/", default_model="claude-3")
        assert provider._base == "https://api.anthropic.com"

    def test_headers(self):
        client = AsyncMock()
        provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
        headers = provider._headers()
        assert headers["x-api-key"] == "sk-ant-test"
        assert headers["anthropic-version"] == "2023-06-01"
        assert headers["content-type"] == "application/json"

    def test_model_from_request(self):
        client = AsyncMock()
        provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
        req = CompletionRequest(messages=[], model="claude-2")
        assert provider._model(req) == "claude-2"

    def test_model_fallback_to_default(self):
        client = AsyncMock()
        provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
        req = CompletionRequest(messages=[])
        assert provider._model(req) == "claude-3"


class TestAnthropicProviderComplete:
    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_success(self):
        respx.post("https://api.anthropic.com/v1/messages").mock(
            return_value=httpx.Response(200, json={
                "content": [{"type": "text", "text": "Hello from Claude"}],
                "usage": {"input_tokens": 10, "output_tokens": 20},
                "stop_reason": "end_turn",
            })
        )

        async with httpx.AsyncClient() as client:
            provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
            req = CompletionRequest(
                messages=[ChatMessage(role="user", content="Hi")],
                max_tokens=100, temperature=0.5,
            )
            result = await provider.complete(req)

        assert result.text == "Hello from Claude"
        assert result.provider_id == "anthropic"
        assert result.model == "claude-3"
        assert result.finish_reason == "end_turn"
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 20
        assert result.usage.total_tokens == 30

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_with_system_message(self):
        respx.post("https://api.anthropic.com/v1/messages").mock(
            return_value=httpx.Response(200, json={
                "content": [{"type": "text", "text": "Hi"}],
                "usage": {"input_tokens": 5, "output_tokens": 5},
                "stop_reason": "stop",
            })
        )

        async with httpx.AsyncClient() as client:
            provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
            req = CompletionRequest(
                messages=[
                    ChatMessage(role="system", content="Be helpful"),
                    ChatMessage(role="user", content="Hi"),
                ],
                max_tokens=100,
            )
            result = await provider.complete(req)

        assert result.text == "Hi"

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_default_max_tokens(self):
        respx.post("https://api.anthropic.com/v1/messages").mock(
            return_value=httpx.Response(200, json={
                "content": [{"type": "text", "text": "Hi"}],
                "usage": {"input_tokens": 1, "output_tokens": 1},
                "stop_reason": None,
            })
        )

        async with httpx.AsyncClient() as client:
            provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], max_tokens=None)
            result = await provider.complete(req)

        assert result.text == "Hi"

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_multiple_content_blocks(self):
        respx.post("https://api.anthropic.com/v1/messages").mock(
            return_value=httpx.Response(200, json={
                "content": [
                    {"type": "text", "text": "Hello"},
                    {"type": "text", "text": " world"},
                    {"type": "tool_use", "id": "1"},
                ],
                "usage": {"input_tokens": 5, "output_tokens": 5},
                "stop_reason": "stop",
            })
        )

        async with httpx.AsyncClient() as client:
            provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], max_tokens=100)
            result = await provider.complete(req)

        assert result.text == "Hello world"

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_empty_content(self):
        respx.post("https://api.anthropic.com/v1/messages").mock(
            return_value=httpx.Response(200, json={
                "content": [],
                "usage": {"input_tokens": 1, "output_tokens": 0},
                "stop_reason": "stop",
            })
        )

        async with httpx.AsyncClient() as client:
            provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], max_tokens=100)
            result = await provider.complete(req)

        assert result.text == ""

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_http_error(self):
        respx.post("https://api.anthropic.com/v1/messages").mock(
            return_value=httpx.Response(401)
        )

        async with httpx.AsyncClient() as client:
            provider = AnthropicProvider(client, api_key="sk-ant-test", base_url="https://api.anthropic.com", default_model="claude-3")
            req = CompletionRequest(messages=[ChatMessage(role="user", content="Hi")], max_tokens=100)
            with pytest.raises(httpx.HTTPStatusError):
                await provider.complete(req)
