"""Mistake predictor — predicts likely future mistakes based on historical patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class MistakePrediction:
    """A prediction about likely future mistakes."""

    concept: str
    predicted_probability: float  # 0.0 to 1.0
    risk_level: str  # "low", "medium", "high", "critical"
    contributing_factors: list[str] = field(default_factory=list)
    recommended_prevention: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "concept": self.concept,
            "predicted_probability": round(self.predicted_probability, 3),
            "risk_level": self.risk_level,
            "contributing_factors": self.contributing_factors,
            "recommended_prevention": self.recommended_prevention,
        }


class MistakePredictor:
    """Predicts likely future mistakes based on historical mistake patterns."""

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def record_outcome(
        self,
        concept: str,
        is_correct: bool,
        time_taken: float = 0.0,
        confidence: float = 0.0,
        difficulty: float = 0.5,
        timestamp: str = "",
    ) -> None:
        """Record a study outcome for prediction modeling."""
        self._history.append(
            {
                "concept": concept,
                "is_correct": is_correct,
                "time_taken": time_taken,
                "confidence": confidence,
                "difficulty": difficulty,
                "timestamp": timestamp,
            }
        )

    def predict_mistake_probability(
        self,
        concept: str,
        upcoming_difficulty: float = 0.5,
    ) -> float:
        """Predict probability of making a mistake on a concept."""
        concept_outcomes = [h for h in self._history if h["concept"] == concept]
        if not concept_outcomes:
            return 0.5  # No data = neutral prediction

        recent = concept_outcomes[-5:]  # Last 5 attempts
        mistake_rate = sum(1 for o in recent if not o["is_correct"]) / len(recent)

        # Factor in confidence (low confidence → higher mistake probability)
        avg_confidence = sum(o["confidence"] for o in recent) / len(recent)
        confidence_factor = max(0.0, 1.0 - avg_confidence) * 0.3

        # Factor in time pressure (fast answers on hard problems → mistakes)
        avg_time = sum(o["time_taken"] for o in recent) / len(recent)
        time_pressure = max(0.0, (1.0 - avg_time / 120.0)) * 0.2 if avg_time > 0 else 0.0

        # Difficulty adjustment
        difficulty_factor = upcoming_difficulty * 0.2

        probability = min(
            1.0, mistake_rate * 0.5 + confidence_factor + time_pressure + difficulty_factor
        )
        return round(probability, 3)

    def get_predictions(self, concepts: list[str] | None = None) -> list[MistakePrediction]:
        """Get mistake predictions for specified or all known concepts."""
        if concepts is None:
            concepts = list(set(h["concept"] for h in self._history))

        predictions = []
        for concept in concepts:
            prob = self.predict_mistake_probability(concept)
            risk = self._classify_risk(prob)
            factors = self._identify_factors(concept)
            prevention = self._recommend_prevention(risk)

            predictions.append(
                MistakePrediction(
                    concept=concept,
                    predicted_probability=prob,
                    risk_level=risk,
                    contributing_factors=factors,
                    recommended_prevention=prevention,
                )
            )

        return sorted(predictions, key=lambda p: p.predicted_probability, reverse=True)

    def get_high_risk_concepts(self, threshold: float = 0.7) -> list[str]:
        """Get concepts with mistake probability above threshold."""
        predictions = self.get_predictions()
        return [p.concept for p in predictions if p.predicted_probability >= threshold]

    def get_improvement_trend(self, concept: str) -> str:
        """Analyze whether performance on a concept is improving, declining, or stable."""
        concept_outcomes = [h for h in self._history if h["concept"] == concept]
        if len(concept_outcomes) < 4:
            return "insufficient_data"

        first_half = concept_outcomes[: len(concept_outcomes) // 2]
        second_half = concept_outcomes[len(concept_outcomes) // 2 :]

        first_rate = sum(1 for o in first_half if o["is_correct"]) / len(first_half)
        second_rate = sum(1 for o in second_half if o["is_correct"]) / len(second_half)

        diff = second_rate - first_rate
        if diff > 0.15:
            return "improving"
        elif diff < -0.15:
            return "declining"
        else:
            return "stable"

    def reset(self) -> None:
        """Clear all history."""
        self._history.clear()

    @staticmethod
    def _classify_risk(probability: float) -> str:
        if probability >= 0.8:
            return "critical"
        elif probability >= 0.6:
            return "high"
        elif probability >= 0.4:
            return "medium"
        else:
            return "low"

    def _identify_factors(self, concept: str) -> list[str]:
        concept_outcomes = [h for h in self._history if h["concept"] == concept]
        if not concept_outcomes:
            return ["no_history"]

        factors = []
        recent = concept_outcomes[-5:]

        # Check for low confidence pattern
        avg_conf = sum(o["confidence"] for o in recent) / len(recent)
        if avg_conf < 0.5:
            factors.append("low_confidence")

        # Check for time pressure pattern
        avg_time = sum(o["time_taken"] for o in recent) / len(recent)
        if avg_time < 30 and avg_time > 0:
            factors.append("rushed_answers")

        # Check for recent mistake streak
        recent_mistakes = sum(1 for o in recent if not o["is_correct"])
        if recent_mistakes >= 3:
            factors.append("mistake_streak")

        # Check for high difficulty struggles
        high_diff = [o for o in recent if o["difficulty"] > 0.7 and not o["is_correct"]]
        if len(high_diff) > 0:
            factors.append("struggles_with_hard_problems")

        return factors if factors else ["consistent_performance"]

    @staticmethod
    def _recommend_prevention(risk: str) -> str:
        if risk == "critical":
            return "Immediate review with foundational concepts before attempting new problems"
        elif risk == "high":
            return "Targeted practice with medium-difficulty problems and self-explanation"
        elif risk == "medium":
            return "Periodic review and mixed practice to reinforce retention"
        else:
            return "Maintain current study routine with occasional self-testing"
