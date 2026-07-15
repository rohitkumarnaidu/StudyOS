"""Tests for MCPJsonRpcClient."""

from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from studyos_api.ai.mcp.jsonrpc import MCPJsonRpcClient


class TestMCPJsonRpcClientInit:
    def test_url_strips_trailing_slash(self):
        client = AsyncMock()
        rpc = MCPJsonRpcClient("http://localhost:3000/", client)
        assert rpc._url == "http://localhost:3000"

    def test_initial_id(self):
        client = AsyncMock()
        rpc = MCPJsonRpcClient("http://localhost:3000", client)
        assert rpc._next_id == 1


class TestMCPJsonRpcClientCall:
    @pytest.mark.asyncio
    @respx.mock
    async def test_call_success(self):
        route = respx.post("http://localhost:3000").mock(
            return_value=httpx.Response(200, json={"jsonrpc": "2.0", "result": {"tools": []}, "id": 1})
        )

        async with httpx.AsyncClient() as client:
            rpc = MCPJsonRpcClient("http://localhost:3000", client)
            result = await rpc.call("tools/list", {})

        assert result == {"tools": []}
        assert route.called
        body = route.calls[0].request.read().decode()
        assert '"method":"tools/list"' in body or '"method": "tools/list"' in body

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_with_params(self):
        respx.post("http://localhost:3000").mock(
            return_value=httpx.Response(200, json={"jsonrpc": "2.0", "result": "ok", "id": 1})
        )

        async with httpx.AsyncClient() as client:
            rpc = MCPJsonRpcClient("http://localhost:3000", client)
            result = await rpc.call("tools/call", {"name": "my_tool", "arguments": {"key": "value"}})

        assert result == "ok"

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_error_response(self):
        respx.post("http://localhost:3000").mock(
            return_value=httpx.Response(200, json={
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request"},
                "id": 1,
            })
        )

        async with httpx.AsyncClient() as client:
            rpc = MCPJsonRpcClient("http://localhost:3000", client)
            with pytest.raises(RuntimeError, match="MCP JSON-RPC error"):
                await rpc.call("tools/list", {})

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_http_error(self):
        respx.post("http://localhost:3000").mock(
            return_value=httpx.Response(500)
        )

        async with httpx.AsyncClient() as client:
            rpc = MCPJsonRpcClient("http://localhost:3000", client)
            with pytest.raises(httpx.HTTPStatusError):
                await rpc.call("tools/list", {})

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_non_dict_result(self):
        respx.post("http://localhost:3000").mock(
            return_value=httpx.Response(200, json={"jsonrpc": "2.0", "result": "string_result", "id": 1})
        )

        async with httpx.AsyncClient() as client:
            rpc = MCPJsonRpcClient("http://localhost:3000", client)
            result = await rpc.call("tools/list", {})

        assert result == "string_result"

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_increments_id(self):
        respx.post("http://localhost:3000").mock(
            return_value=httpx.Response(200, json={"jsonrpc": "2.0", "result": "ok", "id": 1})
        )

        async with httpx.AsyncClient() as client:
            rpc = MCPJsonRpcClient("http://localhost:3000", client)
            await rpc.call("tools/list", {})
            await rpc.call("tools/list", {})

        assert rpc._next_id == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_call_request_format(self):
        route = respx.post("http://localhost:3000").mock(
            return_value=httpx.Response(200, json={"jsonrpc": "2.0", "result": {}, "id": 1})
        )

        async with httpx.AsyncClient() as client:
            rpc = MCPJsonRpcClient("http://localhost:3000", client)
            await rpc.call("tools/list", {"foo": "bar"})

        import json
        body = json.loads(route.calls[0].request.read().decode())
        assert body["jsonrpc"] == "2.0"
        assert body["method"] == "tools/list"
        assert body["params"] == {"foo": "bar"}
        assert body["id"] == 1
