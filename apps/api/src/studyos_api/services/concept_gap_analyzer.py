"""Concept gap analyzer — identifies knowledge gaps from mistake patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ConceptGap:
    """Represents a knowledge gap in a specific concept."""

    concept: str
    gap_score: float  # 0.0 (mastered) to 1.0 (critical gap)
    mistake_count: int
    last_mistake_timestamp: str = ""
    related_concepts: list[str] = field(default_factory=list)
    recommended_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "concept": self.concept,
            "gap_score": round(self.gap_score, 3),
            "mistake_count": self.mistake_count,
            "last_mistake_timestamp": self.last_mistake_timestamp,
            "related_concepts": self.related_concepts,
            "recommended_action": self.recommended_action,
        }


class ConceptGapAnalyzer:
    """Analyzes mistake patterns to identify knowledge gaps."""

    def __init__(self, threshold: float = 0.6) -> None:
        self._threshold = threshold
        self._concept_data: dict[str, dict[str, Any]] = {}

    def record_concept_attempt(
        self,
        concept: str,
        is_correct: bool,
        timestamp: str = "",
        related_concepts: list[str] | None = None,
    ) -> None:
        """Record an attempt on a concept (correct or incorrect)."""
        if concept not in self._concept_data:
            self._concept_data[concept] = {
                "attempts": 0,
                "mistakes": 0,
                "last_mistake": "",
                "related": set(related_concepts or []),
            }

        data = self._concept_data[concept]
        data["attempts"] += 1
        if not is_correct:
            data["mistakes"] += 1
            data["last_mistake"] = timestamp
        if related_concepts:
            data["related"].update(related_concepts)

    def get_gap_score(self, concept: str) -> float:
        """Calculate gap score for a concept (0.0 = mastered, 1.0 = critical)."""
        if concept not in self._concept_data:
            return 1.0  # Unknown concept = full gap

        data = self._concept_data[concept]
        if data["attempts"] == 0:
            return 1.0

        mistake_ratio = data["mistakes"] / data["attempts"]
        # Weight recent mistakes more heavily
        recency_bonus = 0.1 if data["last_mistake"] else 0.0
        return min(1.0, mistake_ratio + recency_bonus)

    def analyze_gaps(self, min_attempts: int = 3) -> list[ConceptGap]:
        """Analyze all concepts and return gaps above threshold."""
        gaps = []
        for concept, data in self._concept_data.items():
            if data["attempts"] < min_attempts:
                continue

            score = self.get_gap_score(concept)
            if score >= self._threshold:
                action = self._recommend_action(score, data["mistakes"])
                gap = ConceptGap(
                    concept=concept,
                    gap_score=score,
                    mistake_count=data["mistakes"],
                    last_mistake_timestamp=data["last_mistake"],
                    related_concepts=sorted(data["related"]),
                    recommended_action=action,
                )
                gaps.append(gap)

        return sorted(gaps, key=lambda g: g.gap_score, reverse=True)

    def get_weak_concepts(self, top_n: int = 5) -> list[ConceptGap]:
        """Get the top N weakest concepts."""
        all_gaps = self.analyze_gaps(min_attempts=1)
        return all_gaps[:top_n]

    def get_mastery_level(self, concept: str) -> str:
        """Get mastery level description for a concept."""
        score = self.get_gap_score(concept)
        if score < 0.2:
            return "mastered"
        elif score < 0.4:
            return "proficient"
        elif score < 0.6:
            return "developing"
        elif score < 0.8:
            return "weak"
        else:
            return "critical"

    def get_study_plan(self, max_concepts: int = 5) -> list[dict[str, Any]]:
        """Generate a prioritized study plan based on gaps."""
        gaps = self.analyze_gaps(min_attempts=1)[:max_concepts]
        plan = []
        for gap in gaps:
            plan.append({
                "concept": gap.concept,
                "priority": "high" if gap.gap_score >= 0.8 else "medium" if gap.gap_score >= 0.6 else "low",
                "gap_score": gap.gap_score,
                "action": gap.recommended_action,
                "related_concepts": gap.related_concepts,
            })
        return plan

    def reset(self) -> None:
        """Clear all concept data."""
        self._concept_data.clear()

    @staticmethod
    def _recommend_action(score: float, mistake_count: int) -> str:
        if score >= 0.8:
            return "Review foundational material and practice basic problems"
        elif score >= 0.6:
            return "Targeted practice on weak areas with guided examples"
        else:
            return "Light review and periodic self-testing"
