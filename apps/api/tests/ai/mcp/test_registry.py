"""Tests for MCPConnectorRegistry."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.ai.mcp.registry import MCPConnectorRegistry


def _make_settings(mcp_servers_json: str = "[]"):
    s = MagicMock()
    s.ai_mcp_servers_json = mcp_servers_json
    return s


class TestMCPConnectorRegistryInit:
    def test_empty_config(self):
        client = AsyncMock()
        settings = _make_settings("[]")
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        assert registry.list_connector_ids() == []

    def test_single_http_server(self):
        client = AsyncMock()
        servers = json.dumps([{"id": "test-server", "url": "http://localhost:3000/mcp"}])
        settings = _make_settings(servers)
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        assert registry.list_connector_ids() == ["test-server"]

    def test_multiple_servers(self):
        client = AsyncMock()
        servers = json.dumps(
            [
                {"id": "server-a", "url": "http://localhost:3000/mcp"},
                {"id": "server-b", "url": "http://localhost:3001/mcp"},
            ]
        )
        settings = _make_settings(servers)
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        assert registry.list_connector_ids() == ["server-a", "server-b"]

    def test_invalid_json(self):
        client = AsyncMock()
        settings = _make_settings("{invalid json")
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        assert registry.list_connector_ids() == []

    def test_non_list_json(self):
        client = AsyncMock()
        settings = _make_settings('{"key": "value"}')
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        assert registry.list_connector_ids() == []

    def test_stdio_server_skipped(self):
        client = AsyncMock()
        servers = json.dumps([{"id": "stdio-server", "command": "npx -y @some/mcp-server"}])
        settings = _make_settings(servers)
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        assert registry.list_connector_ids() == []

    def test_mixed_http_and_stdio(self):
        client = AsyncMock()
        servers = json.dumps(
            [
                {"id": "http-server", "url": "http://localhost:3000/mcp"},
                {"id": "stdio-server", "command": "npx -y @some/mcp-server"},
            ]
        )
        settings = _make_settings(servers)
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        assert registry.list_connector_ids() == ["http-server"]

    def test_invalid_record_skipped(self):
        client = AsyncMock()
        servers = json.dumps(
            [{"id": "valid", "url": "http://localhost:3000/mcp"}, {"bad": "record"}]
        )
        settings = _make_settings(servers)
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        assert "valid" in registry.list_connector_ids()


class TestMCPConnectorRegistryOperations:
    @pytest.fixture
    def registry(self):
        client = AsyncMock()
        servers = json.dumps([{"id": "test-server", "url": "http://localhost:3000/mcp"}])
        settings = _make_settings(servers)
        return MCPConnectorRegistry(settings=settings, http_client=client)

    def test_list_connector_ids_sorted(self):
        client = AsyncMock()
        servers = json.dumps(
            [
                {"id": "z-server", "url": "http://localhost:3000/mcp"},
                {"id": "a-server", "url": "http://localhost:3001/mcp"},
            ]
        )
        settings = _make_settings(servers)
        registry = MCPConnectorRegistry(settings=settings, http_client=client)
        ids = registry.list_connector_ids()
        assert ids == ["a-server", "z-server"]

    def test_client_unknown_server_raises(self, registry):
        with pytest.raises(KeyError):
            registry._client("unknown-server")

    def test_client_known_server(self, registry):
        client = registry._client("test-server")
        assert client is not None

    @pytest.mark.asyncio
    async def test_list_tools(self, registry):
        registry._clients["test-server"].call = AsyncMock(
            return_value={"tools": [{"name": "tool1"}]}
        )
        result = await registry.list_tools("test-server")
        assert result == {"tools": [{"name": "tool1"}]}

    @pytest.mark.asyncio
    async def test_call_tool(self, registry):
        registry._clients["test-server"].call = AsyncMock(
            return_value={"content": [{"text": "result"}]}
        )
        result = await registry.call_tool("test-server", "tool1", {"arg1": "val1"})
        assert result == {"content": [{"text": "result"}]}
        registry._clients["test-server"].call.assert_awaited_once_with(
            "tools/call", {"name": "tool1", "arguments": {"arg1": "val1"}}
        )

    @pytest.mark.asyncio
    async def test_list_tools_unknown_server(self, registry):
        with pytest.raises(KeyError):
            await registry.list_tools("unknown-server")

    @pytest.mark.asyncio
    async def test_call_tool_unknown_server(self, registry):
        with pytest.raises(KeyError):
            await registry.call_tool("unknown-server", "tool1", {})
