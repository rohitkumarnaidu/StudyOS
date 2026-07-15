"""Tests for AI generation Celery tasks."""

from unittest.mock import patch

import pytest

from studyos_api.tasks.ai_tasks import (
    generate_quiz_from_notes,
    generate_roadmap,
    generate_revision_pack,
    generate_study_plan,
    summarize_document,
)


class TestGenerateRoadmap:
    def test_generate_roadmap_success(self) -> None:
        result = generate_roadmap(
            profile_id="user-123",
            exam_type="NEET",
            subjects=["Physics", "Chemistry", "Biology"],
            target_date="2026-12-31",
            difficulty="hard",
        )
        assert result["profile_id"] == "user-123"
        assert result["exam_type"] == "NEET"
        assert result["subjects"] == ["Physics", "Chemistry", "Biology"]
        assert result["target_date"] == "2026-12-31"
        assert result["difficulty"] == "hard"
        assert result["status"] == "completed"
        assert result["items_generated"] == 15

    def test_generate_roadmap_default_values(self) -> None:
        result = generate_roadmap(
            profile_id="user-456",
            exam_type="JEE",
            subjects=["Math"],
        )
        assert result["target_date"] is None
        assert result["difficulty"] == "medium"

    def test_generate_roadmap_retry_on_failure(self) -> None:
        task = generate_roadmap
        assert task.max_retries == 3
        assert task.default_retry_delay == 60
        assert task.queue == "ai"


class TestGenerateRevisionPack:
    def test_generate_revision_pack_success(self) -> None:
        result = generate_revision_pack(
            profile_id="user-123",
            pack_type="active_recall",
            subject="Biology",
            max_items=15,
        )
        assert result["profile_id"] == "user-123"
        assert result["pack_type"] == "active_recall"
        assert result["subject"] == "Biology"
        assert result["items_count"] == 15
        assert result["status"] == "completed"

    def test_generate_revision_pack_default_values(self) -> None:
        result = generate_revision_pack(profile_id="user-789")
        assert result["pack_type"] == "spaced_repetition"
        assert result["subject"] is None
        assert result["items_count"] == 20

    def test_generate_revision_pack_caps_max_items(self) -> None:
        result = generate_revision_pack(
            profile_id="user-123",
            max_items=50,
        )
        assert result["items_count"] == 20

    def test_generate_revision_pack_retry_config(self) -> None:
        task = generate_revision_pack
        assert task.max_retries == 2
        assert task.default_retry_delay == 30


class TestGenerateQuizFromNotes:
    def test_generate_quiz_from_notes_success(self) -> None:
        result = generate_quiz_from_notes(
            profile_id="user-123",
            note_ids=["note-1", "note-2", "note-3"],
            question_count=15,
            difficulty="hard",
        )
        assert result["profile_id"] == "user-123"
        assert result["note_count"] == 3
        assert result["question_count"] == 15
        assert result["difficulty"] == "hard"
        assert result["status"] == "completed"

    def test_generate_quiz_from_notes_default_values(self) -> None:
        result = generate_quiz_from_notes(
            profile_id="user-456",
            note_ids=["note-1"],
        )
        assert result["question_count"] == 10
        assert result["difficulty"] == "medium"

    def test_generate_quiz_from_notes_retry_config(self) -> None:
        task = generate_quiz_from_notes
        assert task.max_retries == 3
        assert task.default_retry_delay == 45


class TestSummarizeDocument:
    def test_summarize_document_success(self) -> None:
        result = summarize_document(
            profile_id="user-123",
            document_id="doc-456",
            summary_type="detailed",
        )
        assert result["profile_id"] == "user-123"
        assert result["document_id"] == "doc-456"
        assert result["summary_type"] == "detailed"
        assert result["status"] == "completed"

    def test_summarize_document_default_values(self) -> None:
        result = summarize_document(
            profile_id="user-789",
            document_id="doc-001",
        )
        assert result["summary_type"] == "brief"

    def test_summarize_document_retry_config(self) -> None:
        task = summarize_document
        assert task.max_retries == 2
        assert task.default_retry_delay == 120


class TestGenerateStudyPlan:
    def test_generate_study_plan_success(self) -> None:
        result = generate_study_plan(
            profile_id="user-123",
            days=60,
            hours_per_day=6.0,
            focus_areas=["Physics", "Organic Chemistry"],
        )
        assert result["profile_id"] == "user-123"
        assert result["days"] == 60
        assert result["hours_per_day"] == 6.0
        assert result["focus_areas"] == ["Physics", "Organic Chemistry"]
        assert result["status"] == "completed"
        assert result["total_sessions"] == 180

    def test_generate_study_plan_default_values(self) -> None:
        result = generate_study_plan(profile_id="user-456")
        assert result["days"] == 30
        assert result["hours_per_day"] == 4.0
        assert result["focus_areas"] == []
        assert result["total_sessions"] == 90

    def test_generate_study_plan_retry_config(self) -> None:
        task = generate_study_plan
        assert task.max_retries == 3
        assert task.default_retry_delay == 60
