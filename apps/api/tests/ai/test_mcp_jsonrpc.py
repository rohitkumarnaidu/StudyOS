"""Tests for AI MCP JSON-RPC client."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.ai.mcp.jsonrpc import MCPJsonRpcClient


class TestMCPJsonRpcClient:
    @pytest.mark.asyncio
    async def test_call_success(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"jsonrpc": "2.0", "result": {"tools": []}, "id": 1}
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_response

        client = MCPJsonRpcClient(endpoint_url="http://localhost:8080/mcp", http=mock_http)
        result = await client.call("tools/list", {})

        assert result == {"tools": []}
        mock_http.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_error(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": "Invalid Request"},
            "id": 1,
        }
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_response

        client = MCPJsonRpcClient(endpoint_url="http://localhost:8080/mcp", http=mock_http)

        with pytest.raises(RuntimeError, match="MCP JSON-RPC error"):
            await client.call("invalid", {})

    @pytest.mark.asyncio
    async def test_call_increments_id(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"jsonrpc": "2.0", "result": "ok", "id": 1}
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_response

        client = MCPJsonRpcClient(endpoint_url="http://localhost:8080/mcp", http=mock_http)
        await client.call("method1", {})
        await client.call("method2", {})

        call_args = mock_http.post.call_args_list[1]
        assert call_args[1]["json"]["id"] == 2

    @pytest.mark.asyncio
    async def test_call_http_error(self) -> None:
        mock_http = AsyncMock()
        mock_http.post.side_effect = Exception("Connection refused")

        client = MCPJsonRpcClient(endpoint_url="http://localhost:8080/mcp", http=mock_http)

        with pytest.raises(Exception, match="Connection refused"):
            await client.call("tools/list", {})
