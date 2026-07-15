"""Tests for progress API endpoints."""

import pytest
from httpx import AsyncClient

from support.auth_tokens import bearer_token


@pytest.mark.api
@pytest.mark.asyncio
async def test_toggle_subtopic_requires_auth(api_client: AsyncClient) -> None:
    res = await api_client.post("/v1/progress/subtopics/00000000-0000-0000-0000-000000000001/toggle")
    assert res.status_code in (401, 403)


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_chapter_progress_requires_auth(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/progress/chapters/00000000-0000-0000-0000-000000000001")
    assert res.status_code in (401, 403)


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_streak_requires_auth(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/progress/streak")
    assert res.status_code in (401, 403)


@pytest.mark.api
@pytest.mark.asyncio
async def test_progress_invalid_uuid_returns_422(api_client: AsyncClient) -> None:
    token = bearer_token(roles=["student"])
    res = await api_client.get(
        "/v1/progress/chapters/not-a-uuid",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422


@pytest.mark.api
@pytest.mark.asyncio
async def test_toggle_subtopic_invalid_uuid_returns_422(api_client: AsyncClient) -> None:
    token = bearer_token(roles=["student"])
    res = await api_client.post(
        "/v1/progress/subtopics/not-a-uuid/toggle",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 422
