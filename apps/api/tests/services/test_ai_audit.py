"""Tests for AI audit trail service."""

import pytest

from studyos_api.services.ai_audit import (
    AIAuditTrail,
    AuditEntry,
    get_audit_trail,
    reset_audit_trail,
)


@pytest.fixture(autouse=True)
def reset_audit():
    reset_audit_trail()
    yield
    reset_audit_trail()


@pytest.fixture
def audit() -> AIAuditTrail:
    return AIAuditTrail()


class TestAIAuditTrail:
    def test_log_entry(self, audit: AIAuditTrail) -> None:
        entry = audit.log(
            profile_id="u1",
            feature="chat",
            model="gpt-4o-mini",
            provider="openai",
            prompt="What is AI?",
            response="AI is artificial intelligence.",
        )
        assert entry.profile_id == "u1"
        assert entry.feature == "chat"
        assert entry.prompt_preview == "What is AI?"
        assert entry.response_preview == "AI is artificial intelligence."

    def test_log_truncates_long_text(self, audit: AIAuditTrail) -> None:
        long_text = "A" * 1000
        entry = audit.log(
            profile_id="u1",
            feature="chat",
            model="gpt-4o-mini",
            provider="openai",
            prompt=long_text,
            response=long_text,
        )
        assert len(entry.prompt_preview) <= 500
        assert len(entry.response_preview) <= 500

    def test_log_error_status(self, audit: AIAuditTrail) -> None:
        entry = audit.log(
            profile_id="u1",
            feature="chat",
            model="gpt-4o-mini",
            provider="openai",
            prompt="test",
            response="",
            status="error",
        )
        assert entry.status == "error"

    def test_get_user_history(self, audit: AIAuditTrail) -> None:
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q1", "A1")
        audit.log("u1", "roadmap", "gpt-4o-mini", "openai", "Q2", "A2")
        audit.log("u2", "chat", "gpt-4o-mini", "openai", "Q3", "A3")
        history = audit.get_user_history("u1")
        assert len(history) == 2
        assert all(e.profile_id == "u1" for e in history)

    def test_get_user_history_by_feature(self, audit: AIAuditTrail) -> None:
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q1", "A1")
        audit.log("u1", "roadmap", "gpt-4o-mini", "openai", "Q2", "A2")
        history = audit.get_user_history("u1", feature="chat")
        assert len(history) == 1
        assert history[0].feature == "chat"

    def test_get_user_history_limit(self, audit: AIAuditTrail) -> None:
        for i in range(10):
            audit.log("u1", "chat", "gpt-4o-mini", "openai", f"Q{i}", f"A{i}")
        history = audit.get_user_history("u1", limit=3)
        assert len(history) == 3

    def test_get_feature_stats(self, audit: AIAuditTrail) -> None:
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q1", "A1", status="success")
        audit.log("u2", "chat", "gpt-4o-mini", "openai", "Q2", "A2", status="success")
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q3", "", status="error")
        stats = audit.get_feature_stats("chat")
        assert stats["total_requests"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(2 / 3)

    def test_search_by_content(self, audit: AIAuditTrail) -> None:
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "What is photosynthesis?", "Photosynthesis is...")
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "What is gravity?", "Gravity is...")
        results = audit.search("photosynthesis")
        assert len(results) == 1
        assert "photosynthesis" in results[0].prompt_preview.lower()

    def test_search_by_profile(self, audit: AIAuditTrail) -> None:
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "test", "response")
        audit.log("u2", "chat", "gpt-4o-mini", "openai", "test", "response")
        results = audit.search("test", profile_id="u1")
        assert len(results) == 1
        assert results[0].profile_id == "u1"

    def test_get_recent_errors(self, audit: AIAuditTrail) -> None:
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q1", "A1", status="success")
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q2", "", status="error")
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q3", "", status="error")
        errors = audit.get_recent_errors(limit=1)
        assert len(errors) == 1
        assert errors[0].status == "error"

    def test_get_entry_count(self, audit: AIAuditTrail) -> None:
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q1", "A1")
        audit.log("u2", "chat", "gpt-4o-mini", "openai", "Q2", "A2")
        assert audit.get_entry_count() == 2

    def test_max_entries_limit(self) -> None:
        audit = AIAuditTrail(max_entries=5)
        for i in range(10):
            audit.log("u1", "chat", "gpt-4o-mini", "openai", f"Q{i}", f"A{i}")
        assert audit.get_entry_count() == 5

    def test_clear(self, audit: AIAuditTrail) -> None:
        audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q1", "A1")
        audit.clear()
        assert audit.get_entry_count() == 0

    def test_timestamp_iso(self, audit: AIAuditTrail) -> None:
        entry = audit.log("u1", "chat", "gpt-4o-mini", "openai", "Q1", "A1")
        assert "T" in entry.timestamp_iso
        assert "+" in entry.timestamp_iso or "Z" in entry.timestamp_iso


class TestAIAuditTrailGlobal:
    def test_get_audit_trail_creates_instance(self) -> None:
        a = get_audit_trail()
        assert isinstance(a, AIAuditTrail)

    def test_get_audit_trail_returns_same(self) -> None:
        a1 = get_audit_trail()
        a2 = get_audit_trail()
        assert a1 is a2
