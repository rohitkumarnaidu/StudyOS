"""Tests for AI memory/conversation context management."""

import time

import pytest

from studyos_api.ai.memory.context import SessionConversationMemory
from studyos_api.ai.types import ChatMessage


@pytest.fixture()
def memory() -> SessionConversationMemory:
    return SessionConversationMemory(max_messages=10, ttl_seconds=60)


class TestSessionConversationMemory:
    def test_empty_session_returns_empty(self, memory: SessionConversationMemory) -> None:
        assert memory.get_messages("nonexistent") == []

    def test_set_and_get_messages(self, memory: SessionConversationMemory) -> None:
        msgs = [
            ChatMessage(role="user", content="Hello"),
            ChatMessage(role="assistant", content="Hi there"),
        ]
        memory.set_messages("session-1", msgs)

        result = memory.get_messages("session-1")
        assert len(result) == 2
        assert result[0].role == "user"
        assert result[0].content == "Hello"
        assert result[1].role == "assistant"

    def test_returns_copy_not_reference(self, memory: SessionConversationMemory) -> None:
        msgs = [ChatMessage(role="user", content="test")]
        memory.set_messages("s1", msgs)

        result = memory.get_messages("s1")
        result.append(ChatMessage(role="user", content="extra"))

        assert len(memory.get_messages("s1")) == 1

    def test_trims_to_max_messages(self, memory: SessionConversationMemory) -> None:
        msgs = [ChatMessage(role="user", content=f"msg-{i}") for i in range(15)]
        memory.set_messages("s1", msgs)

        result = memory.get_messages("s1")
        assert len(result) == 10
        assert result[0].content == "msg-5"
        assert result[-1].content == "msg-14"

    def test_expired_sessions_are_purged(self) -> None:
        memory = SessionConversationMemory(max_messages=10, ttl_seconds=1)
        msgs = [ChatMessage(role="user", content="hello")]
        memory.set_messages("s1", msgs)

        time.sleep(1.1)

        assert memory.get_messages("s1") == []

    def test_different_sessions_are_isolated(self, memory: SessionConversationMemory) -> None:
        memory.set_messages("s1", [ChatMessage(role="user", content="session-1")])
        memory.set_messages("s2", [ChatMessage(role="user", content="session-2")])

        assert memory.get_messages("s1")[0].content == "session-1"
        assert memory.get_messages("s2")[0].content == "session-2"

    def test_overwrite_session(self, memory: SessionConversationMemory) -> None:
        memory.set_messages("s1", [ChatMessage(role="user", content="old")])
        memory.set_messages("s1", [ChatMessage(role="user", content="new")])

        result = memory.get_messages("s1")
        assert len(result) == 1
        assert result[0].content == "new"
