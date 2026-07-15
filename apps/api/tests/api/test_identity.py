import pytest
from httpx import AsyncClient

from support.auth_tokens import bearer_token


@pytest.mark.api
@pytest.mark.asyncio
async def test_me_anonymous(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/me")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["authenticated"] is False


@pytest.mark.api
@pytest.mark.asyncio
async def test_me_jwt_student(api_client: AsyncClient) -> None:
    token = bearer_token(roles=["student"])
    res = await api_client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["authenticated"] is True
    assert data["data"]["user"]["sub"] == "demo@studyos.app"


@pytest.mark.api
@pytest.mark.asyncio
async def test_admin_forbidden_for_student(api_client: AsyncClient) -> None:
    token = bearer_token(roles=["student"])
    res = await api_client.get("/v1/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


@pytest.mark.api
@pytest.mark.asyncio
async def test_admin_ok_platform_admin(api_client: AsyncClient) -> None:
    token = bearer_token(roles=["platform_admin"])
    res = await api_client.get("/v1/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["status"] == "admin-ok"


@pytest.mark.api
@pytest.mark.asyncio
async def test_validated_echo(api_client: AsyncClient) -> None:
    res = await api_client.post("/v1/examples/echo", json={"message": "hello"})
    assert res.status_code == 200
    body = res.json()
    assert body["data"]["echo"] == "hello"


@pytest.mark.api
@pytest.mark.asyncio
async def test_v2_status(api_client: AsyncClient) -> None:
    res = await api_client.get("/v2/status")
    assert res.status_code == 200
    assert res.json()["api_version"] == "v2"
