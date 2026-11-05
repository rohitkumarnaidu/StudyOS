"""WebSocket routes for StudyOS realtime features."""

from __future__ import annotations

import json

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from studyos_api.services.presence import get_presence_service
from studyos_api.services.websocket_handlers import get_handler_registry
from studyos_api.services.websocket_manager import get_connection_manager

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/v1/realtime")
async def websocket_realtime(websocket: WebSocket) -> None:
    """Main WebSocket endpoint for realtime events."""
    manager = get_connection_manager()
    presence = get_presence_service()
    registry = get_handler_registry()

    connection_id = f"conn-{id(websocket)}"
    await manager.connect(websocket, connection_id)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal(
                    connection_id,
                    {
                        "type": "error",
                        "message": "Invalid JSON",
                    },
                )
                continue

            event_type = message.get("type", "unknown")

            if event_type == "ping":
                presence.heartbeat(connection_id)
                await manager.send_personal(connection_id, {"type": "pong"})
                continue

            if event_type == "join_room":
                room_id = message.get("room_id", "")
                if room_id:
                    await manager.join_room(connection_id, room_id)
                    await manager.send_personal(
                        connection_id,
                        {
                            "type": "room_joined",
                            "room_id": room_id,
                            "members": manager.get_room_members(room_id),
                        },
                    )
                continue

            if event_type == "leave_room":
                room_id = message.get("room_id", "")
                if room_id:
                    await manager.leave_room(connection_id, room_id)
                    await manager.send_personal(
                        connection_id,
                        {
                            "type": "room_left",
                            "room_id": room_id,
                        },
                    )
                continue

            if event_type == "room_broadcast":
                room_id = message.get("room_id", "")
                if room_id:
                    await manager.broadcast_to_room(
                        room_id,
                        {"type": "room_message", "data": message.get("data")},
                        exclude=connection_id,
                    )
                continue

            if event_type == "presence_update":
                user_id = message.get("user_id", "")
                if user_id:
                    presence.set_presence(
                        user_id,
                        connection_id,
                        metadata=message.get("metadata", {}),
                    )
                    await manager.send_personal(
                        connection_id,
                        {
                            "type": "presence_confirmed",
                            "user_id": user_id,
                            "online_count": presence.get_online_count(),
                        },
                    )
                continue

            if event_type == "get_online_users":
                online = presence.get_online_users()
                await manager.send_personal(
                    connection_id,
                    {
                        "type": "online_users",
                        "users": online,
                        "count": len(online),
                    },
                )
                continue

            results = await registry.dispatch(event_type, message)
            for result in results:
                await manager.send_personal(connection_id, result)

    except WebSocketDisconnect:
        await manager.disconnect(connection_id)
        presence.remove_presence(connection_id)
    except Exception:
        logger.exception("ws.error", connection_id=connection_id)
        await manager.disconnect(connection_id)
        presence.remove_presence(connection_id)
