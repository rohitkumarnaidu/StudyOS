"""Soft budget alerts — informational only, never blocks usage. Free-tier friendly."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class BudgetAlert:
    """A soft budget alert notification."""

    profile_id: str
    threshold_type: str
    message: str
    usage_value: float
    threshold_value: float
    metadata: dict[str, Any] = field(default_factory=dict)


class SoftBudgetAlerts:
    """Informational budget alerts. Never blocks or rate-limits users."""

    def __init__(self) -> None:
        self._alerts: list[BudgetAlert] = []
        self._thresholds: dict[str, dict[str, Any]] = {}
        self._notified: dict[str, set[str]] = {}

    def set_threshold(
        self,
        profile_id: str,
        token_limit: int = 1_000_000,
        request_limit: int = 10_000,
    ) -> None:
        """Set soft thresholds for a user. Exceeding triggers notification, not block."""
        self._thresholds[profile_id] = {
            "token_limit": token_limit,
            "request_limit": request_limit,
        }
        self._notified.setdefault(profile_id, set())

    def check_and_notify(
        self,
        profile_id: str,
        current_tokens: int,
        current_requests: int,
    ) -> list[BudgetAlert]:
        """Check thresholds and generate informational alerts. Never blocks."""
        thresholds = self._thresholds.get(profile_id)
        if not thresholds:
            return []

        alerts = []
        notified = self._notified.get(profile_id, set())

        token_ratio = current_tokens / max(thresholds["token_limit"], 1)
        request_ratio = current_requests / max(thresholds["request_limit"], 1)

        for threshold_pct, alert_type in [(0.5, "50pct"), (0.8, "80pct"), (1.0, "100pct")]:
            if token_ratio >= threshold_pct and alert_type + "_tokens" not in notified:
                alerts.append(
                    BudgetAlert(
                        profile_id=profile_id,
                        threshold_type=f"tokens_{alert_type}",
                        message=f"You've used {round(token_ratio * 100)}% of your monthly token allocation.",
                        usage_value=current_tokens,
                        threshold_value=thresholds["token_limit"],
                        metadata={"ratio": round(token_ratio, 2)},
                    )
                )
                notified.add(alert_type + "_tokens")

            if request_ratio >= threshold_pct and alert_type + "_requests" not in notified:
                alerts.append(
                    BudgetAlert(
                        profile_id=profile_id,
                        threshold_type=f"requests_{alert_type}",
                        message=f"You've made {round(request_ratio * 100)}% of your monthly request allocation.",
                        usage_value=current_requests,
                        threshold_value=thresholds["request_limit"],
                        metadata={"ratio": round(request_ratio, 2)},
                    )
                )
                notified.add(alert_type + "_requests")

        self._notified[profile_id] = notified
        self._alerts.extend(alerts)

        if alerts:
            logger.info(
                "budget.alerts_generated",
                profile_id=profile_id,
                count=len(alerts),
            )

        return alerts

    def get_user_alerts(self, profile_id: str) -> list[BudgetAlert]:
        """Get all alerts for a user."""
        return [a for a in self._alerts if a.profile_id == profile_id]

    def clear_alerts(self, profile_id: str) -> None:
        """Clear alerts for a user (e.g., at start of new month)."""
        self._alerts = [a for a in self._alerts if a.profile_id != profile_id]
        self._notified.pop(profile_id, None)

    def reset(self) -> None:
        """Reset all alert data."""
        self._alerts.clear()
        self._thresholds.clear()
        self._notified.clear()


_alerts: SoftBudgetAlerts | None = None


def get_budget_alerts() -> SoftBudgetAlerts:
    """Get the global budget alerts instance."""
    global _alerts
    if _alerts is None:
        _alerts = SoftBudgetAlerts()
    return _alerts


def reset_budget_alerts() -> None:
    """Reset the global budget alerts (for testing)."""
    global _alerts
    _alerts = None
