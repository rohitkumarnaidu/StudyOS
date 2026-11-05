"""Mistake tracker — logs and categorizes user mistakes for pattern analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class MistakeType(str, Enum):
    CONCEPTUAL = "conceptual"
    CALCULATION = "calculation"
    MISREAD = "misread"
    GUESS = "guess"
    TIME_PRESSURE = "time_pressure"
    CARELESS = "careless"


@dataclass
class MistakeRecord:
    """A single mistake log entry."""

    mistake_id: str
    profile_id: str
    question_id: str
    mistake_type: MistakeType
    concept_tags: list[str] = field(default_factory=list)
    confidence_level: float = 0.0
    time_taken_seconds: float = 0.0
    correct_answer: str = ""
    user_answer: str = ""
    timestamp: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mistake_id": self.mistake_id,
            "profile_id": self.profile_id,
            "question_id": self.question_id,
            "mistake_type": self.mistake_type.value,
            "concept_tags": self.concept_tags,
            "confidence_level": self.confidence_level,
            "time_taken_seconds": self.time_taken_seconds,
            "timestamp": self.timestamp,
        }


class MistakeTracker:
    """Tracks and analyzes user mistakes across all study activities."""

    def __init__(self) -> None:
        self._mistakes: list[MistakeRecord] = []

    def log_mistake(
        self,
        mistake_id: str,
        profile_id: str,
        question_id: str,
        mistake_type: MistakeType,
        concept_tags: list[str] | None = None,
        confidence_level: float = 0.0,
        time_taken_seconds: float = 0.0,
        correct_answer: str = "",
        user_answer: str = "",
        timestamp: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> MistakeRecord:
        """Log a new mistake."""
        record = MistakeRecord(
            mistake_id=mistake_id,
            profile_id=profile_id,
            question_id=question_id,
            mistake_type=mistake_type,
            concept_tags=concept_tags or [],
            confidence_level=confidence_level,
            time_taken_seconds=time_taken_seconds,
            correct_answer=correct_answer,
            user_answer=user_answer,
            timestamp=timestamp,
            metadata=metadata or {},
        )
        self._mistakes.append(record)
        logger.info(
            "mistake.logged",
            profile_id=profile_id,
            type=mistake_type.value,
            concepts=record.concept_tags,
        )
        return record

    def get_user_mistakes(self, profile_id: str) -> list[MistakeRecord]:
        """Get all mistakes for a user."""
        return [m for m in self._mistakes if m.profile_id == profile_id]

    def get_mistakes_by_type(
        self, profile_id: str, mistake_type: MistakeType
    ) -> list[MistakeRecord]:
        """Get mistakes filtered by type."""
        return [
            m
            for m in self._mistakes
            if m.profile_id == profile_id and m.mistake_type == mistake_type
        ]

    def get_mistakes_by_concept(self, profile_id: str, concept: str) -> list[MistakeRecord]:
        """Get mistakes related to a specific concept."""
        return [
            m for m in self._mistakes if m.profile_id == profile_id and concept in m.concept_tags
        ]

    def get_concept_frequency(self, profile_id: str) -> dict[str, int]:
        """Get frequency of mistakes per concept tag."""
        freq: dict[str, int] = {}
        for m in self._mistakes:
            if m.profile_id != profile_id:
                continue
            for tag in m.concept_tags:
                freq[tag] = freq.get(tag, 0) + 1
        return freq

    def get_type_distribution(self, profile_id: str) -> dict[str, int]:
        """Get distribution of mistake types."""
        dist: dict[str, int] = {}
        for m in self._mistakes:
            if m.profile_id != profile_id:
                continue
            key = m.mistake_type.value
            dist[key] = dist.get(key, 0) + 1
        return dist

    def get_mistake_stats(self, profile_id: str) -> dict[str, Any]:
        """Get overall mistake statistics for a user."""
        user_mistakes = self.get_user_mistakes(profile_id)
        if not user_mistakes:
            return {"total_mistakes": 0}

        avg_confidence = sum(m.confidence_level for m in user_mistakes) / len(user_mistakes)
        avg_time = sum(m.time_taken_seconds for m in user_mistakes) / len(user_mistakes)

        return {
            "total_mistakes": len(user_mistakes),
            "avg_confidence": round(avg_confidence, 2),
            "avg_time_seconds": round(avg_time, 1),
            "type_distribution": self.get_type_distribution(profile_id),
            "top_concepts": sorted(
                self.get_concept_frequency(profile_id).items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5],
        }

    def reset(self) -> None:
        """Clear all mistake records."""
        self._mistakes.clear()
