"""Tests for MistakePredictor service."""

from __future__ import annotations

import pytest

from studyos_api.services.mistake_predictor import MistakePredictor


class TestMistakePredictor:
    def setup_method(self) -> None:
        self.predictor = MistakePredictor()

    def test_record_outcome(self) -> None:
        self.predictor.record_outcome(
            "algebra", is_correct=False, time_taken=45.0, confidence=0.3, difficulty=0.7, timestamp="t1"
        )
        assert len(self.predictor._history) == 1
        assert self.predictor._history[0]["concept"] == "algebra"
        assert self.predictor._history[0]["is_correct"] is False

    def test_predict_no_history(self) -> None:
        prob = self.predictor.predict_mistake_probability("unknown")
        assert prob == 0.5

    def test_predict_all_correct(self) -> None:
        for i in range(5):
            self.predictor.record_outcome("algebra", is_correct=True, confidence=0.9, time_taken=60.0)
        prob = self.predictor.predict_mistake_probability("algebra")
        assert prob < 0.3

    def test_predict_all_wrong(self) -> None:
        for i in range(5):
            self.predictor.record_outcome("algebra", is_correct=False, confidence=0.2, time_taken=20.0)
        prob = self.predictor.predict_mistake_probability("algebra")
        assert prob > 0.5

    def test_predict_mixed_history(self) -> None:
        self.predictor.record_outcome("algebra", is_correct=True, confidence=0.8, time_taken=60.0)
        self.predictor.record_outcome("algebra", is_correct=False, confidence=0.4, time_taken=30.0)
        self.predictor.record_outcome("algebra", is_correct=True, confidence=0.7, time_taken=45.0)
        prob = self.predictor.predict_mistake_probability("algebra")
        assert 0.0 <= prob <= 1.0

    def test_predict_with_high_difficulty(self) -> None:
        for i in range(5):
            self.predictor.record_outcome("algebra", is_correct=False, confidence=0.3, time_taken=20.0)
        prob = self.predictor.predict_mistake_probability("algebra", upcoming_difficulty=0.9)
        assert prob > 0.5

    def test_get_predictions(self) -> None:
        self.predictor.record_outcome("algebra", is_correct=False, confidence=0.2, time_taken=15.0)
        self.predictor.record_outcome("algebra", is_correct=False, confidence=0.3, time_taken=20.0)
        self.predictor.record_outcome("geometry", is_correct=True, confidence=0.9, time_taken=60.0)

        predictions = self.predictor.get_predictions()
        assert len(predictions) == 2
        assert predictions[0].predicted_probability >= predictions[1].predicted_probability

    def test_get_predictions_for_specific_concepts(self) -> None:
        self.predictor.record_outcome("algebra", is_correct=False, confidence=0.2)
        self.predictor.record_outcome("geometry", is_correct=True, confidence=0.9)

        predictions = self.predictor.get_predictions(concepts=["algebra"])
        assert len(predictions) == 1
        assert predictions[0].concept == "algebra"

    def test_get_high_risk_concepts(self) -> None:
        for i in range(5):
            self.predictor.record_outcome("weak", is_correct=False, confidence=0.1, time_taken=10.0)
        for i in range(5):
            self.predictor.record_outcome("strong", is_correct=True, confidence=0.9, time_taken=60.0)

        high_risk = self.predictor.get_high_risk_concepts(threshold=0.6)
        assert "weak" in high_risk
        assert "strong" not in high_risk

    def test_get_improvement_trend_improving(self) -> None:
        # First half: all wrong
        for i in range(4):
            self.predictor.record_outcome("algebra", is_correct=False)
        # Second half: all correct
        for i in range(4):
            self.predictor.record_outcome("algebra", is_correct=True)

        trend = self.predictor.get_improvement_trend("algebra")
        assert trend == "improving"

    def test_get_improvement_trend_declining(self) -> None:
        for i in range(4):
            self.predictor.record_outcome("algebra", is_correct=True)
        for i in range(4):
            self.predictor.record_outcome("algebra", is_correct=False)

        trend = self.predictor.get_improvement_trend("algebra")
        assert trend == "declining"

    def test_get_improvement_trend_stable(self) -> None:
        for i in range(8):
            self.predictor.record_outcome("algebra", is_correct=(i % 2 == 0))

        trend = self.predictor.get_improvement_trend("algebra")
        assert trend == "stable"

    def test_get_improvement_trend_insufficient_data(self) -> None:
        self.predictor.record_outcome("algebra", is_correct=True)
        self.predictor.record_outcome("algebra", is_correct=False)

        trend = self.predictor.get_improvement_trend("algebra")
        assert trend == "insufficient_data"

    def test_classify_risk(self) -> None:
        assert MistakePredictor._classify_risk(0.9) == "critical"
        assert MistakePredictor._classify_risk(0.7) == "high"
        assert MistakePredictor._classify_risk(0.5) == "medium"
        assert MistakePredictor._classify_risk(0.2) == "low"

    def test_identify_factors_low_confidence(self) -> None:
        for i in range(5):
            self.predictor.record_outcome("algebra", is_correct=False, confidence=0.2)
        factors = self.predictor._identify_factors("algebra")
        assert "low_confidence" in factors

    def test_identify_factors_rushed_answers(self) -> None:
        for i in range(5):
            self.predictor.record_outcome("algebra", is_correct=False, time_taken=10.0)
        factors = self.predictor._identify_factors("algebra")
        assert "rushed_answers" in factors

    def test_identify_factors_mistake_streak(self) -> None:
        for i in range(5):
            self.predictor.record_outcome("algebra", is_correct=False)
        factors = self.predictor._identify_factors("algebra")
        assert "mistake_streak" in factors

    def test_identify_factors_struggles_with_hard(self) -> None:
        for i in range(3):
            self.predictor.record_outcome("algebra", is_correct=False, difficulty=0.9)
        factors = self.predictor._identify_factors("algebra")
        assert "struggles_with_hard_problems" in factors

    def test_reset(self) -> None:
        self.predictor.record_outcome("algebra", is_correct=False)
        self.predictor.reset()
        assert len(self.predictor._history) == 0

    def test_prediction_to_dict(self) -> None:
        from studyos_api.services.mistake_predictor import MistakePrediction

        pred = MistakePrediction(
            concept="algebra",
            predicted_probability=0.75,
            risk_level="high",
            contributing_factors=["low_confidence"],
            recommended_prevention="Practice",
        )
        d = pred.to_dict()
        assert d["concept"] == "algebra"
        assert d["predicted_probability"] == 0.75
        assert d["risk_level"] == "high"
