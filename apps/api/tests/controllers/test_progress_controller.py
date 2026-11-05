"""Tests for progress controller."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from studyos_api.controllers.progress_controller import ProgressController


class TestProgressController:
    @pytest.fixture
    def mock_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def controller(self, mock_service: AsyncMock) -> ProgressController:
        return ProgressController(service=mock_service)

    @pytest.mark.asyncio
    async def test_toggle_subtopic_success(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.toggle_subtopic_completion.return_value = {
            "id": uuid4(),
            "subtopic_id": uuid4(),
            "completed_at": "2024-01-01",
        }
        profile_id = uuid4()
        subtopic_id = uuid4()

        result = await controller.toggle_subtopic(mock_request, profile_id, subtopic_id)

        assert "data" in result
        mock_service.toggle_subtopic_completion.assert_called_once_with(profile_id, subtopic_id)

    @pytest.mark.asyncio
    async def test_toggle_subtopic_failure(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.toggle_subtopic_completion.return_value = {}
        profile_id = uuid4()
        subtopic_id = uuid4()

        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            await controller.toggle_subtopic(mock_request, profile_id, subtopic_id)

    @pytest.mark.asyncio
    async def test_get_chapter_progress_success(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_chapter_progress.return_value = {"completed": 5, "total": 10}
        profile_id = uuid4()
        chapter_id = uuid4()

        result = await controller.get_chapter_progress(mock_request, profile_id, chapter_id)

        assert "data" in result
        assert result["data"]["completed"] == 5

    @pytest.mark.asyncio
    async def test_get_subject_progress_success(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_subject_progress.return_value = {"progress_pct": 75.0}
        profile_id = uuid4()
        subject_id = uuid4()

        result = await controller.get_subject_progress(mock_request, profile_id, subject_id)

        assert "data" in result

    @pytest.mark.asyncio
    async def test_get_exam_progress_success(
        self, controller: ProgressController, mock_service: AsyncMock
    ) -> None:
        mock_request = MagicMock()
        mock_service.get_exam_progress.return_value = {"progress_pct": 50.0}
        profile_id = uuid4()
        exam_id = uuid4()

        result = await controller.get_exam_progress(mock_request, profile_id, exam_id)

        assert "data" in result
