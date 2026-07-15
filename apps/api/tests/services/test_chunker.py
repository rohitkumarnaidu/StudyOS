"""Tests for chunker service."""

import pytest

from studyos_api.services.chunker import (
    TextChunk,
    recursive_split,
    chunk_document,
    _merge_splits,
    _split_by_chars,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
)


class TestTextChunk:
    def test_token_estimate(self):
        chunk = TextChunk(content="hello world " * 40, chunk_index=0, source_id="test")
        assert chunk.token_estimate == len(chunk.content) // 4

    def test_metadata_default_empty(self):
        chunk = TextChunk(content="test", chunk_index=0, source_id="test")
        assert chunk.metadata == {}

    def test_metadata_custom(self):
        chunk = TextChunk(content="test", chunk_index=0, source_id="test", metadata={"key": "val"})
        assert chunk.metadata == {"key": "val"}


class TestRecursiveSplit:
    def test_empty_text(self):
        assert recursive_split("") == []

    def test_small_text(self):
        result = recursive_split("hello")
        assert result == ["hello"]

    def test_split_by_newlines(self):
        text = "line1\nline2\nline3"
        result = recursive_split(text, chunk_size=20)
        assert len(result) >= 1
        assert all(len(c) <= 20 for c in result)

    def test_split_by_sentences(self):
        text = "First sentence. Second sentence. Third sentence."
        result = recursive_split(text, chunk_size=20)
        assert len(result) >= 1

    def test_split_by_spaces(self):
        text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10"
        result = recursive_split(text, chunk_size=30)
        assert len(result) >= 1
        assert all(len(c) <= 30 for c in result)

    def test_custom_separators(self):
        text = "a|b|c|d|e|f"
        result = recursive_split(text, separators=["|", ""], chunk_size=5)
        assert len(result) >= 1

    def test_overlap_preserved(self):
        text = "word1 word2 word3 word4 word5 word6 word7 word8"
        result = recursive_split(text, chunk_size=20, chunk_overlap=5)
        assert len(result) >= 2


class TestSplitByChars:
    def test_split_short_text(self):
        result = _split_by_chars("hello", chunk_size=10, chunk_overlap=2)
        assert result == ["hello"]

    def test_split_long_text(self):
        result = _split_by_chars("a" * 50, chunk_size=10, chunk_overlap=2)
        assert len(result) >= 5
        assert all(len(c) <= 10 for c in result)


class TestMergeSplits:
    def test_merge_small_splits(self):
        splits = ["hello", "world", "test"]
        result = _merge_splits(splits, " ", chunk_size=50, chunk_overlap=5)
        assert len(result) >= 1

    def test_merge_empty_splits(self):
        result = _merge_splits([], " ", chunk_size=50, chunk_overlap=5)
        assert result == []


class TestChunkDocument:
    def test_chunk_document_basic(self):
        text = "This is a test document with some content for chunking."
        chunks = chunk_document(text, source_id="doc-1")
        assert len(chunks) >= 1
        assert all(isinstance(c, TextChunk) for c in chunks)
        assert chunks[0].source_id == "doc-1"
        assert chunks[0].chunk_index == 0

    def test_chunk_document_with_metadata(self):
        text = "Document with metadata."
        chunks = chunk_document(text, source_id="doc-2", metadata={"author": "test"})
        assert all(c.metadata == {"author": "test"} for c in chunks)

    def test_chunk_document_custom_size(self):
        text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10"
        chunks = chunk_document(text, source_id="doc-3", chunk_size=20, chunk_overlap=5)
        assert len(chunks) >= 2

    def test_chunk_document_empty(self):
        chunks = chunk_document("", source_id="doc-4")
        assert chunks == []

    def test_chunk_document_indices_sequential(self):
        text = "a" * 1000
        chunks = chunk_document(text, source_id="doc-5", chunk_size=100)
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))
