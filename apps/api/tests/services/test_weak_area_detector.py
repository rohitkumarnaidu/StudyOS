"""Tests for weak_area_detector service."""

from datetime import UTC, datetime, timedelta

import pytest

from studyos_api.services.weak_area_detector import (
    MIN_ATTEMPTS_FOR_ANALYSIS,
    RECENCY_HALF_LIFE,
    SUBJECT_WEIGHTS,
    QuizSessionResult,
    TopicPerformance,
    WeakAreaDetector,
    WeakAreaReport,
    _calculate_weakness_score,
    _recency_factor,
)


class TestConstants:
    def test_recency_half_life(self) -> None:
        assert RECENCY_HALF_LIFE == 30.0

    def test_subject_weights(self) -> None:
        assert SUBJECT_WEIGHTS["physics"] == 1.2
        assert SUBJECT_WEIGHTS["chemistry"] == 1.1
        assert SUBJECT_WEIGHTS["biology"] == 1.0

    def test_min_attempts(self) -> None:
        assert MIN_ATTEMPTS_FOR_ANALYSIS == 3


class TestRecencyFactor:
    def test_recent_attempt_high_factor(self) -> None:
        now = datetime.now(UTC)
        yesterday = (now - timedelta(days=1)).isoformat()
        factor = _recency_factor(yesterday, now)
        assert factor > 0.5

    def test_old_attempt_low_factor(self) -> None:
        now = datetime.now(UTC)
        old = (now - timedelta(days=90)).isoformat()
        factor = _recency_factor(old, now)
        assert factor < 0.5

    def test_empty_timestamp(self) -> None:
        factor = _recency_factor("")
        assert factor == 0.5

    def test_none_timestamp(self) -> None:
        factor = _recency_factor(None)  # type: ignore[arg-type]
        assert factor == 0.5

    def test_invalid_timestamp(self) -> None:
        factor = _recency_factor("not-a-date")
        assert factor == 0.5

    def test_half_life_decay(self) -> None:
        now = datetime.now(UTC)
        thirty_days_ago = (now - timedelta(days=30)).isoformat()
        factor = _recency_factor(thirty_days_ago, now)
        assert abs(factor - 0.5) < 0.01

    def test_very_recent_is_near_one(self) -> None:
        now = datetime.now(UTC)
        factor = _recency_factor(now.isoformat(), now)
        assert factor > 0.99

    def test_returns_in_range(self) -> None:
        now = datetime.now(UTC)
        for days in [0, 1, 7, 30, 60, 180]:
            ts = (now - timedelta(days=days)).isoformat()
            factor = _recency_factor(ts, now)
            assert 0 < factor <= 1.0


class TestCalculateWeaknessScore:
    def test_perfect_accuracy_zero_weakness(self) -> None:
        score = _calculate_weakness_score(
            accuracy=1.0,
            weight=1.0,
            recency=1.0,
            total_attempts=10,
        )
        assert score == 0.0

    def test_zero_accuracy_high_weakness(self) -> None:
        score = _calculate_weakness_score(
            accuracy=0.0,
            weight=1.0,
            recency=1.0,
            total_attempts=10,
        )
        assert score > 0.5

    def test_high_attempts_increases_confidence(self) -> None:
        score_low = _calculate_weakness_score(
            accuracy=0.3, weight=1.0, recency=1.0, total_attempts=3,
        )
        score_high = _calculate_weakness_score(
            accuracy=0.3, weight=1.0, recency=1.0, total_attempts=30,
        )
        assert score_high > score_low

    def test_subject_weight_impact(self) -> None:
        score_physics = _calculate_weakness_score(
            accuracy=0.5, weight=1.2, recency=1.0, total_attempts=5,
        )
        score_biology = _calculate_weakness_score(
            accuracy=0.5, weight=1.0, recency=1.0, total_attempts=5,
        )
        assert score_physics > score_biology

    def test_recency_impact(self) -> None:
        score_recent = _calculate_weakness_score(
            accuracy=0.4, weight=1.0, recency=0.9, total_attempts=5,
        )
        score_old = _calculate_weakness_score(
            accuracy=0.4, weight=1.0, recency=0.2, total_attempts=5,
        )
        assert score_recent > score_old

    def test_score_capped_at_1(self) -> None:
        score = _calculate_weakness_score(
            accuracy=0.0, weight=5.0, recency=2.0, total_attempts=100,
        )
        assert score <= 1.0

    def test_rounded_to_4_decimals(self) -> None:
        score = _calculate_weakness_score(
            accuracy=0.333, weight=1.1, recency=0.77, total_attempts=7,
        )
        assert len(str(score).split(".")[-1]) <= 4


