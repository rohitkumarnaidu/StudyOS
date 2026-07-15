"""Note structurer — AI-powered structuring of extracted PDF text."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ConceptCard:
    """A structured concept extracted from notes."""

    title: str
    definition: str
    examples: list[str] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "definition": self.definition,
            "examples": self.examples,
            "formulas": self.formulas,
            "tags": self.tags,
        }


@dataclass
class StructuredNote:
    """Fully structured note with concepts, summary, and metadata."""

    title: str
    summary: str
    concepts: list[ConceptCard] = field(default_factory=list)
    key_formulas: list[str] = field(default_factory=list)
    chapter_tags: list[str] = field(default_factory=list)
    estimated_study_time: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "concepts": [c.to_dict() for c in self.concepts],
            "key_formulas": self.key_formulas,
            "chapter_tags": self.chapter_tags,
            "estimated_study_time": self.estimated_study_time,
        }


class NoteStructurer:
    """Structure raw extracted text into organized study notes."""

    def __init__(self) -> None:
        pass

    def structure(self, raw_text: str, title: str = "") -> StructuredNote:
        """Structure raw text into organized note format."""
        note = StructuredNote(
            title=title or "Untitled Note",
            summary=self._generate_summary(raw_text),
            concepts=self._extract_concepts(raw_text),
            key_formulas=self._extract_formulas(raw_text),
            chapter_tags=self._detect_chapter_tags(raw_text),
            estimated_study_time=self._estimate_study_time(raw_text),
        )
        logger.info(
            "note.structured",
            title=note.title,
            concepts=len(note.concepts),
            tags=len(note.chapter_tags),
        )
        return note

    def _generate_summary(self, text: str) -> str:
        """Generate a summary from raw text."""
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 20]
        return ". ".join(sentences[:3]) + "." if sentences else "No summary available."

    def _extract_concepts(self, text: str) -> list[ConceptCard]:
        """Extract concept cards from text."""
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
        concepts = []
        for i, para in enumerate(paragraphs[:10]):
            first_line = para.split("\n")[0][:80]
            concepts.append(ConceptCard(
                title=first_line,
                definition=para[:200],
                tags=[f"concept-{i+1}"],
            ))
        return concepts

    def _extract_formulas(self, text: str) -> list[str]:
        """Extract potential formulas from text."""
        formulas = []
        for line in text.split("\n"):
            line = line.strip()
            if any(c in line for c in ["=", "∫", "∑", "√", "π", "²", "³"]):
                formulas.append(line)
        return formulas[:10]

    def _detect_chapter_tags(self, text: str) -> list[str]:
        """Detect chapter/topic tags from text."""
        tags = []
        lower = text.lower()
        subject_keywords = ["physics", "chemistry", "biology", "math", "organic", "inorganic"]
        for kw in subject_keywords:
            if kw in lower:
                tags.append(kw)
        return tags

    def _estimate_study_time(self, text: str) -> int:
        """Estimate study time in minutes based on content length."""
        word_count = len(text.split())
        return max(5, word_count // 200)
