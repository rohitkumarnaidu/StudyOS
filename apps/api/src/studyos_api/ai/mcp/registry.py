"""Register MCP connectors from `STUDYOS_AI_MCP_SERVERS_JSON`."""

from __future__ import annotations

import json

import httpx
import structlog

from studyos_api.ai.mcp.jsonrpc import MCPJsonRpcClient
from studyos_api.ai.mcp.types import MCPServerRecord
from studyos_api.core.config import Settings

logger = structlog.get_logger(__name__)


class MCPConnectorRegistry:
    """Resolve configured MCP servers and expose tool operations."""

    def __init__(self, *, settings: Settings, http_client: httpx.AsyncClient) -> None:
        self._http = http_client
        self._clients: dict[str, MCPJsonRpcClient] = {}
        try:
            raw = json.loads(settings.ai_mcp_servers_json or "[]")
        except json.JSONDecodeError:
            logger.warning("ai.mcp.invalid_json", using="empty")
            raw = []
        if not isinstance(raw, list):
            raw = []
        for item in raw:
            try:
                rec = MCPServerRecord.model_validate(item)
            except Exception as exc:
                logger.warning("ai.mcp.skip_record", error=str(exc))
                continue
            if rec.url:
                self._clients[rec.id] = MCPJsonRpcClient(rec.url, http_client)
            elif rec.command:
                logger.info("ai.mcp.stdio_reserved", id=rec.id, command=rec.command)

    def list_connector_ids(self) -> list[str]:
        return sorted(self._clients.keys())

    def _client(self, server_id: str) -> MCPJsonRpcClient:
        client = self._clients.get(server_id)
        if client is None:
            msg = f"Unknown MCP server id: {server_id}"
            raise KeyError(msg)
        return client

    async def list_tools(self, server_id: str) -> object:
        return await self._client(server_id).call("tools/list", {})

    async def call_tool(self, server_id: str, name: str, arguments: dict[str, object]) -> object:
        return await self._client(server_id).call(
            "tools/call",
            {"name": name, "arguments": arguments},
        )
