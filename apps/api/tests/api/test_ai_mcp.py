import pytest
from httpx import AsyncClient

from support.auth_tokens import bearer_token


@pytest.mark.api
@pytest.mark.auth
@pytest.mark.asyncio
async def test_mcp_servers_requires_auth(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/ai/mcp/servers")
    assert res.status_code == 401


@pytest.mark.api
@pytest.mark.auth
@pytest.mark.asyncio
async def test_mcp_servers_ok_for_student(api_client: AsyncClient) -> None:
    token = bearer_token(roles=["student"])
    res = await api_client.get("/v1/ai/mcp/servers", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["server_ids"] == []
