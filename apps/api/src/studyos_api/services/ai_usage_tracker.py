"""AI usage tracker — tracks token usage per user for analytics (free-tier, no hard limits)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class UsageRecord:
    """Single AI usage record."""

    profile_id: str
    feature: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    duration_ms: float = 0.0
    status: str = "success"
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class AIUsageTracker:
    """Tracks AI usage across all features. Free-tier: no hard limits, analytics only."""

    def __init__(self) -> None:
        self._records: list[UsageRecord] = []
        self._user_totals: dict[str, dict[str, Any]] = {}

    def record(
        self,
        profile_id: str,
        feature: str,
        model: str,
        provider: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        duration_ms: float = 0.0,
        status: str = "success",
        metadata: dict[str, Any] | None = None,
    ) -> UsageRecord:
        """Record an AI usage event."""
        total = prompt_tokens + completion_tokens
        cost = _estimate_cost(provider, model, prompt_tokens, completion_tokens)

        record = UsageRecord(
            profile_id=profile_id,
            feature=feature,
            model=model,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            cost_usd=cost,
            duration_ms=duration_ms,
            status=status,
            metadata=metadata or {},
        )
        self._records.append(record)
        self._update_user_totals(profile_id, record)
        logger.info(
            "ai.usage.recorded",
            profile_id=profile_id,
            feature=feature,
            tokens=total,
            cost=round(cost, 6),
        )
        return record

    def get_user_usage(self, profile_id: str) -> dict[str, Any]:
        """Get aggregated usage for a user."""
        return self._user_totals.get(profile_id, self._empty_totals(profile_id))

    def get_feature_breakdown(self, profile_id: str) -> dict[str, dict[str, Any]]:
        """Get usage breakdown by feature for a user."""
        breakdown: dict[str, dict[str, Any]] = {}
        for record in self._records:
            if record.profile_id != profile_id:
                continue
            if record.feature not in breakdown:
                breakdown[record.feature] = self._empty_feature_totals()
            b = breakdown[record.feature]
            b["requests"] += 1
            b["total_tokens"] += record.total_tokens
            b["cost_usd"] += record.cost_usd
            b["avg_duration_ms"] = (
                (b["avg_duration_ms"] + record.duration_ms) / 2
                if b["requests"] > 1
                else record.duration_ms
            )
        return breakdown

    def get_top_users(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get top users by token usage."""
        sorted_users = sorted(
            self._user_totals.values(),
            key=lambda u: u["total_tokens"],
            reverse=True,
        )
        return sorted_users[:limit]

    def get_global_stats(self) -> dict[str, Any]:
        """Get global usage statistics."""
        total_requests = len(self._records)
        total_tokens = sum(r.total_tokens for r in self._records)
        total_cost = sum(r.cost_usd for r in self._records)
        avg_duration = (
            sum(r.duration_ms for r in self._records) / total_requests
            if total_requests > 0
            else 0.0
        )
        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "avg_duration_ms": round(avg_duration, 2),
            "unique_users": len(self._user_totals),
            "success_rate": (
                sum(1 for r in self._records if r.status == "success") / max(total_requests, 1)
            ),
        }

    def reset(self) -> None:
        """Reset all usage data."""
        self._records.clear()
        self._user_totals.clear()

    def _update_user_totals(self, profile_id: str, record: UsageRecord) -> None:
        if profile_id not in self._user_totals:
            self._user_totals[profile_id] = self._empty_totals(profile_id)
        totals = self._user_totals[profile_id]
        totals["requests"] += 1
        totals["total_tokens"] += record.total_tokens
        totals["prompt_tokens"] += record.prompt_tokens
        totals["completion_tokens"] += record.completion_tokens
        totals["cost_usd"] += record.cost_usd
        totals["features_used"].add(record.feature)
        if record.status == "success":
            totals["successful_requests"] += 1

    def _empty_totals(self, profile_id: str) -> dict[str, Any]:
        return {
            "profile_id": profile_id,
            "requests": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost_usd": 0.0,
            "successful_requests": 0,
            "features_used": set(),
            "is_free_tier": True,
        }

    def _empty_feature_totals(self) -> dict[str, Any]:
        return {
            "requests": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "avg_duration_ms": 0.0,
        }


def _estimate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate cost in USD. Free-tier: always returns 0."""
    return 0.0


_tracker: AIUsageTracker | None = None


def get_usage_tracker() -> AIUsageTracker:
    """Get the global usage tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = AIUsageTracker()
    return _tracker


def reset_usage_tracker() -> None:
    """Reset the global usage tracker (for testing)."""
    global _tracker
    _tracker = None
