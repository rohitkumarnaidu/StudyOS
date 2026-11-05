"""Extended tests for progress controller — covering uncovered error paths."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from studyos_api.controllers.progress_controller import ProgressController


@pytest.mark.unit
class TestProgressControllerErrorPaths:
    @pytest.fixture
    def mock_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def controller(self, mock_service: AsyncMock) -> ProgressController:
        return ProgressController(service=mock_service)

    @pytest.mark.asyncio
    async def test_get_chapter_progress_failure(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_chapter_progress.return_value = None
        profile_id = uuid4()
        chapter_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await controller.get_chapter_progress(mock_request, profile_id, chapter_id)

        assert exc_info.value.status_code == 500
        assert "Failed to fetch chapter progress" in exc_info.value.detail
        mock_service.get_chapter_progress.assert_called_once_with(profile_id, chapter_id)

    @pytest.mark.asyncio
    async def test_get_chapter_progress_empty_dict_failure(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_chapter_progress.return_value = {}
        profile_id = uuid4()
        chapter_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await controller.get_chapter_progress(mock_request, profile_id, chapter_id)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_subject_progress_failure(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_subject_progress.return_value = None
        profile_id = uuid4()
        subject_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await controller.get_subject_progress(mock_request, profile_id, subject_id)

        assert exc_info.value.status_code == 500
        assert "Failed to fetch subject progress" in exc_info.value.detail
        mock_service.get_subject_progress.assert_called_once_with(profile_id, subject_id)

    @pytest.mark.asyncio
    async def test_get_subject_progress_empty_dict_failure(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_subject_progress.return_value = {}
        profile_id = uuid4()
        subject_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await controller.get_subject_progress(mock_request, profile_id, subject_id)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_exam_progress_failure(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_exam_progress.return_value = None
        profile_id = uuid4()
        exam_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await controller.get_exam_progress(mock_request, profile_id, exam_id)

        assert exc_info.value.status_code == 500
        assert "Failed to fetch exam progress" in exc_info.value.detail
        mock_service.get_exam_progress.assert_called_once_with(profile_id, exam_id)

    @pytest.mark.asyncio
    async def test_get_exam_progress_empty_dict_failure(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_exam_progress.return_value = {}
        profile_id = uuid4()
        exam_id = uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await controller.get_exam_progress(mock_request, profile_id, exam_id)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_get_chapter_progress_success_includes_meta(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_chapter_progress.return_value = {"completed": 3, "total": 10}
        profile_id = uuid4()
        chapter_id = uuid4()

        result = await controller.get_chapter_progress(mock_request, profile_id, chapter_id)

        assert "data" in result
        assert "meta" in result
        assert result["data"]["completed"] == 3

    @pytest.mark.asyncio
    async def test_get_subject_progress_success_includes_meta(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_subject_progress.return_value = {"progress_pct": 60.0}
        profile_id = uuid4()
        subject_id = uuid4()

        result = await controller.get_subject_progress(mock_request, profile_id, subject_id)

        assert "meta" in result
        assert result["data"]["progress_pct"] == 60.0

    @pytest.mark.asyncio
    async def test_get_exam_progress_success_includes_meta(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_exam_progress.return_value = {"progress_pct": 45.0}
        profile_id = uuid4()
        exam_id = uuid4()

        result = await controller.get_exam_progress(mock_request, profile_id, exam_id)

        assert "meta" in result
        assert result["data"]["progress_pct"] == 45.0