class TestTopicPerformance:
    def test_accuracy_property(self) -> None:
        tp = TopicPerformance(
            topic="Test", chapter_id="ch1", subject="physics",
            total_attempts=10, correct_attempts=7,
        )
        assert tp.accuracy == 0.7

    def test_accuracy_zero_attempts(self) -> None:
        tp = TopicPerformance(
            topic="Test", chapter_id="ch1", subject="physics",
        )
        assert tp.accuracy == 0.0

    def test_avg_time_property(self) -> None:
        tp = TopicPerformance(
            topic="Test", chapter_id="ch1", subject="physics",
            total_attempts=5, total_time_seconds=150.0,
        )
        assert tp.avg_time_per_question == 30.0

    def test_avg_time_zero_attempts(self) -> None:
        tp = TopicPerformance(
            topic="Test", chapter_id="ch1", subject="physics",
        )
        assert tp.avg_time_per_question == 0.0

    def test_to_dict(self) -> None:
        tp = TopicPerformance(
            topic="Motion", chapter_id="ch1", subject="physics",
            total_attempts=10, correct_attempts=6,
            total_time_seconds=300.0,
            last_attempt_at="2026-01-15T10:00:00",
            accuracy_history=[0.5, 0.6, 0.7],
        )
        d = tp.to_dict()
        assert d["topic"] == "Motion"
        assert d["accuracy"] == 0.6
        assert d["avg_time_per_question"] == 30.0
        assert d["total_attempts"] == 10
        assert d["correct_attempts"] == 6


class TestQuizSessionResult:
    def test_accuracy_property(self) -> None:
        sr = QuizSessionResult(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Test", subject="physics",
            total_questions=10, correct_answers=7,
            score_percent=70.0, time_taken_seconds=300.0,
            completed_at="2026-01-15T10:00:00",
        )
        assert sr.accuracy == 0.7

    def test_accuracy_zero_questions(self) -> None:
        sr = QuizSessionResult(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Test", subject="physics",
            total_questions=0, correct_answers=0,
            score_percent=0.0, time_taken_seconds=0.0,
            completed_at="2026-01-15T10:00:00",
        )
        assert sr.accuracy == 0.0

    def test_to_dict(self) -> None:
        sr = QuizSessionResult(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=8,
            score_percent=80.0, time_taken_seconds=200.0,
            completed_at="2026-01-15T10:00:00",
        )
        d = sr.to_dict()
        assert d["session_id"] == "s1"
        assert d["accuracy"] == 0.8
        assert d["score_percent"] == 80.0


class TestWeakAreaDetectorInit:
    def test_initialization(self) -> None:
        detector = WeakAreaDetector()
        assert detector._sessions == {}
        assert detector._profile_sessions == {}
        assert detector._topic_performance == {}


