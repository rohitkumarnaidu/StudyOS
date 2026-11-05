"""Tests for AI service — mocking dependencies."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.ai.types import ChatMessage


class TestAIService:
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
    async def test_session_key(self, mock_settings, mock_usage_sink) -> None:
        from studyos_api.ai.service import AIService

        mock_provider = MagicMock()
        mock_provider.provider_id = "openai"
        svc = AIService(
            settings=mock_settings,
            http_client=AsyncMock(),
            usage_sink=mock_usage_sink,
            llm_chain=[mock_provider],
        )
        assert svc._session_key("user1", "conv1") == "user1:conv1"
        assert svc._session_key(None, "conv1") is None
        assert svc._session_key("user1", None) is None

    @pytest.mark.asyncio
    async def test_merge_messages_no_memory(self, mock_settings, mock_usage_sink) -> None:
        from studyos_api.ai.service import AIService

        mock_provider = MagicMock()
        mock_provider.provider_id = "openai"
        svc = AIService(
            settings=mock_settings,
            http_client=AsyncMock(),
            usage_sink=mock_usage_sink,
            llm_chain=[mock_provider],
        )
        msgs = [ChatMessage(role="user", content=f"msg{i}") for i in range(15)]
        merged = svc._merge_messages(user_sub=None, conversation_key=None, incoming=msgs)
        assert len(merged) == 10

    @pytest.mark.asyncio
    async def test_persist_turn_no_key(self, mock_settings, mock_usage_sink) -> None:
        from studyos_api.ai.service import AIService

        mock_provider = MagicMock()
        mock_provider.provider_id = "openai"
        svc = AIService(
            settings=mock_settings,
            http_client=AsyncMock(),
            usage_sink=mock_usage_sink,
            llm_chain=[mock_provider],
        )
        svc._persist_turn(
            user_sub=None,
            conversation_key=None,
            merged=[],
            assistant_text="response",
        )

    @pytest.mark.asyncio
    async def test_mcp_property(self, mock_settings, mock_usage_sink) -> None:
        from studyos_api.ai.service import AIService

        mock_provider = MagicMock()
        mock_provider.provider_id = "openai"
        svc = AIService(
            settings=mock_settings,
            http_client=AsyncMock(),
            usage_sink=mock_usage_sink,
            llm_chain=[mock_provider],
        )
        assert svc.mcp is not None
