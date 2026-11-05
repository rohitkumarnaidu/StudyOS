"""Text chunking service — recursive character split for embedding pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


@dataclass(frozen=True)
class TextChunk:
    """A single chunk of text with metadata."""

    content: str
    chunk_index: int
    source_id: str
    metadata: dict = field(default_factory=dict)

    @property
    def token_estimate(self) -> int:
        return len(self.content) // 4


def recursive_split(
    text: str,
    separators: list[str] | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Recursively split text by separators until chunks fit within size limit."""
    if separators is None:
        separators = list(DEFAULT_SEPARATORS)

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    for i, separator in enumerate(separators):
        splits = text.split(separator) if separator else list(text)
        splits = [s for s in splits if s]

        if len(splits) <= 1:
            continue

        chunks = _merge_splits(splits, separator, chunk_size, chunk_overlap)

        good, bad = [], []
        for c in chunks:
            (good if len(c) <= chunk_size else bad).append(c)

        if not bad:
            return good

        refined = list(good)
        for chunk in bad:
            refined.extend(recursive_split(chunk, separators[i + 1 :], chunk_size, chunk_overlap))
        return refined

    return _split_by_chars(text, chunk_size, chunk_overlap)


def chunk_document(
    text: str,
    source_id: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    metadata: dict | None = None,
) -> list[TextChunk]:
    """Split a document into chunks with metadata."""
    raw_chunks = recursive_split(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return [
        TextChunk(
            content=chunk,
            chunk_index=i,
            source_id=source_id,
            metadata=metadata or {},
        )
        for i, chunk in enumerate(raw_chunks)
    ]


def _merge_splits(
    splits: list[str],
    separator: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    chunks: list[str] = []
    current_parts: list[str] = []
    current_len = 0

    for split in splits:
        combined_len = current_len + len(separator) + len(split) if current_parts else len(split)

        if combined_len > chunk_size and current_parts:
            chunks.append(separator.join(current_parts))
            current_parts = _get_overlap(current_parts, separator, chunk_overlap, chunk_size, split)
            current_len = _parts_len(current_parts, separator)

        current_parts.append(split)
        current_len = _parts_len(current_parts, separator)

    if current_parts:
        chunks.append(separator.join(current_parts))

    return chunks


def _parts_len(parts: list[str], separator: str) -> int:
    if not parts:
        return 0
    return sum(len(p) for p in parts) + len(separator) * (len(parts) - 1)


def _get_overlap(
    parts: list[str],
    separator: str,
    chunk_overlap: int,
    chunk_size: int,
    next_split: str,
) -> list[str]:
    """Get overlap parts ensuring the next split can fit."""
    max_overlap = chunk_size - len(next_split) - len(separator)
    effective_overlap = min(chunk_overlap, max_overlap)

    if effective_overlap <= 0:
        return []

    result: list[str] = []
    acc = 0
    for part in reversed(parts):
        add_len = len(part) + len(separator)
        if acc + add_len > effective_overlap:
            break
        result.insert(0, part)
        acc += add_len
    return result


def _split_by_chars(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - chunk_overlap
        if start >= end:
            start = end
    return chunks