class TestWeakAreaDetectorRecordSession:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        return WeakAreaDetector()

    def test_record_basic_session(self, detector: WeakAreaDetector) -> None:
        result = detector.record_session(
            session_id="s1",
            profile_id="p1",
            chapter_id="ch1",
            topic="Motion",
            subject="physics",
            total_questions=10,
            correct_answers=7,
            score_percent=70.0,
            time_taken_seconds=300.0,
        )
        assert result.session_id == "s1"
        assert result.accuracy == 0.7
        assert "s1" in detector._sessions
        assert "s1" in detector._profile_sessions["p1"]

    def test_record_updates_topic_performance(self, detector: WeakAreaDetector) -> None:
        detector.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=7, score_percent=70.0,
        )
        key = "physics:Motion"
        assert key in detector._topic_performance["p1"]
        perf = detector._topic_performance["p1"][key]
        assert perf.total_attempts == 10
        assert perf.correct_attempts == 7

    def test_record_multiple_sessions_same_topic(self, detector: WeakAreaDetector) -> None:
        detector.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=7, score_percent=70.0,
        )
        detector.record_session(
            session_id="s2", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=5, score_percent=50.0,
        )
        key = "physics:Motion"
        perf = detector._topic_performance["p1"][key]
        assert perf.total_attempts == 20
        assert perf.correct_attempts == 12
        assert len(perf.accuracy_history) == 2

    def test_record_with_custom_completed_at(self, detector: WeakAreaDetector) -> None:
        result = detector.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=7, score_percent=70.0,
            completed_at="2025-06-01T10:00:00+00:00",
        )
        assert result.completed_at == "2025-06-01T10:00:00+00:00"

    def test_record_with_question_results(self, detector: WeakAreaDetector) -> None:
        qr = [
            {"is_correct": True, "time_taken": 30.0, "difficulty": 1},
            {"is_correct": False, "time_taken": 60.0, "difficulty": 3},
        ]
        result = detector.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=2, correct_answers=1, score_percent=50.0,
            question_results=qr,
        )
        assert len(result.question_results) == 2

    def test_record_without_topic(self, detector: WeakAreaDetector) -> None:
        detector.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic=None, subject=None,
            total_questions=10, correct_answers=5, score_percent=50.0,
        )
        assert "s1" in detector._sessions
        assert len(detector._topic_performance.get("p1", {})) == 0


class TestWeakAreaDetectorAnalyzeSession:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        det = WeakAreaDetector()
        det.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=7, score_percent=70.0,
            time_taken_seconds=300.0,
        )
        return det

    def test_analyze_existing_session(self, detector: WeakAreaDetector) -> None:
        analysis = detector.analyze_session("s1")
        assert analysis["session_id"] == "s1"
        assert analysis["total_questions"] == 10
        assert analysis["correct"] == 7
        assert analysis["incorrect"] == 3
        assert analysis["accuracy"] == 0.7

    def test_analyze_nonexistent_session(self, detector: WeakAreaDetector) -> None:
        analysis = detector.analyze_session("nonexistent")
        assert "error" in analysis
        assert analysis["error"] == "Session not found"

    def test_analyze_with_question_results(self, detector: WeakAreaDetector) -> None:
        qr = [
            {"is_correct": True, "time_taken": 20.0, "difficulty": 1},
            {"is_correct": True, "time_taken": 25.0, "difficulty": 1},
            {"is_correct": False, "time_taken": 60.0, "difficulty": 3},
            {"is_correct": False, "time_taken": 45.0, "difficulty": 2},
        ]
        detector.record_session(
            session_id="s2", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=4, correct_answers=2, score_percent=50.0,
            time_taken_seconds=150.0,
            question_results=qr,
        )
        analysis = detector.analyze_session("s2")
        assert "avg_time_correct" in analysis
        assert "avg_time_incorrect" in analysis
        assert "by_difficulty" in analysis
        assert analysis["by_difficulty"]["1"]["accuracy"] == 1.0
        assert analysis["by_difficulty"]["2"]["accuracy"] == 0.0
        assert analysis["by_difficulty"]["3"]["accuracy"] == 0.0

    def test_analyze_without_question_results(self, detector: WeakAreaDetector) -> None:
        analysis = detector.analyze_session("s1")
        assert "avg_time_correct" not in analysis
        assert "by_difficulty" not in analysis


