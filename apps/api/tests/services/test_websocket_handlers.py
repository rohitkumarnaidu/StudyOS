"""Tests for WebSocket handler registry."""

from typing import Any

import pytest

from studyos_api.services.websocket_handlers import (
    WSHandlerRegistry,
    get_handler_registry,
    reset_handler_registry,
)


@pytest.fixture(autouse=True)
def reset_registry():
    reset_handler_registry()
    yield
    reset_handler_registry()


@pytest.fixture
def registry() -> WSHandlerRegistry:
    return WSHandlerRegistry()


class TestWSHandlerRegistry:
    @pytest.mark.asyncio
    async def test_register_and_dispatch(self, registry: WSHandlerRegistry) -> None:
        async def handler(payload: dict[str, Any]) -> dict[str, Any]:
            return {"echo": payload}

        registry.register("echo", handler)
        results = await registry.dispatch("echo", {"data": "hello"})
        assert len(results) == 1
        assert results[0] == {"echo": {"data": "hello"}}

    @pytest.mark.asyncio
    async def test_multiple_handlers(self, registry: WSHandlerRegistry) -> None:
        call_order: list[int] = []

        async def handler1(payload: dict[str, Any]) -> dict[str, Any]:
            call_order.append(1)
            return {"handler": 1}

        async def handler2(payload: dict[str, Any]) -> dict[str, Any]:
            call_order.append(2)
            return {"handler": 2}

        registry.register("test", handler1)
        registry.register("test", handler2)
        results = await registry.dispatch("test", {})
        assert len(results) == 2
        assert call_order == [1, 2]

    @pytest.mark.asyncio
    async def test_handler_returns_none(self, registry: WSHandlerRegistry) -> None:
        async def handler(payload: dict[str, Any]) -> None:
            return None

        registry.register("silent", handler)
        results = await registry.dispatch("silent", {})
        assert results == []

    @pytest.mark.asyncio
    async def test_handler_exception(self, registry: WSHandlerRegistry) -> None:
        async def failing_handler(payload: dict[str, Any]) -> dict[str, Any]:
            raise ValueError("Handler error")

        async def good_handler(payload: dict[str, Any]) -> dict[str, Any]:
            return {"ok": True}

        registry.register("test", failing_handler)
        registry.register("test", good_handler)
        results = await registry.dispatch("test", {})
        assert len(results) == 1
        assert results[0] == {"ok": True}

    @pytest.mark.asyncio
    async def test_dispatch_no_handlers(self, registry: WSHandlerRegistry) -> None:
        results = await registry.dispatch("unknown", {})
        assert results == []

    def test_unregister(self, registry: WSHandlerRegistry) -> None:
        async def handler(payload: dict[str, Any]) -> None:
            pass

        registry.register("test", handler)
        assert len(registry.get_handlers("test")) == 1
        registry.unregister("test", handler)
        assert len(registry.get_handlers("test")) == 0

    def test_unregister_nonexistent(self, registry: WSHandlerRegistry) -> None:
        async def handler(payload: dict[str, Any]) -> None:
            pass

        registry.unregister("test", handler)

    def test_get_registered_events(self, registry: WSHandlerRegistry) -> None:
        async def handler(payload: dict[str, Any]) -> None:
            pass

        registry.register("event1", handler)
        registry.register("event2", handler)
        events = registry.get_registered_events()
        assert set(events) == {"event1", "event2"}

    def test_get_handlers_empty(self, registry: WSHandlerRegistry) -> None:
        assert registry.get_handlers("nonexistent") == []


class TestWSHandlerRegistryGlobal:
    def test_get_handler_registry_creates_instance(self) -> None:
        reg = get_handler_registry()
        assert isinstance(reg, WSHandlerRegistry)

    def test_get_handler_registry_returns_same(self) -> None:
        reg1 = get_handler_registry()
        reg2 = get_handler_registry()
        assert reg1 is reg2
