"""Tests for soft budget alerts (informational only, never blocks)."""

import pytest

from studyos_api.services.budget_alerts import (
    SoftBudgetAlerts,
    get_budget_alerts,
    reset_budget_alerts,
)


@pytest.fixture(autouse=True)
def reset_alerts():
    reset_budget_alerts()
    yield
    reset_budget_alerts()


@pytest.fixture
def alerts() -> SoftBudgetAlerts:
    return SoftBudgetAlerts()


class TestSoftBudgetAlerts:
    def test_set_threshold(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=500_000, request_limit=5000)
        assert "u1" in alerts._thresholds

    def test_no_alerts_without_threshold(self, alerts: SoftBudgetAlerts) -> None:
        result = alerts.check_and_notify("u1", 1000, 10)
        assert result == []

    def test_50pct_token_alert(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        result = alerts.check_and_notify("u1", 500, 10)
        assert len(result) == 1
        assert "50pct" in result[0].threshold_type

    def test_80pct_token_alert(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        result = alerts.check_and_notify("u1", 800, 10)
        assert any("80pct" in a.threshold_type for a in result)

    def test_100pct_token_alert(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        result = alerts.check_and_notify("u1", 1200, 10)
        assert any("100pct" in a.threshold_type for a in result)

    def test_no_duplicate_alerts(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        alerts.check_and_notify("u1", 600, 10)
        result2 = alerts.check_and_notify("u1", 700, 10)
        assert result2 == []

    def test_request_threshold_alert(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        result = alerts.check_and_notify("u1", 100, 80)
        assert any("requests_80pct" in a.threshold_type for a in result)

    def test_get_user_alerts(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        alerts.check_and_notify("u1", 600, 10)
        user_alerts = alerts.get_user_alerts("u1")
        assert len(user_alerts) >= 1

    def test_clear_alerts(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        alerts.check_and_notify("u1", 600, 10)
        alerts.clear_alerts("u1")
        assert alerts.get_user_alerts("u1") == []

    def test_reset(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        alerts.check_and_notify("u1", 600, 10)
        alerts.reset()
        assert alerts.get_user_alerts("u1") == []

    def test_alert_message_is_informative(self, alerts: SoftBudgetAlerts) -> None:
        alerts.set_threshold("u1", token_limit=1000, request_limit=100)
        result = alerts.check_and_notify("u1", 600, 10)
        assert "used" in result[0].message.lower()
        assert "allocation" in result[0].message.lower()


class TestSoftBudgetAlertsGlobal:
    def test_get_budget_alerts_creates_instance(self) -> None:
        a = get_budget_alerts()
        assert isinstance(a, SoftBudgetAlerts)

    def test_get_budget_alerts_returns_same(self) -> None:
        a1 = get_budget_alerts()
        a2 = get_budget_alerts()
        assert a1 is a2
