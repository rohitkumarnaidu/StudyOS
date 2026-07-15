"""Tests for AI usage tracker (free-tier)."""

import pytest

from studyos_api.services.ai_usage_tracker import (
    AIUsageTracker,
    get_usage_tracker,
    reset_usage_tracker,
)


@pytest.fixture(autouse=True)
def reset_tracker():
    reset_usage_tracker()
    yield
    reset_usage_tracker()


@pytest.fixture
def tracker() -> AIUsageTracker:
    return AIUsageTracker()


class TestAIUsageTracker:
    def test_record_usage(self, tracker: AIUsageTracker) -> None:
        record = tracker.record(
            profile_id="u1",
            feature="chat",
            model="gpt-4o-mini",
            provider="openai",
            prompt_tokens=100,
            completion_tokens=50,
            duration_ms=1500.0,
        )
        assert record.profile_id == "u1"
        assert record.feature == "chat"
        assert record.total_tokens == 150
        assert record.cost_usd == 0.0  # Free-tier

    def test_record_usage_error(self, tracker: AIUsageTracker) -> None:
        record = tracker.record(
            profile_id="u1",
            feature="chat",
            model="gpt-4o-mini",
            provider="openai",
            status="error",
        )
        assert record.status == "error"

    def test_get_user_usage(self, tracker: AIUsageTracker) -> None:
        tracker.record("u1", "chat", "gpt-4o-mini", "openai", 100, 50)
        tracker.record("u1", "roadmap", "gpt-4o-mini", "openai", 200, 100)
        usage = tracker.get_user_usage("u1")
        assert usage["requests"] == 2
        assert usage["total_tokens"] == 450
        assert usage["is_free_tier"] is True

    def test_get_user_usage_empty(self, tracker: AIUsageTracker) -> None:
        usage = tracker.get_user_usage("nonexistent")
        assert usage["requests"] == 0

    def test_get_feature_breakdown(self, tracker: AIUsageTracker) -> None:
        tracker.record("u1", "chat", "gpt-4o-mini", "openai", 100, 50)
        tracker.record("u1", "chat", "gpt-4o-mini", "openai", 80, 40)
        tracker.record("u1", "roadmap", "gpt-4o-mini", "openai", 200, 100)
        breakdown = tracker.get_feature_breakdown("u1")
        assert "chat" in breakdown
        assert "roadmap" in breakdown
        assert breakdown["chat"]["requests"] == 2
        assert breakdown["roadmap"]["requests"] == 1

    def test_get_top_users(self, tracker: AIUsageTracker) -> None:
        tracker.record("u1", "chat", "gpt-4o-mini", "openai", 500, 250)
        tracker.record("u2", "chat", "gpt-4o-mini", "openai", 100, 50)
        tracker.record("u3", "chat", "gpt-4o-mini", "openai", 300, 150)
        top = tracker.get_top_users(limit=2)
        assert len(top) == 2
        assert top[0]["profile_id"] == "u1"

    def test_get_global_stats(self, tracker: AIUsageTracker) -> None:
        tracker.record("u1", "chat", "gpt-4o-mini", "openai", 100, 50, 1000.0)
        tracker.record("u2", "roadmap", "gpt-4o-mini", "openai", 200, 100, 2000.0)
        stats = tracker.get_global_stats()
        assert stats["total_requests"] == 2
        assert stats["total_tokens"] == 450
        assert stats["unique_users"] == 2
        assert stats["success_rate"] == 1.0

    def test_get_global_stats_with_errors(self, tracker: AIUsageTracker) -> None:
        tracker.record("u1", "chat", "gpt-4o-mini", "openai", 100, 50, status="success")
        tracker.record("u1", "chat", "gpt-4o-mini", "openai", 0, 0, status="error")
        stats = tracker.get_global_stats()
        assert stats["success_rate"] == 0.5

    def test_reset(self, tracker: AIUsageTracker) -> None:
        tracker.record("u1", "chat", "gpt-4o-mini", "openai", 100, 50)
        tracker.reset()
        stats = tracker.get_global_stats()
        assert stats["total_requests"] == 0

    def test_free_tier_always_zero_cost(self, tracker: AIUsageTracker) -> None:
        record = tracker.record(
            profile_id="u1",
            feature="chat",
            model="gpt-4o-mini",
            provider="openai",
            prompt_tokens=100000,
            completion_tokens=50000,
        )
        assert record.cost_usd == 0.0


class TestAIUsageTrackerGlobal:
    def test_get_usage_tracker_creates_instance(self) -> None:
        t = get_usage_tracker()
        assert isinstance(t, AIUsageTracker)

    def test_get_usage_tracker_returns_same(self) -> None:
        t1 = get_usage_tracker()
        t2 = get_usage_tracker()
        assert t1 is t2
