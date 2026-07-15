"""Tests for presence tracking service."""

import time

import pytest

from studyos_api.services.presence import (
    PresenceService,
    UserPresence,
    get_presence_service,
    reset_presence_service,
)


@pytest.fixture(autouse=True)
def reset_presence():
    reset_presence_service()
    yield
    reset_presence_service()


@pytest.fixture
def presence() -> PresenceService:
    return PresenceService()


class TestUserPresence:
    def test_create_presence(self) -> None:
        p = UserPresence(user_id="u1", connection_id="c1")
        assert p.user_id == "u1"
        assert p.connection_id == "c1"
        assert p.is_online is True
        assert p.status == "online"
        assert p.metadata == {}

    def test_presence_with_metadata(self) -> None:
        p = UserPresence(
            user_id="u1",
            connection_id="c1",
            metadata={"room": "lobby"},
        )
        assert p.metadata == {"room": "lobby"}

    def test_heartbeat(self) -> None:
        p = UserPresence(user_id="u1", connection_id="c1")
        old_seen = p.last_seen
        time.sleep(0.01)
        p.heartbeat()
        assert p.last_seen > old_seen

    def test_to_dict(self) -> None:
        p = UserPresence(
            user_id="u1",
            connection_id="c1",
            metadata={"key": "value"},
        )
        d = p.to_dict()
        assert d["user_id"] == "u1"
        assert d["connection_id"] == "c1"
        assert d["status"] == "online"
        assert d["metadata"] == {"key": "value"}


class TestPresenceService:
    def test_set_presence(self, presence: PresenceService) -> None:
        p = presence.set_presence("u1", "c1", {"room": "lobby"})
        assert p.user_id == "u1"
        assert p.connection_id == "c1"

    def test_set_presence_updates_existing(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        p2 = presence.set_presence("u1", "c1", {"updated": True})
        assert p2.metadata == {"updated": True}

    def test_heartbeat(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        old = presence._connections["c1"].last_seen
        time.sleep(0.01)
        presence.heartbeat("c1")
        assert presence._connections["c1"].last_seen > old

    def test_heartbeat_nonexistent(self, presence: PresenceService) -> None:
        presence.heartbeat("nonexistent")

    def test_remove_presence(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        user_id = presence.remove_presence("c1")
        assert user_id == "u1"
        assert presence.get_presence("c1") is None

    def test_remove_presence_nonexistent(self, presence: PresenceService) -> None:
        result = presence.remove_presence("nonexistent")
        assert result is None

    def test_get_presence(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        p = presence.get_presence("c1")
        assert p is not None
        assert p.user_id == "u1"

    def test_get_presence_nonexistent(self, presence: PresenceService) -> None:
        assert presence.get_presence("nonexistent") is None

    def test_get_user_presence(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        presence.set_presence("u1", "c2")
        presences = presence.get_user_presence("u1")
        assert len(presences) == 2

    def test_get_user_presence_empty(self, presence: PresenceService) -> None:
        assert presence.get_user_presence("nonexistent") == []

    def test_is_user_online(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        assert presence.is_user_online("u1") is True

    def test_is_user_offline(self, presence: PresenceService) -> None:
        assert presence.is_user_online("nonexistent") is False

    def test_get_online_users(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        presence.set_presence("u2", "c2")
        online = presence.get_online_users()
        assert set(online) == {"u1", "u2"}

    def test_get_online_count(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        presence.set_presence("u2", "c2")
        assert presence.get_online_count() == 2

    def test_get_connection_count(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        presence.set_presence("u2", "c2")
        assert presence.get_connection_count() == 2

    def test_cleanup_stale(self, presence: PresenceService, monkeypatch: pytest.MonkeyPatch) -> None:
        now = time.time()
        monkeypatch.setattr(time, "time", lambda: now + 60)
        presence.set_presence("u1", "c1")
        removed = presence.cleanup_stale()
        assert removed == 1
        assert presence.get_connection_count() == 0

    def test_cleanup_no_stale(self, presence: PresenceService) -> None:
        presence.set_presence("u1", "c1")
        removed = presence.cleanup_stale()
        assert removed == 0
        assert presence.get_connection_count() == 1


class TestPresenceServiceGlobal:
    def test_get_presence_service_creates_instance(self) -> None:
        svc = get_presence_service()
        assert isinstance(svc, PresenceService)

    def test_get_presence_service_returns_same(self) -> None:
        svc1 = get_presence_service()
        svc2 = get_presence_service()
        assert svc1 is svc2