class TestWeakAreaDetectorGetWeakAreas:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        det = WeakAreaDetector()
        now = datetime.now(UTC)
        for i in range(5):
            det.record_session(
                session_id=f"s{i}", profile_id="p1", chapter_id="ch1",
                topic="Motion", subject="physics",
                total_questions=10, correct_answers=3, score_percent=30.0,
                completed_at=(now - timedelta(days=i)).isoformat(),
            )
        for i in range(5, 10):
            det.record_session(
                session_id=f"s{i}", profile_id="p1", chapter_id="ch2",
                topic="Thermodynamics", subject="physics",
                total_questions=10, correct_answers=8, score_percent=80.0,
                completed_at=(now - timedelta(days=i - 5)).isoformat(),
            )
        return det

    def test_returns_weak_areas(self, detector: WeakAreaDetector) -> None:
        weak = detector.get_weak_areas("p1")
        assert len(weak) > 0

    def test_sorted_by_weakness_score(self, detector: WeakAreaDetector) -> None:
        weak = detector.get_weak_areas("p1")
        scores = [w["weakness_score"] for w in weak]
        assert scores == sorted(scores, reverse=True)

    def test_respects_limit(self, detector: WeakAreaDetector) -> None:
        weak = detector.get_weak_areas("p1", limit=1)
        assert len(weak) == 1

    def test_weak_area_has_required_fields(self, detector: WeakAreaDetector) -> None:
        weak = detector.get_weak_areas("p1")
        for area in weak:
            assert "topic" in area
            assert "subject" in area
            assert "accuracy" in area
            assert "weakness_score" in area
            assert "severity" in area
            assert "total_attempts" in area

    def test_severity_levels(self, detector: WeakAreaDetector) -> None:
        weak = detector.get_weak_areas("p1")
        severities = {w["severity"] for w in weak}
        for sev in severities:
            assert sev in ("critical", "high", "moderate", "low")

    def test_no_sessions_returns_empty(self) -> None:
        det = WeakAreaDetector()
        weak = det.get_weak_areas("nonexistent")
        assert weak == []

    def test_below_min_attempts_excluded(self, detector: WeakAreaDetector) -> None:
        detector.record_session(
            session_id="s_new", profile_id="p1", chapter_id="ch3",
            topic="New Topic", subject="chemistry",
            total_questions=2, correct_answers=1, score_percent=50.0,
        )
        weak = detector.get_weak_areas("p1")
        topics = [w["topic"] for w in weak]
        assert "New Topic" not in topics


class TestWeakAreaDetectorGetSubjectBreakdown:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        det = WeakAreaDetector()
        now = datetime.now(UTC)
        for i in range(6):
            det.record_session(
                session_id=f"s{i}", profile_id="p1", chapter_id="ch1",
                topic="Motion", subject="physics",
                total_questions=10, correct_answers=5 + i, score_percent=50.0 + i * 5,
                completed_at=(now - timedelta(days=i)).isoformat(),
            )
        for i in range(6):
            det.record_session(
                session_id=f"s{i + 10}", profile_id="p1", chapter_id="ch2",
                topic="Equilibrium", subject="chemistry",
                total_questions=10, correct_answers=7 + i, score_percent=70.0 + i * 2,
                completed_at=(now - timedelta(days=i)).isoformat(),
            )
        return det

    def test_returns_breakdown(self, detector: WeakAreaDetector) -> None:
        breakdown = detector.get_subject_breakdown("p1")
        assert "physics" in breakdown
        assert "chemistry" in breakdown

    def test_breakdown_has_required_fields(self, detector: WeakAreaDetector) -> None:
        breakdown = detector.get_subject_breakdown("p1")
        for subj, stats in breakdown.items():
            assert "subject" in stats
            assert "total_attempts" in stats
            assert "correct_attempts" in stats
            assert "accuracy" in stats
            assert "trend" in stats
            assert "weight" in stats

    def test_trend_calculation(self, detector: WeakAreaDetector) -> None:
        breakdown = detector.get_subject_breakdown("p1")
        for subj, stats in breakdown.items():
            assert stats["trend"] in ("improving", "declining", "stable", "insufficient_data")

    def test_empty_profile(self) -> None:
        det = WeakAreaDetector()
        breakdown = det.get_subject_breakdown("nonexistent")
        assert breakdown == {}


class TestWeakAreaDetectorGetImprovementTrend:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        det = WeakAreaDetector()
        now = datetime.now(UTC)
        for i in range(10):
            det.record_session(
                session_id=f"s{i}", profile_id="p1", chapter_id="ch1",
                topic="Motion", subject="physics",
                total_questions=10, correct_answers=3 + i, score_percent=30.0 + i * 5,
                completed_at=(now - timedelta(days=10 - i)).isoformat(),
            )
        return det

    def test_returns_trend(self, detector: WeakAreaDetector) -> None:
        trend = detector.get_improvement_trend("p1")
        assert trend["profile_id"] == "p1"
        assert trend["total_sessions"] == 10
        assert "trajectory" in trend
        assert "monthly_breakdown" in trend

    def test_trajectory_values(self, detector: WeakAreaDetector) -> None:
        trend = detector.get_improvement_trend("p1")
        assert trend["trajectory"] in ("improving", "declining", "stable", "unknown")

    def test_no_sessions(self) -> None:
        det = WeakAreaDetector()
        trend = det.get_improvement_trend("nonexistent")
        assert trend["total_sessions"] == 0
        assert trend["trend"] == "no_data"
        assert trend["trajectory"] == "unknown"

    def test_single_session(self, detector: WeakAreaDetector) -> None:
        det = WeakAreaDetector()
        det.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=5, score_percent=50.0,
        )
        trend = det.get_improvement_trend("p1")
        assert trend["total_sessions"] == 1
        assert trend["trend"] == "insufficient_data"

    def test_monthly_breakdown_structure(self, detector: WeakAreaDetector) -> None:
        trend = detector.get_improvement_trend("p1")
        for month in trend["monthly_breakdown"]:
            assert "month" in month
            assert "sessions" in month
            assert "accuracy" in month
            assert "avg_time_per_question" in month

    def test_recent_5_accuracy(self, detector: WeakAreaDetector) -> None:
        trend = detector.get_improvement_trend("p1")
        assert "recent_5_session_accuracy" in trend
        assert 0 <= trend["recent_5_session_accuracy"] <= 1.0


