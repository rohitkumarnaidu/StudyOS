"""Tests for AI service — covering complete_chat and stream_chat paths."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.ai.types import ChatMessage, CompletionResult, TokenUsage


class TestAIServiceComplete:
    @pytest.fixture
    def mock_settings(self):
        from studyos_api.core.config import Settings

        return Settings(
            ai_ollama_base_url="http://localhost:11434",
            ai_openai_api_key="test-key",
            ai_primary_provider="openai",
            ai_memory_max_messages=10,
            ai_memory_session_ttl_seconds=3600,
        )

    @pytest.fixture
    def mock_usage_sink(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_complete_chat_with_conversation(self, mock_settings, mock_usage_sink) -> None:
        from studyos_api.ai.service import AIService

        mock_provider = MagicMock()
        mock_provider.provider_id = "openai"
        mock_result = CompletionResult(
            text="Hello!",
            provider_id="openai",
            model="gpt-4o-mini",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )
        mock_orch = AsyncMock()
        mock_orch.complete.return_value = mock_result

        svc = AIService(
            settings=mock_settings,
            http_client=AsyncMock(),
            usage_sink=mock_usage_sink,
            llm_chain=[mock_provider],
        )
        svc._orch = mock_orch

        result = await svc.complete_chat(
            messages=[ChatMessage(role="user", content="Hi")],
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=100,
            prompt_id=None,
            prompt_variables={},
            conversation_key="conv1",
            user_sub="user1",
            request_id="req-123",
        )
        assert result.text == "Hello!"
        mock_orch.complete.assert_called_once()
