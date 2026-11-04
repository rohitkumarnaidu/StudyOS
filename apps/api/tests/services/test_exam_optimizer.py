"""Tests for exam_optimizer service."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from studyos_api.services.exam_optimizer import ExamOptimizer


class MockAsyncpgRow(dict):
    """Mock asyncpg Row that supports dict-like access."""

    def __getitem__(self, key: str) -> object:
        return dict.get(self, key)


class MockAsyncContextManager:
    """Mock async context manager for pool.acquire()."""

    def __init__(self, conn: AsyncMock) -> None:
        self._conn = conn

    async def __aenter__(self) -> AsyncMock:
        return self._conn

    async def __aexit__(self, *args: object) -> None:
        pass


class TestExamOptimizerInit:
    def test_init_with_pool(self) -> None:
        pool = AsyncMock()
        opt = ExamOptimizer(pool=pool)
        assert opt._pool is pool

    def test_init_without_pool(self) -> None:
        opt = ExamOptimizer(pool=None)
        assert opt._pool is None


class TestExamOptimizerOptimizePlan:
    @pytest.mark.asyncio
    async def test_returns_error_when_no_pool(self) -> None:
        opt = ExamOptimizer(pool=None)
        result = await opt.optimize_plan(uuid4(), date.today() + timedelta(days=30))
        assert result["error"] == "Database not available"

    @pytest.mark.asyncio
    async def test_returns_error_when_exam_passed(self) -> None:
        pool = AsyncMock()
        opt = ExamOptimizer(pool=pool)
        result = await opt.optimize_plan(uuid4(), date.today() - timedelta(days=1))
        assert result["error"] == "Exam date has passed"

    @pytest.mark.asyncio
    async def test_returns_error_when_exam_today(self) -> None:
        pool = AsyncMock()
        opt = ExamOptimizer(pool=pool)
        result = await opt.optimize_plan(uuid4(), date.today())
        assert result["error"] == "Exam date has passed"

    @pytest.mark.asyncio
    async def test_optimize_plan_success(self) -> None:
        conn = AsyncMock()
        subject_row = MockAsyncpgRow(
            {
                "id": uuid4(),
                "name": "Physics",
                "chapter_count": 10,
            }
        )
        conn.fetch.return_value = [subject_row]

        chapter_row = MockAsyncpgRow(
            {
                "id": uuid4(),
                "name": "Motion",
                "weightage": 5.0,
                "total_subtopics": 10,
                "completed_subtopics": 3,
            }
        )
        conn.fetch.side_effect = [[subject_row], [chapter_row]]

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        opt = ExamOptimizer(pool=pool)
        profile_id = uuid4()
        exam_date = date.today() + timedelta(days=45)
        result = await opt.optimize_plan(profile_id, exam_date)

        assert "error" not in result
        assert result["exam_date"] == exam_date.isoformat()
        assert result["days_remaining"] == 45
        assert "phase" in result
        assert "subject_analysis" in result
        assert "recommendations" in result
        assert "daily_target_hours" in result
        assert "weekly_milestones" in result

    @pytest.mark.asyncio
    async def test_optimize_plan_multiple_subjects(self) -> None:
        conn = AsyncMock()
        subjects = [
            MockAsyncpgRow({"id": uuid4(), "name": "Physics", "chapter_count": 10}),
            MockAsyncpgRow({"id": uuid4(), "name": "Chemistry", "chapter_count": 8}),
            MockAsyncpgRow({"id": uuid4(), "name": "Biology", "chapter_count": 12}),
        ]

        chapter_rows = [
            MockAsyncpgRow(
                {
                    "id": uuid4(),
                    "name": "Motion",
                    "weightage": 5.0,
                    "total_subtopics": 10,
                    "completed_subtopics": 3,
                }
            ),
        ]

        conn.fetch.side_effect = [subjects] + [chapter_rows] * 3

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        opt = ExamOptimizer(pool=pool)
        result = await opt.optimize_plan(uuid4(), date.today() + timedelta(days=60))

        assert len(result["subject_analysis"]) == 3


class TestExamOptimizerAnalyzeSubject:
    @pytest.mark.asyncio
    async def test_analyze_subject_weak_chapters(self) -> None:
        conn = AsyncMock()
        chapter_rows = [
            MockAsyncpgRow(
                {
                    "id": uuid4(),
                    "name": "Motion",
                    "weightage": 5.0,
                    "total_subtopics": 10,
                    "completed_subtopics": 2,
                }
            ),
            MockAsyncpgRow(
                {
                    "id": uuid4(),
                    "name": "Thermodynamics",
                    "weightage": 4.0,
                    "total_subtopics": 8,
                    "completed_subtopics": 7,
                }
            ),
        ]
        conn.fetch.return_value = chapter_rows

        opt = ExamOptimizer(pool=None)
        result = await opt._analyze_subject(conn, uuid4(), uuid4())

        assert len(result["weak_chapters"]) == 1
        assert len(result["strong_chapters"]) == 1
        assert result["total_chapters"] == 2
        assert result["total_subtopics"] == 18
        assert result["completed_subtopics"] == 9

    @pytest.mark.asyncio
    async def test_analyze_subject_no_chapters(self) -> None:
        conn = AsyncMock()
        conn.fetch.return_value = []

        opt = ExamOptimizer(pool=None)
        result = await opt._analyze_subject(conn, uuid4(), uuid4())

        assert result["subject_name"] == "Unknown"
        assert result["total_chapters"] == 0
        assert result["completion_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_analyze_subject_completion_rate(self) -> None:
        conn = AsyncMock()
        chapter_rows = [
            MockAsyncpgRow(
                {
                    "id": uuid4(),
                    "name": "Test",
                    "weightage": 3.0,
                    "total_subtopics": 20,
                    "completed_subtopics": 15,
                }
            ),
        ]
        conn.fetch.return_value = chapter_rows

        opt = ExamOptimizer(pool=None)
        result = await opt._analyze_subject(conn, uuid4(), uuid4())

        assert abs(result["completion_rate"] - 0.75) < 0.01

    @pytest.mark.asyncio
    async def test_analyze_subject_zero_subtopics(self) -> None:
        conn = AsyncMock()
        chapter_rows = [
            MockAsyncpgRow(
                {
                    "id": uuid4(),
                    "name": "Empty",
                    "weightage": 1.0,
                    "total_subtopics": 0,
                    "completed_subtopics": 0,
                }
            ),
        ]
        conn.fetch.return_value = chapter_rows

        opt = ExamOptimizer(pool=None)
        result = await opt._analyze_subject(conn, uuid4(), uuid4())

        assert result["completion_rate"] == 0.0
        assert len(result["weak_chapters"]) == 1

    @pytest.mark.asyncio
    async def test_analyze_subject_null_values(self) -> None:
        conn = AsyncMock()
        chapter_rows = [
            MockAsyncpgRow(
                {
                    "id": uuid4(),
                    "name": "Test",
                    "weightage": None,
                    "total_subtopics": None,
                    "completed_subtopics": None,
                }
            ),
        ]
        conn.fetch.return_value = chapter_rows

        opt = ExamOptimizer(pool=None)
        result = await opt._analyze_subject(conn, uuid4(), uuid4())

        assert result["total_subtopics"] == 0
        assert result["completed_subtopics"] == 0


class TestExamOptimizerDeterminePhase:
    def test_crash_phase(self) -> None:
        opt = ExamOptimizer(pool=None)
        assert opt._determine_phase(1) == "crash"
        assert opt._determine_phase(30) == "crash"

    def test_intensive_phase(self) -> None:
        opt = ExamOptimizer(pool=None)
        assert opt._determine_phase(31) == "intensive"
        assert opt._determine_phase(60) == "intensive"

    def test_focused_phase(self) -> None:
        opt = ExamOptimizer(pool=None)
        assert opt._determine_phase(61) == "focused"
        assert opt._determine_phase(90) == "focused"

    def test_foundational_phase(self) -> None:
        opt = ExamOptimizer(pool=None)
        assert opt._determine_phase(91) == "foundational"
        assert opt._determine_phase(365) == "foundational"


class TestExamOptimizerGenerateRecommendations:
    def test_priority_focus_recommendation(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"subject_name": "Physics", "completion_rate": 0.2, "weak_chapters": []},
        ]
        recs = opt._generate_recommendations(subjects, "foundational", 120)
        assert len(recs) >= 1
        assert recs[0]["type"] == "priority_focus"
        assert recs[0]["priority"] == "critical"

    def test_accelerate_recommendation(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"subject_name": "Chemistry", "completion_rate": 0.5, "weak_chapters": []},
        ]
        recs = opt._generate_recommendations(subjects, "foundational", 120)
        assert any(r["type"] == "accelerate" for r in recs)

    def test_crash_phase_strategy(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"subject_name": "Physics", "completion_rate": 0.8, "weak_chapters": []},
        ]
        recs = opt._generate_recommendations(subjects, "crash", 15)
        assert any(r["type"] == "strategy" for r in recs)
        strategy = [r for r in recs if r["type"] == "strategy"][0]
        assert "Crash phase" in strategy["message"]

    def test_intensive_phase_strategy(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"subject_name": "Physics", "completion_rate": 0.8, "weak_chapters": []},
        ]
        recs = opt._generate_recommendations(subjects, "intensive", 45)
        strategy = [r for r in recs if r["type"] == "strategy"][0]
        assert "Intensive phase" in strategy["message"]

    def test_warning_many_weak_chapters(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {
                "subject_name": "Physics",
                "completion_rate": 0.3,
                "weak_chapters": [
                    {
                        "chapter_id": str(uuid4()),
                        "chapter_name": f"Ch{i}",
                        "weightage": 5.0,
                        "completion_rate": 0.2,
                    }
                    for i in range(6)
                ],
            },
            {
                "subject_name": "Chemistry",
                "completion_rate": 0.3,
                "weak_chapters": [
                    {
                        "chapter_id": str(uuid4()),
                        "chapter_name": f"Ch{i}",
                        "weightage": 4.0,
                        "completion_rate": 0.1,
                    }
                    for i in range(6)
                ],
            },
        ]
        recs = opt._generate_recommendations(subjects, "focused", 75)
        assert any(r["type"] == "warning" for r in recs)

    def test_no_recommendations_for_good_progress(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"subject_name": "Physics", "completion_rate": 0.9, "weak_chapters": []},
            {"subject_name": "Chemistry", "completion_rate": 0.85, "weak_chapters": []},
        ]
        recs = opt._generate_recommendations(subjects, "foundational", 200)
        phase_recs = [r for r in recs if r["type"] in ("priority_focus", "accelerate")]
        assert len(phase_recs) == 0

    def test_empty_subjects(self) -> None:
        opt = ExamOptimizer(pool=None)
        recs = opt._generate_recommendations([], "foundational", 100)
        assert recs == []


class TestExamOptimizerComputeDailyHours:
    def test_crash_phase(self) -> None:
        opt = ExamOptimizer(pool=None)
        hours = opt._compute_daily_hours("crash", [])
        assert hours == 12.0

    def test_intensive_phase(self) -> None:
        opt = ExamOptimizer(pool=None)
        hours = opt._compute_daily_hours("intensive", [])
        assert hours == 10.0

    def test_focused_phase(self) -> None:
        opt = ExamOptimizer(pool=None)
        hours = opt._compute_daily_hours("focused", [])
        assert hours == 8.0

    def test_foundational_low_completion(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"completion_rate": 0.2},
            {"completion_rate": 0.1},
        ]
        hours = opt._compute_daily_hours("foundational", subjects)
        assert hours == 8.0

    def test_foundational_medium_completion(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"completion_rate": 0.4},
            {"completion_rate": 0.5},
        ]
        hours = opt._compute_daily_hours("foundational", subjects)
        assert hours == 6.0

    def test_foundational_high_completion(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"completion_rate": 0.8},
            {"completion_rate": 0.9},
        ]
        hours = opt._compute_daily_hours("foundational", subjects)
        assert hours == 4.0

    def test_empty_subjects(self) -> None:
        opt = ExamOptimizer(pool=None)
        hours = opt._compute_daily_hours("foundational", [])
        assert hours == 8.0


class TestExamOptimizerComputeWeeklyMilestones:
    def test_basic_milestones(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"total_chapters": 10, "completion_rate": 0.3, "subject_name": "Physics"},
        ]
        milestones = opt._compute_weekly_milestones("focused", 70, subjects)
        assert len(milestones) == 10
        assert milestones[0]["week"] == 1
        assert milestones[0]["target_chapters"] == 1

    def test_caps_at_12_weeks(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"total_chapters": 30, "completion_rate": 0.3, "subject_name": "Physics"},
        ]
        milestones = opt._compute_weekly_milestones("foundational", 200, subjects)
        assert len(milestones) == 12

    def test_minimum_one_week(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"total_chapters": 5, "completion_rate": 0.3, "subject_name": "Physics"},
        ]
        milestones = opt._compute_weekly_milestones("crash", 3, subjects)
        assert len(milestones) >= 1

    def test_target_completion_increases(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"total_chapters": 10, "completion_rate": 0.3, "subject_name": "Physics"},
        ]
        milestones = opt._compute_weekly_milestones("focused", 70, subjects)
        for i in range(1, len(milestones)):
            assert (
                milestones[i]["target_completion_pct"] >= milestones[i - 1]["target_completion_pct"]
            )

    def test_target_completion_capped_at_100(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"total_chapters": 5, "completion_rate": 0.3, "subject_name": "Physics"},
        ]
        milestones = opt._compute_weekly_milestones("focused", 70, subjects)
        for m in milestones:
            assert m["target_completion_pct"] <= 100.0


class TestExamOptimizerGetWeekFocus:
    def test_crash_always_revision(self) -> None:
        opt = ExamOptimizer(pool=None)
        assert opt._get_week_focus("crash", 1, []) == "Revision + mock tests"
        assert opt._get_week_focus("crash", 5, []) == "Revision + mock tests"

    def test_intensive_early_weeks(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [{"subject_name": "Physics", "completion_rate": 0.3}]
        assert opt._get_week_focus("intensive", 1, subjects) == "Complete weak chapters"
        assert opt._get_week_focus("intensive", 2, subjects) == "Complete weak chapters"

    def test_intensive_later_weeks(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [{"subject_name": "Physics", "completion_rate": 0.3}]
        assert opt._get_week_focus("intensive", 3, subjects) == "Mock tests + revision"

    def test_focused_weak_subjects(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"subject_name": "Physics", "completion_rate": 0.3},
            {"subject_name": "Chemistry", "completion_rate": 0.4},
        ]
        assert opt._get_week_focus("focused", 1, subjects) == "Focus on Physics"
        assert opt._get_week_focus("focused", 2, subjects) == "Focus on Chemistry"

    def test_focused_balanced(self) -> None:
        opt = ExamOptimizer(pool=None)
        subjects = [
            {"subject_name": "Physics", "completion_rate": 0.8},
        ]
        assert opt._get_week_focus("focused", 1, subjects) == "Balanced progress"

    def test_foundational(self) -> None:
        opt = ExamOptimizer(pool=None)
        assert opt._get_week_focus("foundational", 1, []) == "Foundation building"
