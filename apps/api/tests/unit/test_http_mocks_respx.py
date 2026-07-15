"""Example: mock outbound HTTP with respx (use for provider integration tests)."""

import httpx
import pytest
import respx


@pytest.mark.unit
@pytest.mark.asyncio
@respx.mock
async def test_respx_mocks_outbound_http() -> None:
    respx.get("https://example.test/ping").mock(return_value=httpx.Response(200, json={"ok": True}))
    async with httpx.AsyncClient() as client:
        r = await client.get("https://example.test/ping")
    assert r.status_code == 200
    assert r.json() == {"ok": True}
