"""Note embedder — chunk + embed + store in pgvector."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class TextChunk:
    """A chunk of text ready for embedding."""

    chunk_id: str
    content: str
    page_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content[:200],
            "page_number": self.page_number,
            "metadata": self.metadata,
        }


@dataclass
class EmbeddedChunk:
    """A chunk with its vector embedding."""

    chunk_id: str
    content: str
    embedding: list[float]
    page_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class RecursiveChunker:
    """Split text into overlapping chunks for embedding."""

    def __init__(self, chunk_size: int = 500, overlap: int = 100) -> None:
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str, page_number: int | None = None) -> list[TextChunk]:
        """Split text into overlapping chunks."""
        chunks = []
        words = text.split()
        start = 0

        while start < len(words):
            end = start + self._chunk_size
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunks.append(TextChunk(
                chunk_id=f"chunk-{start}-{len(chunk_text)}",
                content=chunk_text,
                page_number=page_number,
            ))

            start = end - self._overlap

        return chunks


class NoteEmbedder:
    """Embed note chunks using OpenAI embeddings (or mock)."""

    def __init__(self, api_key: str = "", model: str = "text-embedding-3-small") -> None:
        self._api_key = api_key
        self._model = model
        self._chunker = RecursiveChunker()

    def embed_note(self, text: str, note_id: str) -> list[EmbeddedChunk]:
        """Chunk and embed a full note."""
        chunks = self._chunker.chunk(text)
        embedded = []

        for chunk in chunks:
            embedding = self._get_embedding(chunk.content)
            embedded.append(EmbeddedChunk(
                chunk_id=f"{note_id}-{chunk.chunk_id}",
                content=chunk.content,
                embedding=embedding,
                page_number=chunk.page_number,
                metadata={"note_id": note_id},
            ))

        logger.info("note.embedded", note_id=note_id, chunks=len(embedded))
        return embedded

    def _get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for text."""
        if not self._api_key:
            return self._mock_embedding(text)

        import httpx
        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self._model, "input": text[:8000]},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

    def _mock_embedding(self, text: str) -> list[float]:
        """Generate deterministic mock embedding."""
        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()
        return [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
