"""AI audit trail — logs every AI request/response for compliance and debugging."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import structlog
from datetime import UTC

logger = structlog.get_logger(__name__)


@dataclass
class AuditEntry:
    """Single audit log entry."""

    profile_id: str
    feature: str
    model: str
    provider: str
    prompt_preview: str
    response_preview: str
    status: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def timestamp_iso(self) -> str:
        from datetime import datetime
        return datetime.fromtimestamp(self.timestamp, tz=UTC).isoformat()


class AIAuditTrail:
    """Audit trail for all AI interactions. Free-tier: logs everything for quality monitoring."""

    def __init__(self, max_entries: int = 100_000) -> None:
        self._entries: list[AuditEntry] = []
        self._max_entries = max_entries

    def log(
        self,
        profile_id: str,
        feature: str,
        model: str,
        provider: str,
        prompt: str,
        response: str,
        status: str = "success",
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Log an AI interaction."""
        entry = AuditEntry(
            profile_id=profile_id,
            feature=feature,
            model=model,
            provider=provider,
            prompt_preview=prompt[:500],
            response_preview=response[:500],
            status=status,
            metadata=metadata or {},
        )
        self._entries.append(entry)

        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        logger.info(
            "ai.audit.logged",
            profile_id=profile_id,
            feature=feature,
            status=status,
        )
        return entry

    def get_user_history(
        self,
        profile_id: str,
        limit: int = 50,
        feature: str | None = None,
    ) -> list[AuditEntry]:
        """Get audit history for a user."""
        entries = [e for e in self._entries if e.profile_id == profile_id]
        if feature:
            entries = [e for e in entries if e.feature == feature]
        return entries[-limit:]

    def get_feature_stats(self, feature: str) -> dict[str, Any]:
        """Get statistics for a specific feature."""
        entries = [e for e in self._entries if e.feature == feature]
        total = len(entries)
        success = sum(1 for e in entries if e.status == "success")
        return {
            "feature": feature,
            "total_requests": total,
            "successful": success,
            "failed": total - success,
            "success_rate": success / max(total, 1),
        }

    def search(
        self,
        query: str,
        limit: int = 20,
        profile_id: str | None = None,
    ) -> list[AuditEntry]:
        """Search audit log by content."""
        entries = self._entries
        if profile_id:
            entries = [e for e in entries if e.profile_id == profile_id]

        results = []
        query_lower = query.lower()
        for entry in entries:
            if (
                query_lower in entry.prompt_preview.lower()
                or query_lower in entry.response_preview.lower()
            ):
                results.append(entry)
            if len(results) >= limit:
                break

        return results

    def get_recent_errors(self, limit: int = 10) -> list[AuditEntry]:
        """Get recent failed AI requests."""
        return [
            e for e in reversed(self._entries)
            if e.status == "error"
        ][:limit]

    def get_entry_count(self) -> int:
        """Get total number of audit entries."""
        return len(self._entries)

    def clear(self) -> None:
        """Clear all audit entries."""
        self._entries.clear()


_audit: AIAuditTrail | None = None


def get_audit_trail() -> AIAuditTrail:
    """Get the global audit trail instance."""
    global _audit
    if _audit is None:
        _audit = AIAuditTrail()
    return _audit


def reset_audit_trail() -> None:
    """Reset the global audit trail (for testing)."""
    global _audit
    _audit = None
