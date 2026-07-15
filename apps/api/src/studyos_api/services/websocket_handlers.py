"""WebSocket event handlers for StudyOS realtime features."""

from __future__ import annotations

from typing import Any
from collections.abc import Callable, Coroutine

import structlog

logger = structlog.get_logger(__name__)

WSHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, dict[str, Any] | None]]


class WSHandlerRegistry:
    """Registry for WebSocket event handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[WSHandler]] = {}

    def register(self, event_type: str, handler: WSHandler) -> None:
        """Register a handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unregister(self, event_type: str, handler: WSHandler) -> None:
        """Unregister a specific handler."""
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def dispatch(self, event_type: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Dispatch an event to all registered handlers."""
        handlers = self._handlers.get(event_type, [])
        results = []
        for handler in handlers:
            try:
                result = await handler(payload)
                if result is not None:
                    results.append(result)
            except Exception:
                logger.exception("ws.handler_failed", event_type=event_type)
        return results

    def get_handlers(self, event_type: str) -> list[WSHandler]:
        """Get all handlers for an event type."""
        return self._handlers.get(event_type, [])

    def get_registered_events(self) -> list[str]:
        """Get all registered event types."""
        return list(self._handlers.keys())


_registry: WSHandlerRegistry | None = None


def get_handler_registry() -> WSHandlerRegistry:
    """Get the global handler registry."""
    global _registry
    if _registry is None:
        _registry = WSHandlerRegistry()
    return _registry


def reset_handler_registry() -> None:
    """Reset the global handler registry (for testing)."""
    global _registry
    _registry = None
