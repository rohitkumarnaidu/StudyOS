"""Note search — hybrid search (keyword + semantic)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

from studyos_api.services.note_embedder import cosine_similarity

logger = structlog.get_logger(__name__)


@dataclass
class SearchResult:
    """A single search result."""

    note_id: str
    note_title: str
    chunk_content: str
    score: float
    page_number: int | None = None
    match_type: str = "keyword"

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_id": self.note_id,
            "note_title": self.note_title,
            "chunk_content": self.chunk_content[:200],
            "score": round(self.score, 3),
            "page_number": self.page_number,
            "match_type": self.match_type,
        }


@dataclass
class NoteDocument:
    """A searchable note document."""

    note_id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    chunks: list[dict[str, Any]] = field(default_factory=list)


class NoteSearch:
    """Hybrid search across notes (keyword + semantic)."""

    def __init__(self) -> None:
        self._index: dict[str, NoteDocument] = {}

    def index_note(self, note: NoteDocument) -> None:
        """Add a note to the search index."""
        self._index[note.note_id] = note
        logger.info("note.indexed", note_id=note.note_id, title=note.title)

    def remove_note(self, note_id: str) -> None:
        """Remove a note from the index."""
        self._index.pop(note_id, None)

    def search(
        self,
        query: str,
        chapter_id: str | None = None,
        top_k: int = 10,
    ) -> list[SearchResult]:
        """Search notes by keyword matching."""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for note in self._index.values():
            if chapter_id and chapter_id not in note.tags:
                continue

            note_lower = note.content.lower()
            title_lower = note.title.lower()

            title_score = sum(1 for w in query_words if w in title_lower)
            content_score = sum(1 for w in query_words if w in note_lower)
            score = title_score * 3 + content_score

            if score > 0:
                snippet = self._extract_snippet(note.content, query_words)
                results.append(SearchResult(
                    note_id=note.note_id,
                    note_title=note.title,
                    chunk_content=snippet,
                    score=score,
                    match_type="keyword",
                ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[SearchResult]:
        """Search notes by semantic similarity."""
        results = []

        for note in self._index.values():
            for chunk in note.chunks:
                sim = cosine_similarity(query_embedding, chunk.get("embedding", []))
                if sim > 0.3:
                    results.append(SearchResult(
                        note_id=note.note_id,
                        note_title=note.title,
                        chunk_content=chunk.get("content", "")[:200],
                        score=sim,
                        page_number=chunk.get("page_number"),
                        match_type="semantic",
                    ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def _extract_snippet(self, text: str, query_words: set[str]) -> str:
        """Extract a relevant snippet containing query words."""
        text_lower = text.lower()
        for word in query_words:
            idx = text_lower.find(word)
            if idx >= 0:
                start = max(0, idx - 50)
                end = min(len(text), idx + 150)
                snippet = text[start:end].strip()
                return ("..." if start > 0 else "") + snippet + ("..." if end < len(text) else "")
        return text[:200]

    def reset(self) -> None:
        """Clear the search index."""
        self._index.clear()
