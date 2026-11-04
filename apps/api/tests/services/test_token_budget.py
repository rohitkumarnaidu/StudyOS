"""Tests for token budget enforcement."""

from studyos_api.services.token_budget import TokenBudgetEnforcer


class TestTokenBudgetEnforcer:
    def setup_method(self) -> None:
        self.enforcer = TokenBudgetEnforcer(daily_token_limit=1000, monthly_token_limit=5000)

    def test_check_budget_initial(self) -> None:
        result = self.enforcer.check_budget("user1")
        assert result["allowed"] is True
        assert result["daily_remaining"] == 1000
        assert result["monthly_remaining"] == 5000

    def test_record_usage_reduces_budget(self) -> None:
        self.enforcer.record_usage("user1", 500)
        result = self.enforcer.check_budget("user1")
        assert result["allowed"] is True
        assert result["daily_remaining"] == 500
        assert result["monthly_remaining"] == 4500

    def test_daily_budget_exceeded(self) -> None:
        self.enforcer.record_usage("user1", 1000)
        result = self.enforcer.check_budget("user1")
        assert result["allowed"] is False
        assert result["daily_remaining"] == 0

    def test_monthly_budget_exceeded(self) -> None:
        self.enforcer.record_usage("user1", 5000)
        result = self.enforcer.check_budget("user1")
        assert result["allowed"] is False
        assert result["monthly_remaining"] == 0

    def test_different_users_isolated(self) -> None:
        self.enforcer.record_usage("user1", 1000)
        result1 = self.enforcer.check_budget("user1")
        result2 = self.enforcer.check_budget("user2")
        assert result1["allowed"] is False
        assert result2["allowed"] is True

    def test_reset_clears_usage(self) -> None:
        self.enforcer.record_usage("user1", 500)
        self.enforcer.reset()
        result = self.enforcer.check_budget("user1")
        assert result["allowed"] is True
        assert result["daily_remaining"] == 1000
