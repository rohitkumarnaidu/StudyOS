"""Spaced repetition service — SM-2 algorithm for optimal review scheduling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SM2Item:
    """A single item tracked by the SM-2 spaced repetition algorithm."""

    item_id: str
    ease_factor: float = 2.5
    interval: int = 0
    repetitions: int = 0
    next_review: str = ""
    last_quality: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "ease_factor": round(self.ease_factor, 2),
            "interval": self.interval,
            "repetitions": self.repetitions,
            "next_review": self.next_review,
            "last_quality": self.last_quality,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SM2Item:
        return cls(
            item_id=data["item_id"],
            ease_factor=data.get("ease_factor", 2.5),
            interval=data.get("interval", 0),
            repetitions=data.get("repetitions", 0),
            next_review=data.get("next_review", ""),
            last_quality=data.get("last_quality", 0.0),
        )


class SpacedRepetitionEngine:
    """SM-2 algorithm implementation for spaced repetition scheduling."""

    MIN_EASE_FACTOR = 1.3
    DEFAULT_EASE_FACTOR = 2.5
    INITIAL_INTERVAL = 1
    SECOND_INTERVAL = 6

    def review(self, item: SM2Item, quality: float, today: str) -> SM2Item:
        """Process a review session and update the item's schedule.

        Args:
            item: The item being reviewed.
            quality: User's self-rated quality (0.0-5.0, where 5.0 is perfect).
            today: Current date string (YYYY-MM-DD).

        Returns:
            Updated SM2Item with new schedule.
        """
        quality = max(0.0, min(5.0, quality))
        item.last_quality = quality

        if quality < 3.0:
            item.repetitions = 0
            item.interval = 1
        else:
            if item.repetitions == 0:
                item.interval = self.INITIAL_INTERVAL
            elif item.repetitions == 1:
                item.interval = self.SECOND_INTERVAL
            else:
                item.interval = round(item.interval * item.ease_factor)

            item.repetitions += 1

        item.ease_factor = max(
            self.MIN_EASE_FACTOR,
            item.ease_factor + (0.1 - (5.0 - quality) * (0.08 + (5.0 - quality) * 0.02)),
        )

        item.next_review = self._add_days(today, item.interval)

        logger.info(
            "sm2.review",
            item_id=item.item_id,
            quality=quality,
            interval=item.interval,
            ease_factor=round(item.ease_factor, 2),
            next_review=item.next_review,
        )
        return item

    def get_due_items(self, items: list[SM2Item], today: str) -> list[SM2Item]:
        """Get all items due for review on or before today."""
        return [item for item in items if item.next_review <= today]

    def get_overdue_items(self, items: list[SM2Item], today: str) -> list[SM2Item]:
        """Get items that are overdue (past their review date)."""
        return [item for item in items if item.next_review < today]

    def get_predicted_retention(self, item: SM2Item, days_since_review: int) -> float:
        """Predict memory retention probability using forgetting curve approximation."""
        if days_since_review <= 0:
            return 1.0
        if item.interval <= 0:
            return 0.5

        decay = days_since_review / (item.interval * item.ease_factor)
        retention = max(0.0, min(1.0, 1.0 / (1.0 + decay)))
        return round(retention, 3)

    def create_new_item(self, item_id: str, today: str) -> SM2Item:
        """Create a new SM2 item scheduled for first review."""
        return SM2Item(
            item_id=item_id,
            ease_factor=self.DEFAULT_EASE_FACTOR,
            interval=0,
            repetitions=0,
            next_review=today,
        )

    def get_review_stats(self, items: list[SM2Item], today: str) -> dict[str, Any]:
        """Get statistics about a set of SM2 items."""
        due = self.get_due_items(items, today)
        overdue = self.get_overdue_items(items, today)
        avg_ease = sum(i.ease_factor for i in items) / len(items) if items else 0.0
        avg_interval = sum(i.interval for i in items) / len(items) if items else 0.0

        return {
            "total_items": len(items),
            "due_today": len(due),
            "overdue": len(overdue),
            "upcoming": len(items) - len(due),
            "avg_ease_factor": round(avg_ease, 2),
            "avg_interval_days": round(avg_interval, 1),
        }

    @staticmethod
    def _add_days(date_str: str, days: int) -> str:
        """Add days to a YYYY-MM-DD date string."""
        from datetime import datetime, timedelta

        dt = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=days)
        return dt.strftime("%Y-%m-%d")
