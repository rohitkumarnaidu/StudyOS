import pytest

from studyos_api.ai.memory.context import SessionConversationMemory
from studyos_api.ai.prompts.registry import PromptRegistry
from studyos_api.ai.types import ChatMessage


@pytest.mark.unit
def test_prompt_registry_render() -> None:
    reg = PromptRegistry.default()
    text = reg.render("tutor.system.v1", context="NEET biology")
    assert "NEET biology" in text


@pytest.mark.unit
def test_session_memory_trims() -> None:
    mem = SessionConversationMemory(max_messages=3, ttl_seconds=3600)
    mem.set_messages("u:k", [ChatMessage(role="user", content=str(i)) for i in range(5)])
    got = mem.get_messages("u:k")
    assert len(got) == 3
    assert got[0].content == "2"
