"""Tests for feature flag service."""

import pytest

from studyos_api.services.feature_flags import (
    FeatureFlag,
    FeatureFlagService,
    get_feature_flag_service,
    reset_feature_flag_service,
)


@pytest.fixture(autouse=True)
def reset_service():
    reset_feature_flag_service()
    yield
    reset_feature_flag_service()


@pytest.fixture
def service() -> FeatureFlagService:
    return FeatureFlagService()


class TestFeatureFlag:
    def test_flag_disabled(self) -> None:
        flag = FeatureFlag(key="test", enabled=False)
        assert flag.is_enabled_for("user1") is False

    def test_flag_enabled_full_rollout(self) -> None:
        flag = FeatureFlag(key="test", enabled=True, rollout_percentage=100.0)
        assert flag.is_enabled_for("user1") is True

    def test_flag_zero_rollout(self) -> None:
        flag = FeatureFlag(key="test", enabled=True, rollout_percentage=0.0)
        assert flag.is_enabled_for("user1") is False

    def test_flag_no_user_id(self) -> None:
        flag = FeatureFlag(key="test", enabled=True, rollout_percentage=50.0)
        assert flag.is_enabled_for(None) is False

    def test_flag_conditions_match(self) -> None:
        flag = FeatureFlag(
            key="test",
            enabled=True,
            conditions={"platform": "mobile"},
        )
        assert flag.is_enabled_for("user1", {"platform": "mobile"}) is True

    def test_flag_conditions_no_match(self) -> None:
        flag = FeatureFlag(
            key="test",
            enabled=True,
            conditions={"platform": "mobile"},
        )
        assert flag.is_enabled_for("user1", {"platform": "web"}) is False

    def test_flag_conditions_empty(self) -> None:
        flag = FeatureFlag(key="test", enabled=True, conditions={})
        assert flag.is_enabled_for("user1") is True

    def test_flag_rollout_deterministic(self) -> None:
        flag = FeatureFlag(key="test", enabled=True, rollout_percentage=100.0)
        for i in range(100):
            assert flag.is_enabled_for(f"user{i}") is True

    def test_flag_rollout_zero_percent(self) -> None:
        flag = FeatureFlag(key="test", enabled=True, rollout_percentage=0.0)
        for i in range(100):
            assert flag.is_enabled_for(f"user{i}") is False

    def test_flag_rollout_partial(self) -> None:
        flag = FeatureFlag(key="test", enabled=True, rollout_percentage=50.0)
        enabled_count = sum(
            1 for i in range(1000)
            if flag.is_enabled_for(f"user{i}")
        )
        assert 300 < enabled_count < 700


class TestFeatureFlagService:
    def test_set_flag(self, service: FeatureFlagService) -> None:
        flag = service.set_flag("new_feature", enabled=True, rollout_percentage=50.0)
        assert flag.key == "new_feature"
        assert flag.enabled is True
        assert flag.rollout_percentage == 50.0

    def test_set_flag_overwrites(self, service: FeatureFlagService) -> None:
        service.set_flag("feature", enabled=False)
        service.set_flag("feature", enabled=True)
        assert service.is_enabled("feature") is True

    def test_get_flag(self, service: FeatureFlagService) -> None:
        service.set_flag("feature", enabled=True)
        flag = service.get_flag("feature")
        assert flag is not None
        assert flag.key == "feature"

    def test_get_flag_nonexistent(self, service: FeatureFlagService) -> None:
        assert service.get_flag("nonexistent") is None

    def test_is_enabled(self, service: FeatureFlagService) -> None:
        service.set_flag("feature", enabled=True)
        assert service.is_enabled("feature") is True

    def test_is_enabled_nonexistent(self, service: FeatureFlagService) -> None:
        assert service.is_enabled("nonexistent") is False

    def test_is_enabled_with_user(self, service: FeatureFlagService) -> None:
        service.set_flag("feature", enabled=True, rollout_percentage=100.0)
        assert service.is_enabled("feature", user_id="user1") is True

    def test_is_enabled_with_context(self, service: FeatureFlagService) -> None:
        service.set_flag(
            "feature",
            enabled=True,
            conditions={"platform": "mobile"},
        )
        assert service.is_enabled("feature", user_id="user1", context={"platform": "mobile"}) is True
        assert service.is_enabled("feature", user_id="user1", context={"platform": "web"}) is False

    def test_get_all_flags(self, service: FeatureFlagService) -> None:
        service.set_flag("flag1", enabled=True)
        service.set_flag("flag2", enabled=False)
        flags = service.get_all_flags("user1")
        assert flags["flag1"] is True
        assert flags["flag2"] is False

    def test_delete_flag(self, service: FeatureFlagService) -> None:
        service.set_flag("feature", enabled=True)
        assert service.delete_flag("feature") is True
        assert service.get_flag("feature") is None

    def test_delete_flag_nonexistent(self, service: FeatureFlagService) -> None:
        assert service.delete_flag("nonexistent") is False

    def test_list_flags(self, service: FeatureFlagService) -> None:
        service.set_flag("flag1", enabled=True, rollout_percentage=50.0)
        service.set_flag("flag2", enabled=False)
        flags = service.list_flags()
        assert len(flags) == 2

    def test_sync_from_posthog(self, service: FeatureFlagService) -> None:
        flags = {
            "flag1": {"enabled": True, "rollout_percentage": 100.0},
            "flag2": {"enabled": False, "rollout_percentage": 0.0},
            "flag3": {"enabled": True, "conditions": {"locale": "en"}},
        }
        count = service.sync_from_posthog(flags)
        assert count == 3
        assert service.is_enabled("flag1", user_id="user1") is True
        assert service.is_enabled("flag2", user_id="user1") is False

    def test_needs_sync(self, service: FeatureFlagService) -> None:
        assert service.needs_sync() is True
        service.sync_from_posthog({})
        assert service.needs_sync() is False

    def test_get_flag_count(self, service: FeatureFlagService) -> None:
        service.set_flag("flag1", enabled=True)
        service.set_flag("flag2", enabled=True)
        assert service.get_flag_count() == 2

    def test_reset(self, service: FeatureFlagService) -> None:
        service.set_flag("flag1", enabled=True)
        service.reset()
        assert service.get_flag_count() == 0
        assert service.needs_sync() is True

    def test_rollout_percentage_clamped(self, service: FeatureFlagService) -> None:
        flag = service.set_flag("test", enabled=True, rollout_percentage=150.0)
        assert flag.rollout_percentage == 100.0

        flag2 = service.set_flag("test2", enabled=True, rollout_percentage=-10.0)
        assert flag2.rollout_percentage == 0.0


class TestFeatureFlagServiceGlobal:
    def test_get_service_creates_instance(self) -> None:
        svc = get_feature_flag_service()
        assert isinstance(svc, FeatureFlagService)

    def test_get_service_returns_same(self) -> None:
        svc1 = get_feature_flag_service()
        svc2 = get_feature_flag_service()
        assert svc1 is svc2
