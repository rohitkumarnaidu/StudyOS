"""Revision pack generator — AI-curated revision packs from spaced repetition data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RevisionPack:
    """A curated set of items for revision."""

    pack_id: str
    pack_type: str
    items: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pack_id": self.pack_id,
            "pack_type": self.pack_type,
            "item_count": len(self.items),
            "items": self.items,
            "metadata": self.metadata,
        }


class RevisionPackGenerator:
    """Generates revision packs based on spaced repetition and retention data."""

    def __init__(self) -> None:
        self._packs: dict[str, RevisionPack] = {}

    def generate_due_pack(
        self,
        pack_id: str,
        due_items: list[dict[str, Any]],
        max_items: int = 20,
    ) -> RevisionPack:
        """Generate a pack from items due for review."""
        sorted_items = sorted(
            due_items,
            key=lambda x: x.get("next_review", ""),
        )
        selected = sorted_items[:max_items]

        pack = RevisionPack(
            pack_id=pack_id,
            pack_type="due_review",
            items=selected,
            metadata={
                "total_due": len(due_items),
                "selected": len(selected),
                "strategy": "oldest_first",
            },
        )
        self._packs[pack_id] = pack
        logger.info("revision_pack.generated", pack_id=pack_id, items=len(selected))
        return pack

    def generate_weak_pack(
        self,
        pack_id: str,
        weak_items: list[dict[str, Any]],
        max_items: int = 15,
    ) -> RevisionPack:
        """Generate a pack focusing on weak/low-retention items."""
        sorted_items = sorted(
            weak_items,
            key=lambda x: x.get("retention_score", 1.0),
        )
        selected = sorted_items[:max_items]

        pack = RevisionPack(
            pack_id=pack_id,
            pack_type="weak_focus",
            items=selected,
            metadata={
                "total_weak": len(weak_items),
                "selected": len(selected),
                "strategy": "lowest_retention_first",
            },
        )
        self._packs[pack_id] = pack
        logger.info("revision_pack.generated_weak", pack_id=pack_id, items=len(selected))
        return pack

    def generate_mixed_pack(
        self,
        pack_id: str,
        due_items: list[dict[str, Any]],
        weak_items: list[dict[str, Any]],
        max_items: int = 20,
        weak_ratio: float = 0.4,
    ) -> RevisionPack:
        """Generate a mixed pack with both due and weak items."""
        weak_count = min(int(max_items * weak_ratio), len(weak_items))
        due_count = max_items - weak_count

        selected_weak = sorted(
            weak_items,
            key=lambda x: x.get("retention_score", 1.0),
        )[:weak_count]

        selected_due = sorted(
            due_items,
            key=lambda x: x.get("next_review", ""),
        )[:due_count]

        combined = selected_weak + selected_due

        pack = RevisionPack(
            pack_id=pack_id,
            pack_type="mixed",
            items=combined,
            metadata={
                "weak_items": weak_count,
                "due_items": due_count,
                "weak_ratio": weak_ratio,
                "strategy": "balanced",
            },
        )
        self._packs[pack_id] = pack
        logger.info("revision_pack.generated_mixed", pack_id=pack_id, items=len(combined))
        return pack

    def generate_cram_pack(
        self,
        pack_id: str,
        all_items: list[dict[str, Any]],
        max_items: int = 50,
    ) -> RevisionPack:
        """Generate a cram pack for exam prep — high volume, short intervals."""
        sorted_items = sorted(
            all_items,
            key=lambda x: x.get("retention_score", 1.0),
        )
        selected = sorted_items[:max_items]

        pack = RevisionPack(
            pack_id=pack_id,
            pack_type="cram",
            items=selected,
            metadata={
                "total_items": len(all_items),
                "selected": len(selected),
                "strategy": "exam_cram",
                "interval_override": 1,
            },
        )
        self._packs[pack_id] = pack
        logger.info("revision_pack.generated_cram", pack_id=pack_id, items=len(selected))
        return pack

    def get_pack(self, pack_id: str) -> RevisionPack | None:
        """Get a generated pack by ID."""
        return self._packs.get(pack_id)

    def list_packs(self) -> list[dict[str, Any]]:
        """List all generated packs."""
        return [
            {
                "pack_id": p.pack_id,
                "pack_type": p.pack_type,
                "item_count": len(p.items),
            }
            for p in self._packs.values()
        ]

    def delete_pack(self, pack_id: str) -> bool:
        """Delete a generated pack."""
        if pack_id in self._packs:
            del self._packs[pack_id]
            return True
        return False

    def reset(self) -> None:
        """Clear all generated packs."""
        self._packs.clear()
