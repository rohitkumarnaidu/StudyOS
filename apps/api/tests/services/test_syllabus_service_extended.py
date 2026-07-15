"""Extended tests for syllabus service — covering uncovered lines."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from studyos_api.services.syllabus_service import SyllabusService


class FakeRow(dict):
    def __getitem__(self, key):
        return dict.__getitem__(self, key)


class MockConnection:
    def __init__(self) -> None:
        self._queries: list[tuple[str, tuple]] = []
        self._rows: list[FakeRow] = []

    async def fetchrow(self, query: str, *args: object) -> FakeRow | None:
        self._queries.append((query, args))
        return self._rows[0] if self._rows else None

    async def fetch(self, query: str, *args: object) -> list[FakeRow]:
        self._queries.append((query, args))
        return self._rows


class MockPool:
    def __init__(self, rows: list[FakeRow] | None = None) -> None:
        self._conn = MockConnection()
        if rows:
            self._conn._rows = rows

    def acquire(self) -> MagicMock:
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=self._conn)
        ctx.__aexit__ = AsyncMock(return_value=False)
        return ctx


@pytest.mark.unit
class TestSyllabusServiceListSubjects:
    @pytest.mark.asyncio
    async def test_list_subjects_no_pool(self) -> None:
        service = SyllabusService(pool=None)
        result = await service.list_subjects(exam_id=uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_list_subjects_with_pool_empty(self) -> None:
        pool = MockPool(rows=[])
        service = SyllabusService(pool=pool)
        result = await service.list_subjects(exam_id=uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_list_subjects_with_pool_returns_data(self) -> None:
        rows = [
            FakeRow(id=uuid4(), name="Biology", sort_order=1),
            FakeRow(id=uuid4(), name="Physics", sort_order=2),
        ]
        pool = MockPool(rows=rows)
        service = SyllabusService(pool=pool)
        result = await service.list_subjects(exam_id=uuid4())
        assert len(result) == 2
        assert result[0]["name"] == "Biology"
        assert result[1]["name"] == "Physics"

    @pytest.mark.asyncio
    async def test_list_subjects_passes_exam_id(self) -> None:
        pool = MockPool(rows=[])
        service = SyllabusService(pool=pool)
        exam_id = uuid4()
        await service.list_subjects(exam_id=exam_id)
        conn = pool._conn
        assert len(conn._queries) == 1
        query, args = conn._queries[0]
        assert args[0] == exam_id
        assert "exam_profile_id" in query


@pytest.mark.unit
class TestSyllabusServiceListExamsWithData:
    @pytest.mark.asyncio
    async def test_list_exams_returns_data(self) -> None:
        rows = [
            FakeRow(id=uuid4(), code="NEET", title="NEET UG", description="Medical entrance"),
        ]
        pool = MockPool(rows=rows)
        service = SyllabusService(pool=pool)
        result = await service.list_exams()
        assert len(result) == 1
        assert result[0]["code"] == "NEET"


@pytest.mark.unit
class TestSyllabusServiceListChaptersWithData:
    @pytest.mark.asyncio
    async def test_list_chapters_subject_filter_returns_data(self) -> None:
        rows = [
            FakeRow(id=uuid4(), name="Cell Biology", sort_order=1),
        ]
        pool = MockPool(rows=rows)
        service = SyllabusService(pool=pool)
        result = await service.list_chapters(subject_id=uuid4())
        assert len(result) == 1
        assert result[0]["name"] == "Cell Biology"

    @pytest.mark.asyncio
    async def test_list_chapters_exam_filter_returns_data(self) -> None:
        rows = [
            FakeRow(id=uuid4(), name="Chapter 1", sort_order=1),
        ]
        pool = MockPool(rows=rows)
        service = SyllabusService(pool=pool)
        result = await service.list_chapters(exam_id=uuid4())
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_chapters_no_filter_returns_data(self) -> None:
        rows = [
            FakeRow(id=uuid4(), name="General Chapter", sort_order=1),
        ]
        pool = MockPool(rows=rows)
        service = SyllabusService(pool=pool)
        result = await service.list_chapters()
        assert len(result) == 1


@pytest.mark.unit
class TestSyllabusServiceGetChapterWithTopicsWithData:
    @pytest.mark.asyncio
    async def test_get_chapter_with_topics_returns_full_structure(self) -> None:
        chapter_id = uuid4()
        topic_id = uuid4()
        subtopic_id = uuid4()

        chapter_row = FakeRow(id=chapter_id, name="Biology", sort_order=1)
        topic_row = FakeRow(id=topic_id, name="Cells", sort_order=1)
        subtopic_row = FakeRow(id=subtopic_id, name="Cell membrane", sort_order=1, estimated_minutes=30)

        pool = MockPool()
        pool._conn._rows = [chapter_row]
        service = SyllabusService(pool=pool)

        chapter_result = await service.get_chapter_with_topics(chapter_id)
        assert chapter_result is not None
        assert chapter_result["name"] == "Biology"
