"""Tests for MistakeTracker service."""

from __future__ import annotations

from studyos_api.services.mistake_tracker import MistakeTracker, MistakeType


class TestMistakeRecord:
    def test_to_dict(self) -> None:
        from studyos_api.services.mistake_tracker import MistakeRecord

        record = MistakeRecord(
            mistake_id="m1",
            profile_id="p1",
            question_id="q1",
            mistake_type=MistakeType.CONCEPTUAL,
            concept_tags=["algebra", "quadratic"],
            confidence_level=0.7,
            time_taken_seconds=45.0,
            timestamp="2026-05-19T10:00:00Z",
        )
        d = record.to_dict()
        assert d["mistake_id"] == "m1"
        assert d["profile_id"] == "p1"
        assert d["question_id"] == "q1"
        assert d["mistake_type"] == "conceptual"
        assert d["concept_tags"] == ["algebra", "quadratic"]
        assert d["confidence_level"] == 0.7
        assert d["time_taken_seconds"] == 45.0


class TestMistakeTracker:
    def setup_method(self) -> None:
        self.tracker = MistakeTracker()

    def test_log_mistake(self) -> None:
        record = self.tracker.log_mistake(
            mistake_id="m1",
            profile_id="p1",
            question_id="q1",
            mistake_type=MistakeType.CONCEPTUAL,
            concept_tags=["algebra"],
            confidence_level=0.5,
            time_taken_seconds=30.0,
            timestamp="2026-05-19T10:00:00Z",
        )
        assert record.mistake_id == "m1"
        assert record.profile_id == "p1"
        assert record.mistake_type == MistakeType.CONCEPTUAL
        assert len(self.tracker._mistakes) == 1

    def test_get_user_mistakes(self) -> None:
        self.tracker.log_mistake("m1", "p1", "q1", MistakeType.CONCEPTUAL, timestamp="t1")
        self.tracker.log_mistake("m2", "p2", "q2", MistakeType.CALCULATION, timestamp="t2")
        self.tracker.log_mistake("m3", "p1", "q3", MistakeType.MISREAD, timestamp="t3")

        user_mistakes = self.tracker.get_user_mistakes("p1")
        assert len(user_mistakes) == 2
        assert all(m.profile_id == "p1" for m in user_mistakes)

    def test_get_mistakes_by_type(self) -> None:
        self.tracker.log_mistake("m1", "p1", "q1", MistakeType.CONCEPTUAL, timestamp="t1")
        self.tracker.log_mistake("m2", "p1", "q2", MistakeType.CALCULATION, timestamp="t2")
        self.tracker.log_mistake("m3", "p1", "q3", MistakeType.CONCEPTUAL, timestamp="t3")

        conceptual = self.tracker.get_mistakes_by_type("p1", MistakeType.CONCEPTUAL)
        assert len(conceptual) == 2
        assert all(m.mistake_type == MistakeType.CONCEPTUAL for m in conceptual)

    def test_get_mistakes_by_concept(self) -> None:
        self.tracker.log_mistake(
            "m1", "p1", "q1", MistakeType.CONCEPTUAL, concept_tags=["algebra"], timestamp="t1"
        )
        self.tracker.log_mistake(
            "m2", "p1", "q2", MistakeType.CALCULATION, concept_tags=["geometry"], timestamp="t2"
        )
        self.tracker.log_mistake(
            "m3",
            "p1",
            "q3",
            MistakeType.MISREAD,
            concept_tags=["algebra", "trigonometry"],
            timestamp="t3",
        )

        algebra_mistakes = self.tracker.get_mistakes_by_concept("p1", "algebra")
        assert len(algebra_mistakes) == 2

    def test_get_concept_frequency(self) -> None:
        self.tracker.log_mistake(
            "m1", "p1", "q1", MistakeType.CONCEPTUAL, concept_tags=["algebra"], timestamp="t1"
        )
        self.tracker.log_mistake(
            "m2", "p1", "q2", MistakeType.CALCULATION, concept_tags=["algebra"], timestamp="t2"
        )
        self.tracker.log_mistake(
            "m3", "p1", "q3", MistakeType.MISREAD, concept_tags=["geometry"], timestamp="t3"
        )

        freq = self.tracker.get_concept_frequency("p1")
        assert freq["algebra"] == 2
        assert freq["geometry"] == 1

    def test_get_type_distribution(self) -> None:
        self.tracker.log_mistake("m1", "p1", "q1", MistakeType.CONCEPTUAL, timestamp="t1")
        self.tracker.log_mistake("m2", "p1", "q2", MistakeType.CONCEPTUAL, timestamp="t2")
        self.tracker.log_mistake("m3", "p1", "q3", MistakeType.CALCULATION, timestamp="t3")
        self.tracker.log_mistake("m4", "p1", "q4", MistakeType.CARELESS, timestamp="t4")

        dist = self.tracker.get_type_distribution("p1")
        assert dist["conceptual"] == 2
        assert dist["calculation"] == 1
        assert dist["careless"] == 1

    def test_get_mistake_stats(self) -> None:
        self.tracker.log_mistake(
            "m1",
            "p1",
            "q1",
            MistakeType.CONCEPTUAL,
            confidence_level=0.5,
            time_taken_seconds=30.0,
            timestamp="t1",
        )
        self.tracker.log_mistake(
            "m2",
            "p1",
            "q2",
            MistakeType.CALCULATION,
            confidence_level=0.8,
            time_taken_seconds=60.0,
            timestamp="t2",
        )

        stats = self.tracker.get_mistake_stats("p1")
        assert stats["total_mistakes"] == 2
        assert stats["avg_confidence"] == 0.65
        assert stats["avg_time_seconds"] == 45.0
        assert "type_distribution" in stats
        assert "top_concepts" in stats

    def test_get_mistake_stats_empty(self) -> None:
        stats = self.tracker.get_mistake_stats("p1")
        assert stats == {"total_mistakes": 0}

    def test_reset(self) -> None:
        self.tracker.log_mistake("m1", "p1", "q1", MistakeType.CONCEPTUAL, timestamp="t1")
        self.tracker.log_mistake("m2", "p1", "q2", MistakeType.CALCULATION, timestamp="t2")
        self.tracker.reset()
        assert len(self.tracker._mistakes) == 0
