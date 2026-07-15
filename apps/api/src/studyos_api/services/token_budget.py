"""Token budget enforcement middleware — blocks usage when budget exceeded."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, UTC
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class TokenBudgetEnforcer:
    """Enforces token budgets per user. Returns False when budget exceeded."""

    def __init__(
        self,
        daily_token_limit: int = 100_000,
        monthly_token_limit: int = 2_000_000,
    ) -> None:
        self._daily_limit = daily_token_limit
        self._monthly_limit = monthly_token_limit
        self._daily_usage: dict[str, dict[str, int]] = defaultdict(lambda: {"tokens": 0, "date": ""})
        self._monthly_usage: dict[str, dict[str, int]] = defaultdict(lambda: {"tokens": 0, "month": ""})

    def check_budget(self, user_sub: str) -> dict[str, Any]:
        """Check if user is within budget. Returns status dict."""
        now = datetime.now(UTC)
        today = now.strftime("%Y-%m-%d")
        this_month = now.strftime("%Y-%m")

        daily = self._daily_usage[user_sub]
        monthly = self._monthly_usage[user_sub]

        daily_ok = daily["date"] != today or daily["tokens"] < self._daily_limit
        monthly_ok = monthly["month"] != this_month or monthly["tokens"] < self._monthly_limit

        daily_remaining = max(0, self._daily_limit - (daily["tokens"] if daily["date"] == today else 0))
        monthly_remaining = max(0, self._monthly_limit - (monthly["tokens"] if monthly["month"] == this_month else 0))

        return {
            "allowed": daily_ok and monthly_ok,
            "daily_remaining": daily_remaining,
            "monthly_remaining": monthly_remaining,
            "daily_limit": self._daily_limit,
            "monthly_limit": self._monthly_limit,
        }

    def record_usage(self, user_sub: str, tokens: int) -> None:
        """Record token usage against budget."""
        now = datetime.now(UTC)
        today = now.strftime("%Y-%m-%d")
        this_month = now.strftime("%Y-%m")

        daily = self._daily_usage[user_sub]
        if daily["date"] != today:
            daily["date"] = today
            daily["tokens"] = 0
        daily["tokens"] += tokens

        monthly = self._monthly_usage[user_sub]
        if monthly["month"] != this_month:
            monthly["month"] = this_month
            monthly["tokens"] = 0
        monthly["tokens"] += tokens

    def reset(self) -> None:
        """Clear all usage data (for testing)."""
        self._daily_usage.clear()
        self._monthly_usage.clear()


_budget_enforcer: TokenBudgetEnforcer | None = None


def get_budget_enforcer() -> TokenBudgetEnforcer:
    """Get the global budget enforcer instance."""
    global _budget_enforcer
    if _budget_enforcer is None:
        _budget_enforcer = TokenBudgetEnforcer()
    return _budget_enforcer


def reset_budget_enforcer() -> None:
    """Reset the global budget enforcer (for testing)."""
    global _budget_enforcer
    _budget_enforcer = None
