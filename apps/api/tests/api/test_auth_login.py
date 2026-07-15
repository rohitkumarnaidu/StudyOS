import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.auth
@pytest.mark.asyncio
async def test_auth_login_memory_demo(api_client: AsyncClient) -> None:
    res = await api_client.post(
        "/v1/auth/login",
        json={"email": "demo@studyos.app", "password": "demo"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body
    assert "refresh_token" in body
