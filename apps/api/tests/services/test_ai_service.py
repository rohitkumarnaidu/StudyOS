"""Tests for AI service."""

from unittest.mock import MagicMock

import pytest

from studyos_api.ai.service import AIService
from studyos_api.ai.types import ChatMessage


class TestAIServiceUnit:
    @pytest.fixture
    def mock_settings(self):
        settings = MagicMock()
        settings.ai_memory_max_messages = 10
        settings.ai_memory_session_ttl_seconds = 3600
        settings.ai_mcp_servers_json = "[]"
        return settings

    @pytest.fixture
    def mock_http_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_usage_sink(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_settings, mock_http_client, mock_usage_sink):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("studyos_api.ai.service.build_llm_chain", lambda s, h: [])
            mp.setattr("studyos_api.ai.service.FallbackOrchestrator", lambda **kw: MagicMock())
            mp.setattr("studyos_api.ai.service.MCPConnectorRegistry", lambda **kw: MagicMock())
            mp.setattr("studyos_api.ai.service.PromptRegistry", MagicMock())
            mp.setattr("studyos_api.ai.service.SessionConversationMemory", lambda **kw: MagicMock())

            return AIService(
                settings=mock_settings,
                http_client=mock_http_client,
                usage_sink=mock_usage_sink,
            )

    def test_session_key_with_user_and_conversation(self, service):
        key = service._session_key("user-123", "conv-456")
        assert key == "user-123:conv-456"

    def test_session_key_without_user(self, service):
        key = service._session_key(None, "conv-456")
        assert key is None

    def test_session_key_without_conversation(self, service):
        key = service._session_key("user-123", None)
        assert key is None

    def test_session_key_without_both(self, service):
        key = service._session_key(None, None)
        assert key is None

    def test_merge_messages_without_session(self, service):
        messages = [
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there"),
        ]
        merged = service._merge_messages(
            user_sub=None,
            conversation_key=None,
            incoming=messages,
        )
        assert len(merged) == 2

    def test_persist_turn_without_session(self, service):
        service._persist_turn(
            user_sub=None,
            conversation_key=None,
            merged=[ChatMessage(role="user", content="Hello")],
            assistant_text="Hi",
        )

    def test_mcp_property(self, service):
        assert service.mcp is not None