class TestWeakAreaDetectorGenerateRecommendations:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        det = WeakAreaDetector()
        now = datetime.now(UTC)
        for i in range(5):
            det.record_session(
                session_id=f"s{i}", profile_id="p1", chapter_id="ch1",
                topic="Motion", subject="physics",
                total_questions=10, correct_answers=2, score_percent=20.0,
                completed_at=(now - timedelta(days=i)).isoformat(),
            )
        return det

    def test_generates_recommendations(self, detector: WeakAreaDetector) -> None:
        recs = detector.generate_study_recommendations("p1")
        assert len(recs) > 0

    def test_recommendation_structure(self, detector: WeakAreaDetector) -> None:
        recs = detector.generate_study_recommendations("p1")
        for rec in recs:
            assert "type" in rec
            assert "priority" in rec
            assert "action" in rec
            assert "reason" in rec

    def test_sorted_by_priority(self, detector: WeakAreaDetector) -> None:
        recs = detector.generate_study_recommendations("p1")
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        priorities = [priority_order.get(r["priority"], 3) for r in recs]
        assert priorities == sorted(priorities)

    def test_empty_profile(self) -> None:
        det = WeakAreaDetector()
        recs = det.generate_study_recommendations("nonexistent")
        assert recs == []


class TestWeakAreaDetectorGenerateFullReport:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        det = WeakAreaDetector()
        now = datetime.now(UTC)
        for i in range(5):
            det.record_session(
                session_id=f"s{i}", profile_id="p1", chapter_id="ch1",
                topic="Motion", subject="physics",
                total_questions=10, correct_answers=4, score_percent=40.0,
                completed_at=(now - timedelta(days=i)).isoformat(),
            )
        return det

    def test_returns_report(self, detector: WeakAreaDetector) -> None:
        report = detector.generate_full_report("p1")
        assert isinstance(report, WeakAreaReport)

    def test_report_has_all_sections(self, detector: WeakAreaDetector) -> None:
        report = detector.generate_full_report("p1")
        d = report.to_dict()
        assert "profile_id" in d
        assert "generated_at" in d
        assert "weak_areas" in d
        assert "subject_breakdown" in d
        assert "improvement_trend" in d
        assert "recommendations" in d


class TestWeakAreaDetectorComputeTrend:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        return WeakAreaDetector()

    def test_improving_trend(self, detector: WeakAreaDetector) -> None:
        history = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        trend = detector._compute_trend(history)
        assert trend == "improving"

    def test_declining_trend(self, detector: WeakAreaDetector) -> None:
        history = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
        trend = detector._compute_trend(history)
        assert trend == "declining"

    def test_stable_trend(self, detector: WeakAreaDetector) -> None:
        history = [0.5, 0.5, 0.5, 0.5, 0.5]
        trend = detector._compute_trend(history)
        assert trend == "stable"

    def test_insufficient_data(self, detector: WeakAreaDetector) -> None:
        history = [0.5, 0.6]
        trend = detector._compute_trend(history)
        assert trend == "insufficient_data"


