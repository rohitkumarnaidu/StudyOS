"""Extended tests for feature flags — additional coverage."""

from studyos_api.services.feature_flags import FeatureFlagService


class TestFeatureFlagServiceEdgeCases:
    def test_set_flag_overwrites_existing(self):
        svc = FeatureFlagService()
        svc.set_flag("flag1", enabled=True)
        svc.set_flag("flag1", enabled=False)
        assert svc.is_enabled("flag1") is False

    def test_is_enabled_unknown_flag(self):
        svc = FeatureFlagService()
        assert svc.is_enabled("nonexistent_flag") is False

    def test_is_enabled_with_user_and_conditions(self):
        svc = FeatureFlagService()
        svc.set_flag(
            "flag",
            enabled=True,
            rollout_percentage=100.0,
            conditions={"plan": "premium"},
        )
        assert svc.is_enabled("flag", user_id="user-123", context={"plan": "premium"}) is True
        assert svc.is_enabled("flag", user_id="user-123", context={"plan": "free"}) is False

    def test_get_all_flags_empty(self):
        svc = FeatureFlagService()
        assert svc.get_all_flags() == {}

    def test_list_flags_empty(self):
        svc = FeatureFlagService()
        assert svc.list_flags() == []

    def test_rollout_percentage_boundary_50(self):
        svc = FeatureFlagService()
        svc.set_flag("half", enabled=True, rollout_percentage=50.0)
        enabled_count = sum(1 for i in range(1000) if svc.is_enabled("half", user_id=f"user{i}"))
        assert 400 < enabled_count < 600

    def test_rollout_percentage_boundary_1(self):
        svc = FeatureFlagService()
        svc.set_flag("rare", enabled=True, rollout_percentage=1.0)
        enabled_count = sum(1 for i in range(1000) if svc.is_enabled("rare", user_id=f"user{i}"))
        assert enabled_count < 30

    def test_multiple_conditions_all_must_match(self):
        svc = FeatureFlagService()
        svc.set_flag(
            "complex",
            enabled=True,
            conditions={"plan": "premium", "region": "us", "platform": "mobile"},
        )
        assert (
            svc.is_enabled(
                "complex",
                user_id="u1",
                context={"plan": "premium", "region": "us", "platform": "mobile"},
            )
            is True
        )
        assert (
            svc.is_enabled(
                "complex",
                user_id="u1",
                context={"plan": "premium", "region": "eu", "platform": "mobile"},
            )
            is False
        )


class TestFeatureFlagSync:
    def test_sync_overwrites_existing_flags(self):
        svc = FeatureFlagService()
        svc.set_flag("flag1", enabled=True)
        svc.sync_from_posthog({"flag1": {"enabled": False}})
        assert svc.is_enabled("flag1", user_id="user1") is False

    def test_sync_preserves_unrelated_flags(self):
        svc = FeatureFlagService()
        svc.set_flag("local_flag", enabled=True)
        svc.sync_from_posthog({"remote_flag": {"enabled": True}})
        assert svc.is_enabled("local_flag") is True
        assert svc.is_enabled("remote_flag") is True

    def test_needs_sync_after_sync(self):
        svc = FeatureFlagService()
        assert svc.needs_sync() is True
        svc.sync_from_posthog({})
        assert svc.needs_sync() is False
