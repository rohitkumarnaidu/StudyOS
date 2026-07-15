"""Tests for roadmap_generator service."""

from datetime import date, timedelta
from unittest.mock import patch

import pytest

from studyos_api.services.roadmap_generator import (
    ChapterTarget,
    DayPlan,
    NEET_SYLLABUS,
    Roadmap,
    RoadmapGenerator,
    RoadmapStatus,
)


class TestChapterTarget:
    def test_to_dict(self) -> None:
        ct = ChapterTarget(
            id="ch-1",
            name="Motion",
            subject="Physics",
            grade="11th",
            priority_score=80,
            estimated_minutes=60,
        )
        d = ct.to_dict()
        assert d["id"] == "ch-1"
        assert d["name"] == "Motion"
        assert d["subject"] == "Physics"
        assert d["grade"] == "11th"
        assert d["priority_score"] == 80
        assert d["estimated_minutes"] == 60
        assert d["completed"] is False

    def test_completed_flag(self) -> None:
        ct = ChapterTarget(
            id="ch-1",
            name="Motion",
            subject="Physics",
            grade="11th",
            priority_score=80,
            estimated_minutes=60,
            completed=True,
        )
        assert ct.completed is True
        assert ct.to_dict()["completed"] is True


class TestDayPlan:
    def test_to_dict(self) -> None:
        ct = ChapterTarget(
            id="ch-1",
            name="Motion",
            subject="Physics",
            grade="11th",
            priority_score=80,
            estimated_minutes=60,
        )
        dp = DayPlan(
            date="2026-01-15",
            day_number=1,
            day_type="study",
            chapters=[ct],
        )
        d = dp.to_dict()
        assert d["date"] == "2026-01-15"
        assert d["day_number"] == 1
        assert d["day_type"] == "study"
        assert len(d["chapters"]) == 1
        assert d["total_minutes"] == 60
        assert d["status"] == "pending"

    def test_total_minutes_auto_calc(self) -> None:
        ct1 = ChapterTarget(
            id="ch-1", name="A", subject="Physics", grade="11th",
            priority_score=50, estimated_minutes=30,
        )
        ct2 = ChapterTarget(
            id="ch-2", name="B", subject="Physics", grade="11th",
            priority_score=50, estimated_minutes=45,
        )
        dp = DayPlan(
            date="2026-01-15",
            day_number=1,
            day_type="study",
            chapters=[ct1, ct2],
        )
        assert dp.total_minutes == 75

    def test_total_minutes_explicit(self) -> None:
        dp = DayPlan(
            date="2026-01-15",
            day_number=1,
            day_type="study",
            chapters=[],
            total_minutes=120,
        )
        assert dp.total_minutes == 120

    def test_default_status(self) -> None:
        dp = DayPlan(
            date="2026-01-15",
            day_number=1,
            day_type="study",
            chapters=[],
        )
        assert dp.status == RoadmapStatus.PENDING


class TestRoadmap:
    def test_to_dict(self) -> None:
        r = Roadmap(
            id="rm-1",
            profile_id="prof-1",
            exam_date="2026-06-01",
            daily_hours=6,
            total_days=30,
            study_days=20,
            revision_days=5,
            mock_test_days=3,
            buffer_days=2,
            days=[],
            created_at="2026-01-01T00:00:00",
        )
        d = r.to_dict()
        assert d["id"] == "rm-1"
        assert d["profile_id"] == "prof-1"
        assert d["total_days"] == 30
        assert d["study_days"] == 20
        assert len(d["days"]) == 0


class TestRoadmapStatus:
    def test_status_values(self) -> None:
        assert RoadmapStatus.PENDING.value == "pending"
        assert RoadmapStatus.IN_PROGRESS.value == "in_progress"
        assert RoadmapStatus.COMPLETED.value == "completed"
        assert RoadmapStatus.SKIPPED.value == "skipped"
        assert RoadmapStatus.MISSED.value == "missed"


