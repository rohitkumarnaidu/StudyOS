"""Integration tests for syllabus service with mocked database pool."""

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from studyos_api.services.syllabus_service import SyllabusService


class FakeRow(dict):
    """Mimics asyncpg.Row for dict access."""

    def __getitem__(self, key):
        return dict.__getitem__(self, key)


class MockConnection:
    """Mock asyncpg connection."""

    def __init__(self) -> None:
        self._queries: list[tuple[str, tuple]] = []

    async def fetchrow(self, query: str, *args: object) -> FakeRow | None:
        self._queries.append((query, args))
        return None

    async def fetch(self, query: str, *args: object) -> list[FakeRow]:
        self._queries.append((query, args))
        return []


class MockPool:
    """Mock asyncpg pool."""

    def __init__(self) -> None:
        self._conn = MockConnection()

    def acquire(self) -> AsyncMock:
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=self._conn)
        ctx.__aexit__ = AsyncMock(return_value=False)
        return ctx


@pytest.fixture()
def mock_pool() -> MockPool:
    return MockPool()


@pytest.fixture()
def service(mock_pool: MockPool) -> SyllabusService:
    return SyllabusService(pool=mock_pool)


class TestSyllabusServiceExams:
    @pytest.mark.asyncio
    async def test_list_exams_returns_list(self, service: SyllabusService) -> None:
        result = await service.list_exams()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_list_exams_with_no_pool_returns_empty(self) -> None:
        service = SyllabusService(pool=None)
        result = await service.list_exams()
        assert result == []


class TestSyllabusServiceChapters:
    @pytest.mark.asyncio
    async def test_list_chapters_returns_list(self, service: SyllabusService) -> None:
        result = await service.list_chapters()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_list_chapters_with_no_pool_returns_empty(self) -> None:
        service = SyllabusService(pool=None)
        result = await service.list_chapters()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_chapters_with_exam_filter(self, service: SyllabusService) -> None:
        result = await service.list_chapters(exam_id=uuid4())
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_list_chapters_with_subject_filter(self, service: SyllabusService) -> None:
        result = await service.list_chapters(subject_id=uuid4())
        assert isinstance(result, list)


class TestSyllabusServiceChapterDetail:
    @pytest.mark.asyncio
    async def test_get_chapter_with_topics_returns_none(self, service: SyllabusService) -> None:
        result = await service.get_chapter_with_topics(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_chapter_with_no_pool_returns_none(self) -> None:
        service = SyllabusService(pool=None)
        result = await service.get_chapter_with_topics(uuid4())
        assert result is None
