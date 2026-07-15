"""Tests for WebSocket connection manager."""

import pytest

from studyos_api.services.websocket_manager import (
    ConnectionManager,
    get_connection_manager,
    reset_connection_manager,
)


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self) -> None:
        self._accepted = False
        self._sent: list = []
        self._closed = False

    async def accept(self) -> None:
        self._accepted = True

    async def send_json(self, data: dict) -> None:
        self._sent.append(data)

    async def close(self, code: int = 1000) -> None:
        self._closed = True

    @property
    def sent_messages(self) -> list:
        return self._sent


@pytest.fixture(autouse=True)
def reset_manager():
    reset_connection_manager()
    yield
    reset_connection_manager()


@pytest.fixture
def manager() -> ConnectionManager:
    return ConnectionManager()


class TestConnectionManager:
    @pytest.mark.asyncio
    async def test_connect(self, manager: ConnectionManager) -> None:
        ws = MockWebSocket()
        await manager.connect(ws, "conn-1")
        assert ws._accepted is True
        assert manager.is_connected("conn-1")
        assert manager.get_connection_count() == 1

    @pytest.mark.asyncio
    async def test_disconnect(self, manager: ConnectionManager) -> None:
        ws = MockWebSocket()
        await manager.connect(ws, "conn-1")
        await manager.disconnect("conn-1")
        assert not manager.is_connected("conn-1")
        assert manager.get_connection_count() == 0

    @pytest.mark.asyncio
    async def test_send_personal(self, manager: ConnectionManager) -> None:
        ws = MockWebSocket()
        await manager.connect(ws, "conn-1")
        await manager.send_personal("conn-1", {"type": "test"})
        assert len(ws.sent_messages) == 1
        assert ws.sent_messages[0] == {"type": "test"}

    @pytest.mark.asyncio
    async def test_send_personal_nonexistent(self, manager: ConnectionManager) -> None:
        await manager.send_personal("nonexistent", {"type": "test"})

    @pytest.mark.asyncio
    async def test_broadcast(self, manager: ConnectionManager) -> None:
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        await manager.connect(ws1, "conn-1")
        await manager.connect(ws2, "conn-2")
        await manager.broadcast({"type": "broadcast"})
        assert len(ws1.sent_messages) == 1
        assert len(ws2.sent_messages) == 1

    @pytest.mark.asyncio
    async def test_join_room(self, manager: ConnectionManager) -> None:
        ws = MockWebSocket()
        await manager.connect(ws, "conn-1")
        await manager.join_room("conn-1", "room-1")
        assert "conn-1" in manager.get_room_members("room-1")

    @pytest.mark.asyncio
    async def test_leave_room(self, manager: ConnectionManager) -> None:
        ws = MockWebSocket()
        await manager.connect(ws, "conn-1")
        await manager.join_room("conn-1", "room-1")
        await manager.leave_room("conn-1", "room-1")
        assert "conn-1" not in manager.get_room_members("room-1")

    @pytest.mark.asyncio
    async def test_broadcast_to_room(self, manager: ConnectionManager) -> None:
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        await manager.connect(ws1, "conn-1")
        await manager.connect(ws2, "conn-2")
        await manager.join_room("conn-1", "room-1")
        await manager.join_room("conn-2", "room-1")
        await manager.broadcast_to_room("room-1", {"type": "room_msg"}, exclude="conn-1")
        assert len(ws1.sent_messages) == 0
        assert len(ws2.sent_messages) == 1

    @pytest.mark.asyncio
    async def test_broadcast_to_room_empty(self, manager: ConnectionManager) -> None:
        await manager.broadcast_to_room("nonexistent", {"type": "test"})

    @pytest.mark.asyncio
    async def test_disconnect_cleans_rooms(self, manager: ConnectionManager) -> None:
        ws = MockWebSocket()
        await manager.connect(ws, "conn-1")
        await manager.join_room("conn-1", "room-1")
        await manager.disconnect("conn-1")
        assert manager.get_room_members("room-1") == []

    @pytest.mark.asyncio
    async def test_get_user_rooms(self, manager: ConnectionManager) -> None:
        ws = MockWebSocket()
        await manager.connect(ws, "conn-1")
        await manager.join_room("conn-1", "room-1")
        await manager.join_room("conn-1", "room-2")
        rooms = manager.get_user_rooms("conn-1")
        assert rooms == {"room-1", "room-2"}

    def test_get_room_count(self, manager: ConnectionManager) -> None:
        assert manager.get_room_count() == 0

    def test_is_connected_false(self, manager: ConnectionManager) -> None:
        assert manager.is_connected("nonexistent") is False


class TestConnectionManagerGlobal:
    def test_get_connection_manager_creates_instance(self) -> None:
        mgr = get_connection_manager()
        assert isinstance(mgr, ConnectionManager)

    def test_get_connection_manager_returns_same(self) -> None:
        mgr1 = get_connection_manager()
        mgr2 = get_connection_manager()
        assert mgr1 is mgr2
