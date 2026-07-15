"""Feature flag service — local cache with PostHog sync and gradual rollout support."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class FeatureFlag:
    """A single feature flag definition."""

    key: str
    enabled: bool = False
    rollout_percentage: float = 100.0
    conditions: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def is_enabled_for(self, user_id: str | None = None, context: dict[str, Any] | None = None) -> bool:
        """Evaluate if this flag is enabled for a specific user/context."""
        if not self.enabled:
            return False

        if self.rollout_percentage >= 100.0:
            return self._check_conditions(context)

        if self.rollout_percentage <= 0.0:
            return False

        if user_id is None:
            return False

        return self._is_in_rollout(user_id) and self._check_conditions(context)

    def _is_in_rollout(self, user_id: str) -> bool:
        hash_val = int(hashlib.md5(f"{self.key}:{user_id}".encode()).hexdigest(), 16)
        return (hash_val % 100) < self.rollout_percentage

    def _check_conditions(self, context: dict[str, Any] | None) -> bool:
        if not context or not self.conditions:
            return True

        for key, value in self.conditions.items():
            ctx_val = context.get(key)
            if ctx_val != value:
                return False
        return True


class FeatureFlagService:
    """Feature flag service with local cache and gradual rollout support."""

    def __init__(self) -> None:
        self._flags: dict[str, FeatureFlag] = {}
        self._last_sync: float = 0.0
        self._sync_interval: float = 60.0

    def set_flag(
        self,
        key: str,
        enabled: bool = False,
        rollout_percentage: float = 100.0,
        conditions: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> FeatureFlag:
        """Create or update a feature flag."""
        flag = FeatureFlag(
            key=key,
            enabled=enabled,
            rollout_percentage=min(max(rollout_percentage, 0.0), 100.0),
            conditions=conditions or {},
            metadata=metadata or {},
            updated_at=time.time(),
        )
        self._flags[key] = flag
        logger.info("feature_flag.set", key=key, enabled=enabled, rollout=rollout_percentage)
        return flag

    def get_flag(self, key: str) -> FeatureFlag | None:
        """Get a feature flag by key."""
        return self._flags.get(key)

    def is_enabled(
        self,
        key: str,
        user_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Check if a feature flag is enabled for a user/context."""
        flag = self._flags.get(key)
        if flag is None:
            return False
        return flag.is_enabled_for(user_id, context)

    def get_all_flags(self, user_id: str | None = None, context: dict[str, Any] | None = None) -> dict[str, bool]:
        """Get evaluation of all flags for a user/context."""
        return {
            key: flag.is_enabled_for(user_id, context)
            for key, flag in self._flags.items()
        }

    def delete_flag(self, key: str) -> bool:
        """Delete a feature flag."""
        if key in self._flags:
            del self._flags[key]
            logger.info("feature_flag.deleted", key=key)
            return True
        return False

    def list_flags(self) -> list[dict[str, Any]]:
        """List all flags with their current state."""
        return [
            {
                "key": f.key,
                "enabled": f.enabled,
                "rollout_percentage": f.rollout_percentage,
                "conditions": f.conditions,
                "metadata": f.metadata,
            }
            for f in self._flags.values()
        ]

    def sync_from_posthog(self, flags: dict[str, dict[str, Any]]) -> int:
        """Sync flags from PostHog. Returns count of synced flags."""
        count = 0
        for key, config in flags.items():
            self.set_flag(
                key=key,
                enabled=config.get("enabled", False),
                rollout_percentage=config.get("rollout_percentage", 100.0),
                conditions=config.get("conditions"),
                metadata=config.get("metadata"),
            )
            count += 1
        self._last_sync = time.time()
        logger.info("feature_flag.synced", count=count, source="posthog")
        return count

    def needs_sync(self) -> bool:
        """Check if flags need to be re-synced from PostHog."""
        return (time.time() - self._last_sync) > self._sync_interval

    def get_flag_count(self) -> int:
        """Get total number of registered flags."""
        return len(self._flags)

    def reset(self) -> None:
        """Reset all flags."""
        self._flags.clear()
        self._last_sync = 0.0


_service: FeatureFlagService | None = None


def get_feature_flag_service() -> FeatureFlagService:
    """Get the global feature flag service instance."""
    global _service
    if _service is None:
        _service = FeatureFlagService()
    return _service


def reset_feature_flag_service() -> None:
    """Reset the global feature flag service (for testing)."""
    global _service
    _service = None
