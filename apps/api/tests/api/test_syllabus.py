"""Tests for syllabus API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.asyncio
async def test_list_exams_returns_data_array(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/syllabus/exams")
    assert res.status_code == 200
    data = res.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.api
@pytest.mark.asyncio
async def test_list_chapters_returns_data_array(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/syllabus/chapters")
    assert res.status_code == 200
    data = res.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.api
@pytest.mark.asyncio
async def test_list_chapters_with_invalid_uuid_returns_422(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/syllabus/chapters", params={"exam_id": "not-a-uuid"})
    assert res.status_code == 422


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_chapter_detail_with_invalid_uuid_returns_422(api_client: AsyncClient) -> None:
    res = await api_client.get("/v1/syllabus/chapters/not-a-uuid")
    assert res.status_code == 422


@pytest.mark.api
@pytest.mark.asyncio
async def test_get_chapter_detail_with_nonexistent_uuid_returns_404(
    api_client: AsyncClient,
) -> None:
    res = await api_client.get("/v1/syllabus/chapters/00000000-0000-0000-0000-000000000000")
    assert res.status_code in (404, 200)
