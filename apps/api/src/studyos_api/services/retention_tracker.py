"""Retention tracker — forgetting curve model for predicting memory decay."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RetentionRecord:
    """A single retention measurement."""

    item_id: str
    days_since_review: int
    predicted_retention: float
    actual_retention: float
    quality_score: float
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "days_since_review": self.days_since_review,
            "predicted_retention": round(self.predicted_retention, 3),
            "actual_retention": round(self.actual_retention, 3),
            "quality_score": self.quality_score,
            "timestamp": self.timestamp,
        }


class ForgettingCurveModel:
    """Ebbinghaus forgetting curve with personalized decay parameters."""

    def __init__(self, decay_rate: float = 0.5, baseline_retention: float = 1.0) -> None:
        self._decay_rate = decay_rate
        self._baseline = baseline_retention

    def predict_retention(self, days_elapsed: int, strength: float = 1.0) -> float:
        """Predict memory retention after given days.

        Uses exponential decay: R(t) = baseline * e^(-decay_rate * t / strength)
        """
        if days_elapsed <= 0:
            return self._baseline

        retention = self._baseline * math.exp(-self._decay_rate * days_elapsed / max(strength, 0.1))
        return round(max(0.0, min(1.0, retention)), 3)

    def optimal_review_interval(self, target_retention: float = 0.8, strength: float = 1.0) -> int:
        """Calculate optimal days until next review for target retention."""
        if target_retention >= self._baseline:
            return 1

        days = -math.log(target_retention / self._baseline) * strength / self._decay_rate
        return max(1, round(days))


class RetentionTracker:
    """Tracks and analyzes memory retention patterns across study items."""

    def __init__(self) -> None:
        self._records: list[RetentionRecord] = []
        self._curve = ForgettingCurveModel()

    def record(
        self,
        item_id: str,
        days_since_review: int,
        quality_score: float,
        timestamp: str = "",
    ) -> RetentionRecord:
        """Record a retention measurement."""
        strength = max(0.1, quality_score / 5.0)
        predicted = self._curve.predict_retention(days_since_review, strength)
        actual = quality_score / 5.0

        record = RetentionRecord(
            item_id=item_id,
            days_since_review=days_since_review,
            predicted_retention=predicted,
            actual_retention=actual,
            quality_score=quality_score,
            timestamp=timestamp,
        )
        self._records.append(record)
        return record

    def get_item_retention(self, item_id: str) -> list[RetentionRecord]:
        """Get all retention records for an item."""
        return [r for r in self._records if r.item_id == item_id]

    def get_average_retention(self, days_elapsed: int) -> float:
        """Get average actual retention for items at a given elapsed time."""
        relevant = [r for r in self._records if abs(r.days_since_review - days_elapsed) <= 1]
        if not relevant:
            return 0.0
        return round(sum(r.actual_retention for r in relevant) / len(relevant), 3)

    def get_model_accuracy(self) -> float:
        """Calculate how well the forgetting curve predicts actual retention."""
        if not self._records:
            return 0.0

        errors = [abs(r.predicted_retention - r.actual_retention) for r in self._records]
        mae = sum(errors) / len(errors)
        return round(max(0.0, 1.0 - mae), 3)

    def get_weak_items(self, threshold: float = 0.5) -> list[str]:
        """Get items with retention below threshold."""
        item_scores: dict[str, list[float]] = {}
        for r in self._records:
            item_scores.setdefault(r.item_id, []).append(r.actual_retention)

        weak = []
        for item_id, scores in item_scores.items():
            avg = sum(scores) / len(scores)
            if avg < threshold:
                weak.append(item_id)
        return weak

    def get_retention_summary(self) -> dict[str, Any]:
        """Get overall retention statistics."""
        if not self._records:
            return {"total_records": 0}

        avg_actual = sum(r.actual_retention for r in self._records) / len(self._records)
        avg_predicted = sum(r.predicted_retention for r in self._records) / len(self._records)

        return {
            "total_records": len(self._records),
            "avg_actual_retention": round(avg_actual, 3),
            "avg_predicted_retention": round(avg_predicted, 3),
            "model_accuracy": self.get_model_accuracy(),
            "weak_items_count": len(self.get_weak_items()),
            "unique_items": len(set(r.item_id for r in self._records)),
        }

    def reset(self) -> None:
        """Clear all retention records."""
        self._records.clear()
