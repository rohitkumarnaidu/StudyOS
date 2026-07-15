import pytest
from httpx import ASGITransport, AsyncClient

from studyos_api.main import create_app


@pytest.mark.api
@pytest.mark.asyncio
async def test_healthz(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    assert res.headers.get("cache-control")


@pytest.mark.api
@pytest.mark.asyncio
async def test_readyz() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/v1/readyz")
    assert res.status_code == 200
    assert res.json() == {"status": "ready"}