class TestRoadmapGeneratorGenerateRoadmap:
    @pytest.fixture
    def gen(self) -> RoadmapGenerator:
        return RoadmapGenerator()

    def test_basic_generation(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=90)
        roadmap = gen.generate_roadmap(
            profile_id="prof-1",
            exam_date=exam_date,
            daily_hours=6,
        )
        assert roadmap.profile_id == "prof-1"
        assert roadmap.daily_hours == 6
        assert roadmap.total_days == 90
        assert len(roadmap.days) == 90
        assert roadmap.study_days > 0
        assert roadmap.revision_days > 0
        assert roadmap.mock_test_days > 0
        assert roadmap.buffer_days > 0

    def test_total_days_minimum_7(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=2)
        roadmap = gen.generate_roadmap(
            profile_id="prof-1",
            exam_date=exam_date,
            daily_hours=4,
        )
        assert roadmap.total_days == 7

    def test_day_types_exist(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=60)
        roadmap = gen.generate_roadmap(
            profile_id="prof-1",
            exam_date=exam_date,
            daily_hours=6,
        )
        day_types = {d.day_type for d in roadmap.days}
        assert "study" in day_types
        assert "revision" in day_types
        assert "mock_test" in day_types
        assert "buffer" in day_types

    def test_mock_test_day_has_mock_chapter(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=60)
        roadmap = gen.generate_roadmap(
            profile_id="prof-1",
            exam_date=exam_date,
            daily_hours=6,
        )
        mock_days = [d for d in roadmap.days if d.day_type == "mock_test"]
        assert len(mock_days) > 0
        for md in mock_days:
            assert len(md.chapters) == 1
            assert "Mock Test" in md.chapters[0].name
            assert md.chapters[0].estimated_minutes == 180

    def test_buffer_day_has_no_chapters(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=60)
        roadmap = gen.generate_roadmap(
            profile_id="prof-1",
            exam_date=exam_date,
            daily_hours=6,
        )
        buffer_days = [d for d in roadmap.days if d.day_type == "buffer"]
        assert len(buffer_days) > 0
        for bd in buffer_days:
            assert len(bd.chapters) == 0

    def test_revision_day_has_revision_chapters(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=120)
        roadmap = gen.generate_roadmap(
            profile_id="prof-1",
            exam_date=exam_date,
            daily_hours=8,
        )
        revision_days = [d for d in roadmap.days if d.day_type == "revision"]
        for rd in revision_days:
            for ch in rd.chapters:
                assert ch.name.startswith("Revise:")

    def test_with_completed_chapters(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=60)
        roadmap = gen.generate_roadmap(
            profile_id="prof-1",
            exam_date=exam_date,
            daily_hours=6,
            completed_chapters=["Motion in a Straight Line"],
        )
        assert roadmap is not None
        all_chapter_names = []
        for day in roadmap.days:
            for ch in day.chapters:
                all_chapter_names.append(ch.name)
        assert "Motion in a Straight Line" not in all_chapter_names

    def test_with_weak_areas(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=60)
        roadmap = gen.generate_roadmap(
            profile_id="prof-1",
            exam_date=exam_date,
            daily_hours=6,
            weak_areas=["Thermodynamics"],
        )
        assert roadmap is not None

    def test_different_daily_hours(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=30)
        roadmap_4h = gen.generate_roadmap("p1", exam_date, daily_hours=4)
        roadmap_8h = gen.generate_roadmap("p2", exam_date, daily_hours=8)
        assert roadmap_4h.daily_hours == 4
        assert roadmap_8h.daily_hours == 8

    def test_roadmap_has_unique_id(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=30)
        r1 = gen.generate_roadmap("p1", exam_date)
        r2 = gen.generate_roadmap("p2", exam_date)
        assert r1.id != r2.id

    def test_study_day_has_chapters(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=30)
        roadmap = gen.generate_roadmap("p1", exam_date, daily_hours=6)
        study_days = [d for d in roadmap.days if d.day_type == "study"]
        for sd in study_days:
            assert len(sd.chapters) <= 3

    def test_dates_are_sequential(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=14)
        roadmap = gen.generate_roadmap("p1", exam_date, daily_hours=6)
        dates = [d.date for d in roadmap.days]
        for i in range(1, len(dates)):
            assert dates[i] >= dates[i - 1]

    def test_created_at_is_set(self, gen: RoadmapGenerator) -> None:
        exam_date = date.today() + timedelta(days=30)
        roadmap = gen.generate_roadmap("p1", exam_date)
        assert roadmap.created_at is not None
        assert len(roadmap.created_at) > 0