class TestWeakAreaDetectorGetProfileStats:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        det = WeakAreaDetector()
        det.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=7, score_percent=70.0,
        )
        det.record_session(
            session_id="s2", profile_id="p1", chapter_id="ch2",
            topic="Thermodynamics", subject="physics",
            total_questions=10, correct_answers=5, score_percent=50.0,
        )
        det.record_session(
            session_id="s3", profile_id="p1", chapter_id="ch3",
            topic="Equilibrium", subject="chemistry",
            total_questions=10, correct_answers=8, score_percent=80.0,
        )
        return det

    def test_returns_stats(self, detector: WeakAreaDetector) -> None:
        stats = detector.get_profile_stats("p1")
        assert stats["profile_id"] == "p1"
        assert stats["total_sessions"] == 3
        assert stats["total_questions"] == 30
        assert stats["total_correct"] == 20
        assert abs(stats["overall_accuracy"] - 0.667) < 0.01

    def test_empty_profile(self) -> None:
        det = WeakAreaDetector()
        stats = det.get_profile_stats("nonexistent")
        assert stats["total_sessions"] == 0
        assert stats["total_questions"] == 0
        assert stats["overall_accuracy"] == 0.0

    def test_subjects_covered(self, detector: WeakAreaDetector) -> None:
        stats = detector.get_profile_stats("p1")
        assert "physics" in stats["subjects_covered"]
        assert "chemistry" in stats["subjects_covered"]


class TestWeakAreaDetectorReset:
    @pytest.fixture
    def detector(self) -> WeakAreaDetector:
        det = WeakAreaDetector()
        det.record_session(
            session_id="s1", profile_id="p1", chapter_id="ch1",
            topic="Motion", subject="physics",
            total_questions=10, correct_answers=7, score_percent=70.0,
        )
        det.record_session(
            session_id="s2", profile_id="p2", chapter_id="ch2",
            topic="Equilibrium", subject="chemistry",
            total_questions=10, correct_answers=8, score_percent=80.0,
        )
        return det

    def test_reset_all(self, detector: WeakAreaDetector) -> None:
        detector.reset()
        assert detector._sessions == {}
        assert detector._profile_sessions == {}
        assert detector._topic_performance == {}

    def test_reset_single_profile(self, detector: WeakAreaDetector) -> None:
        detector.reset(profile_id="p1")
        assert "s1" not in detector._sessions
        assert "p1" not in detector._profile_sessions
        assert "s2" in detector._sessions
        assert "p2" in detector._profile_sessions

    def test_reset_nonexistent_profile(self, detector: WeakAreaDetector) -> None:
        detector.reset(profile_id="nonexistent")
        assert "s1" in detector._sessions
        assert "s2" in detector._sessions


class TestWeakAreaDetectorEdgeCases:
    def test_all_correct_sessions(self) -> None:
        det = WeakAreaDetector()
        now = datetime.now(UTC)
        for i in range(5):
            det.record_session(
                session_id=f"s{i}", profile_id="p1", chapter_id="ch1",
                topic="Motion", subject="physics",
                total_questions=10, correct_answers=10, score_percent=100.0,
                completed_at=(now - timedelta(days=i)).isoformat(),
            )
        weak = det.get_weak_areas("p1")
        if weak:
            assert weak[0]["weakness_score"] == 0.0

    def test_all_wrong_sessions(self) -> None:
        det = WeakAreaDetector()
        now = datetime.now(UTC)
        for i in range(5):
            det.record_session(
                session_id=f"s{i}", profile_id="p1", chapter_id="ch1",
                topic="Motion", subject="physics",
                total_questions=10, correct_answers=0, score_percent=0.0,
                completed_at=(now - timedelta(days=i)).isoformat(),
            )
        weak = det.get_weak_areas("p1")
        assert len(weak) == 1
        assert weak[0]["severity"] in ("critical", "high")

    def test_mixed_subjects(self) -> None:
        det = WeakAreaDetector()
        now = datetime.now(UTC)
        subjects = ["physics", "chemistry", "biology"]
        for idx, subj in enumerate(subjects):
            for i in range(5):
                det.record_session(
                    session_id=f"s{idx}_{i}", profile_id="p1", chapter_id=f"ch{idx}",
                    topic=f"Topic {subj}", subject=subj,
                    total_questions=10, correct_answers=3, score_percent=30.0,
                    completed_at=(now - timedelta(days=i)).isoformat(),
                )
        breakdown = det.get_subject_breakdown("p1")
        assert len(breakdown) == 3
