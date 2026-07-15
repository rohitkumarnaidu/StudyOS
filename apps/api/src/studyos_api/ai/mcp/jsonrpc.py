"""Minimal JSON-RPC 2.0 over HTTP for MCP-style tool servers."""

from __future__ import annotations

import httpx


class MCPJsonRpcClient:
    def __init__(self, endpoint_url: str, http: httpx.AsyncClient) -> None:
        self._url = endpoint_url.rstrip("/")
        self._http = http
        self._next_id = 1

    async def call(self, method: str, params: object) -> object:
        req_id = self._next_id
        self._next_id += 1
        body = {"jsonrpc": "2.0", "method": method, "params": params, "id": req_id}
        r = await self._http.post(
            self._url,
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=60.0,
        )
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get("error"):
            msg = f"MCP JSON-RPC error: {data['error']}"
            raise RuntimeError(msg)
        if isinstance(data, dict):
            return data.get("result")
        return data