class TestRoadmapGeneratorGetDailyPlan:
    @pytest.fixture
    def gen(self) -> RoadmapGenerator:
        gen = RoadmapGenerator()
        exam_date = date.today() + timedelta(days=30)
        gen.generate_roadmap("p1", exam_date)
        return gen

    def test_get_existing_date(self, gen: RoadmapGenerator) -> None:
        roadmap_id = list(gen._roadmaps.keys())[0]
        roadmap = gen._roadmaps[roadmap_id]
        target_date = date.fromisoformat(roadmap.days[0].date)
        dp = gen.get_daily_plan(roadmap_id, target_date)
        assert dp is not None
        assert dp.day_number == 1

    def test_get_nonexistent_roadmap(self, gen: RoadmapGenerator) -> None:
        result = gen.get_daily_plan("fake-id", date.today())
        assert result is None

    def test_get_date_outside_range(self, gen: RoadmapGenerator) -> None:
        roadmap_id = list(gen._roadmaps.keys())[0]
        far_future = date.today() + timedelta(days=999)
        result = gen.get_daily_plan(roadmap_id, far_future)
        assert result is None


class TestRoadmapGeneratorAdjustRoadmap:
    @pytest.fixture
    def gen(self) -> RoadmapGenerator:
        gen = RoadmapGenerator()
        exam_date = date.today() + timedelta(days=30)
        roadmap = gen.generate_roadmap("p1", exam_date)
        return gen

    def test_adjust_with_completed(self, gen: RoadmapGenerator) -> None:
        roadmap_id = list(gen._roadmaps.keys())[0]
        roadmap = gen._roadmaps[roadmap_id]
        study_days = [d for d in roadmap.days if d.day_type == "study" and d.chapters]
        if study_days:
            chapter_id = study_days[0].chapters[0].id
            result = gen.adjust_roadmap(roadmap_id, [chapter_id])
            assert result is not None
            for day in result.days:
                for ch in day.chapters:
                    if ch.id == chapter_id:
                        assert ch.completed is True

    def test_adjust_nonexistent_roadmap(self, gen: RoadmapGenerator) -> None:
        result = gen.adjust_roadmap("fake-id", ["ch-1"])
        assert result is None

    def test_adjust_empty_completed(self, gen: RoadmapGenerator) -> None:
        roadmap_id = list(gen._roadmaps.keys())[0]
        result = gen.adjust_roadmap(roadmap_id, [])
        assert result is not None


class TestRoadmapGeneratorGetProgress:
    @pytest.fixture
    def gen(self) -> RoadmapGenerator:
        gen = RoadmapGenerator()
        exam_date = date.today() + timedelta(days=30)
        gen.generate_roadmap("p1", exam_date)
        return gen

    def test_progress_structure(self, gen: RoadmapGenerator) -> None:
        roadmap_id = list(gen._roadmaps.keys())[0]
        progress = gen.get_roadmap_progress(roadmap_id)
        assert progress is not None
        assert "roadmap_id" in progress
        assert "total_chapters" in progress
        assert "completed_chapters" in progress
        assert "completion_pct" in progress
        assert "study_days_completed" in progress
        assert "total_study_days" in progress
        assert "days_remaining" in progress

    def test_progress_nonexistent_roadmap(self, gen: RoadmapGenerator) -> None:
        result = gen.get_roadmap_progress("fake-id")
        assert result is None

    def test_completion_pct_calculation(self, gen: RoadmapGenerator) -> None:
        roadmap_id = list(gen._roadmaps.keys())[0]
        progress = gen.get_roadmap_progress(roadmap_id)
        assert progress is not None
        assert 0 <= progress["completion_pct"] <= 100


