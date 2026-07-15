"""Presence tracking service — tracks online users and their activity."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

_PRESENCE_TTL_SECONDS = 30


@dataclass
class UserPresence:
    """Tracks a user's online presence."""

    user_id: str
    connection_id: str
    last_seen: float = field(default_factory=time.time)
    status: str = "online"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_online(self) -> bool:
        return (time.time() - self.last_seen) < _PRESENCE_TTL_SECONDS

    def heartbeat(self) -> None:
        self.last_seen = time.time()
        self.status = "online"

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "connection_id": self.connection_id,
            "status": self.status if self.is_online else "away",
            "last_seen": self.last_seen,
            "metadata": self.metadata,
        }


class PresenceService:
    """Tracks user presence across WebSocket connections."""

    def __init__(self) -> None:
        self._connections: dict[str, UserPresence] = {}
        self._user_connections: dict[str, set[str]] = {}

    def set_presence(
        self,
        user_id: str,
        connection_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> UserPresence:
        """Set or update a user's presence."""
        presence = UserPresence(
            user_id=user_id,
            connection_id=connection_id,
            metadata=metadata or {},
        )
        self._connections[connection_id] = presence
        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()
        self._user_connections[user_id].add(connection_id)
        logger.info("presence.set", user_id=user_id, connection_id=connection_id)
        return presence

    def heartbeat(self, connection_id: str) -> None:
        """Update last-seen timestamp for a connection."""
        presence = self._connections.get(connection_id)
        if presence:
            presence.heartbeat()

    def remove_presence(self, connection_id: str) -> str | None:
        """Remove a connection's presence. Returns user_id if found."""
        presence = self._connections.pop(connection_id, None)
        if presence:
            user_conns = self._user_connections.get(presence.user_id)
            if user_conns:
                user_conns.discard(connection_id)
                if not user_conns:
                    del self._user_connections[presence.user_id]
            logger.info("presence.removed", user_id=presence.user_id)
            return presence.user_id
        return None

    def get_presence(self, connection_id: str) -> UserPresence | None:
        """Get presence for a specific connection."""
        return self._connections.get(connection_id)

    def get_user_presence(self, user_id: str) -> list[UserPresence]:
        """Get all active presence entries for a user."""
        conn_ids = self._user_connections.get(user_id, set())
        return [
            self._connections[cid]
            for cid in conn_ids
            if cid in self._connections
        ]

    def is_user_online(self, user_id: str) -> bool:
        """Check if a user has any active connections."""
        conn_ids = self._user_connections.get(user_id, set())
        return any(
            cid in self._connections and self._connections[cid].is_online
            for cid in conn_ids
        )

    def get_online_users(self) -> list[str]:
        """Get list of all online user IDs."""
        online = []
        for user_id, conn_ids in self._user_connections.items():
            if any(
                cid in self._connections and self._connections[cid].is_online
                for cid in conn_ids
            ):
                online.append(user_id)
        return online

    def get_online_count(self) -> int:
        """Get total number of online users."""
        return len(self.get_online_users())

    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self._connections)

    def cleanup_stale(self) -> int:
        """Remove stale connections. Returns count of removed entries."""
        stale = [
            cid
            for cid, presence in self._connections.items()
            if not presence.is_online
        ]
        for cid in stale:
            self.remove_presence(cid)
        if stale:
            logger.info("presence.cleanup", removed=len(stale))
        return len(stale)


_presence: PresenceService | None = None


def get_presence_service() -> PresenceService:
    """Get the global presence service instance."""
    global _presence
    if _presence is None:
        _presence = PresenceService()
    return _presence


def reset_presence_service() -> None:
    """Reset the global presence service (for testing)."""
    global _presence
    _presence = None
