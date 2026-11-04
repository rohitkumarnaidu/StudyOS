"""Tests for ConceptGapAnalyzer service."""

from __future__ import annotations

from studyos_api.services.concept_gap_analyzer import ConceptGapAnalyzer


class TestConceptGapAnalyzer:
    def setup_method(self) -> None:
        self.analyzer = ConceptGapAnalyzer()

    def test_record_concept_attempt_correct(self) -> None:
        self.analyzer.record_concept_attempt("algebra", is_correct=True, timestamp="t1")
        assert self.analyzer._concept_data["algebra"]["attempts"] == 1
        assert self.analyzer._concept_data["algebra"]["mistakes"] == 0

    def test_record_concept_attempt_incorrect(self) -> None:
        self.analyzer.record_concept_attempt("algebra", is_correct=False, timestamp="t1")
        assert self.analyzer._concept_data["algebra"]["attempts"] == 1
        assert self.analyzer._concept_data["algebra"]["mistakes"] == 1
        assert self.analyzer._concept_data["algebra"]["last_mistake"] == "t1"

    def test_record_concept_attempt_with_related(self) -> None:
        self.analyzer.record_concept_attempt(
            "algebra", is_correct=False, timestamp="t1", related_concepts=["quadratic", "equations"]
        )
        assert "quadratic" in self.analyzer._concept_data["algebra"]["related"]
        assert "equations" in self.analyzer._concept_data["algebra"]["related"]

    def test_get_gap_score_unknown_concept(self) -> None:
        assert self.analyzer.get_gap_score("unknown") == 1.0

    def test_get_gap_score_no_attempts(self) -> None:
        self.analyzer._concept_data["algebra"] = {
            "attempts": 0,
            "mistakes": 0,
            "last_mistake": "",
            "related": set(),
        }
        assert self.analyzer.get_gap_score("algebra") == 1.0

    def test_get_gap_score_perfect(self) -> None:
        for i in range(5):
            self.analyzer.record_concept_attempt("algebra", is_correct=True, timestamp=f"t{i}")
        score = self.analyzer.get_gap_score("algebra")
        assert score == 0.0

    def test_get_gap_score_all_wrong(self) -> None:
        for i in range(5):
            self.analyzer.record_concept_attempt("algebra", is_correct=False, timestamp=f"t{i}")
        score = self.analyzer.get_gap_score("algebra")
        assert score == 1.0

    def test_get_gap_score_mixed(self) -> None:
        self.analyzer.record_concept_attempt("algebra", is_correct=True, timestamp="t1")
        self.analyzer.record_concept_attempt("algebra", is_correct=False, timestamp="t2")
        self.analyzer.record_concept_attempt("algebra", is_correct=True, timestamp="t3")
        score = self.analyzer.get_gap_score("algebra")
        assert 0.0 < score < 1.0

    def test_analyze_gaps_returns_above_threshold(self) -> None:
        # Create a weak concept
        for i in range(5):
            self.analyzer.record_concept_attempt("weak", is_correct=False, timestamp=f"t{i}")
        # Create a strong concept
        for i in range(5):
            self.analyzer.record_concept_attempt("strong", is_correct=True, timestamp=f"t{i}")

        gaps = self.analyzer.analyze_gaps(min_attempts=3)
        assert len(gaps) == 1
        assert gaps[0].concept == "weak"
        assert gaps[0].gap_score >= 0.6

    def test_analyze_gaps_respects_min_attempts(self) -> None:
        self.analyzer.record_concept_attempt("new", is_correct=False, timestamp="t1")
        gaps = self.analyzer.analyze_gaps(min_attempts=3)
        assert len(gaps) == 0

    def test_analyze_gaps_sorted_by_score(self) -> None:
        for i in range(5):
            self.analyzer.record_concept_attempt("critical", is_correct=False, timestamp=f"t{i}")
        for i in range(4):
            self.analyzer.record_concept_attempt(
                "moderate", is_correct=(i % 2 == 0), timestamp=f"t{i}"
            )

        gaps = self.analyzer.analyze_gaps(min_attempts=3)
        if len(gaps) > 1:
            assert gaps[0].gap_score >= gaps[1].gap_score

    def test_get_weak_concepts(self) -> None:
        for i in range(5):
            self.analyzer.record_concept_attempt(
                f"concept_{i}", is_correct=(i > 2), timestamp=f"t{i}"
            )

        weak = self.analyzer.get_weak_concepts(top_n=3)
        assert len(weak) <= 3

    def test_get_mastery_level(self) -> None:
        assert self.analyzer.get_mastery_level("unknown") == "critical"

        self.analyzer._concept_data["mastered"] = {
            "attempts": 10,
            "mistakes": 0,
            "last_mistake": "",
            "related": set(),
        }
        assert self.analyzer.get_mastery_level("mastered") == "mastered"

        self.analyzer._concept_data["weak"] = {
            "attempts": 10,
            "mistakes": 8,
            "last_mistake": "t1",
            "related": set(),
        }
        assert self.analyzer.get_mastery_level("weak") == "critical"

    def test_get_study_plan(self) -> None:
        for i in range(5):
            self.analyzer.record_concept_attempt("gap1", is_correct=False, timestamp=f"t{i}")
        for i in range(4):
            self.analyzer.record_concept_attempt("gap2", is_correct=(i % 2 == 0), timestamp=f"t{i}")

        plan = self.analyzer.get_study_plan(max_concepts=3)
        assert len(plan) >= 1
        assert plan[0]["concept"] == "gap1"
        assert plan[0]["priority"] == "high"

    def test_reset(self) -> None:
        self.analyzer.record_concept_attempt("algebra", is_correct=False, timestamp="t1")
        self.analyzer.reset()
        assert len(self.analyzer._concept_data) == 0

    def test_concept_gap_to_dict(self) -> None:
        from studyos_api.services.concept_gap_analyzer import ConceptGap

        gap = ConceptGap(
            concept="algebra",
            gap_score=0.75,
            mistake_count=5,
            last_mistake_timestamp="t1",
            related_concepts=["quadratic"],
            recommended_action="Practice",
        )
        d = gap.to_dict()
        assert d["concept"] == "algebra"
        assert d["gap_score"] == 0.75
        assert d["mistake_count"] == 5
        assert d["related_concepts"] == ["quadratic"]