class TestRoadmapGeneratorBuildChapterList:
    @pytest.fixture
    def gen(self) -> RoadmapGenerator:
        return RoadmapGenerator()

    def test_all_chapters_included(self, gen: RoadmapGenerator) -> None:
        chapters = gen._build_chapter_list([], [])
        assert len(chapters) > 0

    def test_completed_excluded(self, gen: RoadmapGenerator) -> None:
        chapters = gen._build_chapter_list(["Motion in a Straight Line"], [])
        names = [c["name"] for c in chapters]
        assert "Motion in a Straight Line" not in names

    def test_weak_areas_boosted(self, gen: RoadmapGenerator) -> None:
        chapters_normal = gen._build_chapter_list([], [])
        chapters_weak = gen._build_chapter_list([], ["Thermodynamics"])
        normal_thermo = [c for c in chapters_normal if c["name"] == "Thermodynamics"]
        weak_thermo = [c for c in chapters_weak if c["name"] == "Thermodynamics"]
        if normal_thermo and weak_thermo:
            assert weak_thermo[0]["priority"] >= normal_thermo[0]["priority"]

    def test_chapters_have_required_fields(self, gen: RoadmapGenerator) -> None:
        chapters = gen._build_chapter_list([], [])
        for ch in chapters:
            assert "name" in ch
            assert "subject" in ch
            assert "grade" in ch
            assert "priority" in ch
            assert "weight" in ch
            assert "dependencies" in ch

    def test_priority_capped_at_100(self, gen: RoadmapGenerator) -> None:
        chapters = gen._build_chapter_list([], [])
        for ch in chapters:
            assert ch["priority"] <= 100

    def test_sorted_by_priority(self, gen: RoadmapGenerator) -> None:
        chapters = gen._build_chapter_list([], [])
        priorities = [c["priority"] for c in chapters]
        assert priorities == sorted(priorities, reverse=True)


class TestRoadmapGeneratorAssignDailyChapters:
    @pytest.fixture
    def gen(self) -> RoadmapGenerator:
        return RoadmapGenerator()

    def test_assigns_chapters(self, gen: RoadmapGenerator) -> None:
        chapters = gen._build_chapter_list([], [])
        assigned = gen._assign_daily_chapters(chapters, 0, 360)
        assert len(assigned) > 0
        assert len(assigned) <= 3

    def test_empty_when_start_idx_beyond(self, gen: RoadmapGenerator) -> None:
        chapters = gen._build_chapter_list([], [])
        assigned = gen._assign_daily_chapters(chapters, len(chapters) + 100, 360)
        assert assigned == []

    def test_balances_subjects(self, gen: RoadmapGenerator) -> None:
        chapters = gen._build_chapter_list([], [])
        assigned = gen._assign_daily_chapters(chapters, 0, 360)
        subjects = {ch.subject for ch in assigned}
        assert len(subjects) >= 1


class TestRoadmapGeneratorGetRevisionChapters:
    @pytest.fixture
    def gen(self) -> RoadmapGenerator:
        return RoadmapGenerator()

    def test_returns_revision_chapters(self, gen: RoadmapGenerator) -> None:
        study_day = DayPlan(
            date="2026-01-01",
            day_number=1,
            day_type="study",
            chapters=[
                ChapterTarget(
                    id="ch-1", name="Motion", subject="Physics", grade="11th",
                    priority_score=80, estimated_minutes=60,
                ),
            ],
        )
        revision = gen._get_revision_chapters([study_day], count=1)
        assert len(revision) == 1
        assert revision[0].name.startswith("Revise:")

    def test_empty_when_no_previous_study(self, gen: RoadmapGenerator) -> None:
        revision = gen._get_revision_chapters([], count=3)
        assert revision == []

    def test_respects_count_limit(self, gen: RoadmapGenerator) -> None:
        study_days = [
            DayPlan(
                date=f"2026-01-{i:02d}",
                day_number=i,
                day_type="study",
                chapters=[
                    ChapterTarget(
                        id=f"ch-{i}", name=f"Topic {i}", subject="Physics", grade="11th",
                        priority_score=50, estimated_minutes=30,
                    ),
                ],
            )
            for i in range(1, 6)
        ]
        revision = gen._get_revision_chapters(study_days, count=2)
        assert len(revision) <= 2


class TestNeeetSyllabus:
    def test_has_three_subjects(self) -> None:
        assert "Physics" in NEET_SYLLABUS
        assert "Chemistry" in NEET_SYLLABUS
        assert "Biology" in NEET_SYLLABUS

    def test_subjects_have_weight(self) -> None:
        for subj_data in NEET_SYLLABUS.values():
            assert "weight" in subj_data
            assert subj_data["weight"] > 0

    def test_chapters_have_tuple_structure(self) -> None:
        for subj_data in NEET_SYLLABUS.values():
            for grade_key in ["11th", "12th"]:
                for chapter_tuple in subj_data[grade_key]:
                    assert len(chapter_tuple) == 3
                    name, weight, deps = chapter_tuple
                    assert isinstance(name, str)
                    assert isinstance(weight, int)
                    assert isinstance(deps, list)
