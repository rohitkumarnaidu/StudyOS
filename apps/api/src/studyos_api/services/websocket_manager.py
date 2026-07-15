"""WebSocket connection manager for StudyOS realtime infrastructure."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections with room-based broadcasting."""

    def __init__(self) -> None:
        self._active_connections: dict[str, WebSocket] = {}
        self._rooms: dict[str, dict[str, WebSocket]] = {}
        self._user_rooms: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, connection_id: str) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self._active_connections[connection_id] = websocket
        logger.info("ws.connected", connection_id=connection_id)

    async def disconnect(self, connection_id: str) -> None:
        """Remove a WebSocket connection and clean up rooms."""
        self._active_connections.pop(connection_id, None)
        for room_id in list(self._user_rooms.get(connection_id, set())):
            await self.leave_room(connection_id, room_id)
        self._user_rooms.pop(connection_id, None)
        logger.info("ws.disconnected", connection_id=connection_id)

    async def send_personal(self, connection_id: str, message: dict[str, Any]) -> None:
        """Send a message to a specific connection."""
        ws = self._active_connections.get(connection_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast a message to all active connections."""
        disconnected = []
        for conn_id, ws in self._active_connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(conn_id)
        for conn_id in disconnected:
            await self.disconnect(conn_id)

    async def join_room(self, connection_id: str, room_id: str) -> None:
        """Add a connection to a room."""
        if room_id not in self._rooms:
            self._rooms[room_id] = {}
        ws = self._active_connections.get(connection_id)
        if ws:
            self._rooms[room_id][connection_id] = ws
            if connection_id not in self._user_rooms:
                self._user_rooms[connection_id] = set()
            self._user_rooms[connection_id].add(room_id)
            logger.info("ws.joined_room", connection_id=connection_id, room_id=room_id)

    async def leave_room(self, connection_id: str, room_id: str) -> None:
        """Remove a connection from a room."""
        room = self._rooms.get(room_id)
        if room:
            room.pop(connection_id, None)
            if not room:
                del self._rooms[room_id]
        user_rooms = self._user_rooms.get(connection_id)
        if user_rooms:
            user_rooms.discard(room_id)
            if not user_rooms:
                del self._user_rooms[connection_id]
        logger.info("ws.left_room", connection_id=connection_id, room_id=room_id)

    async def broadcast_to_room(self, room_id: str, message: dict[str, Any], exclude: str | None = None) -> None:
        """Broadcast a message to all connections in a room."""
        room = self._rooms.get(room_id, {})
        disconnected = []
        for conn_id, ws in room.items():
            if conn_id == exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(conn_id)
        for conn_id in disconnected:
            await self.disconnect(conn_id)

    def get_room_members(self, room_id: str) -> list[str]:
        """Get all connection IDs in a room."""
        return list(self._rooms.get(room_id, {}).keys())

    def get_connection_count(self) -> int:
        """Get total active connection count."""
        return len(self._active_connections)

    def get_room_count(self) -> int:
        """Get total active room count."""
        return len(self._rooms)

    def get_user_rooms(self, connection_id: str) -> set[str]:
        """Get all rooms a connection belongs to."""
        return self._user_rooms.get(connection_id, set())

    def is_connected(self, connection_id: str) -> bool:
        """Check if a connection is active."""
        return connection_id in self._active_connections


_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


def reset_connection_manager() -> None:
    """Reset the global connection manager (for testing)."""
    global _manager
    _manager = None
