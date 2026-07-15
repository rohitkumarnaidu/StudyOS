"""Extended tests for note embedder — covering uncovered lines."""

from unittest.mock import MagicMock, patch

import pytest

from studyos_api.services.note_embedder import (
    EmbeddedChunk,
    NoteEmbedder,
    RecursiveChunker,
    TextChunk,
    cosine_similarity,
)


@pytest.mark.unit
class TestTextChunk:
    def test_to_dict_truncates_content(self) -> None:
        long_content = "word " * 100
        chunk = TextChunk(chunk_id="c1", content=long_content, page_number=3)
        result = chunk.to_dict()
        assert len(result["content"]) <= 200
        assert result["page_number"] == 3
        assert result["chunk_id"] == "c1"

    def test_to_dict_with_metadata(self) -> None:
        chunk = TextChunk(
            chunk_id="c2",
            content="short",
            metadata={"source": "test", "index": 1},
        )
        result = chunk.to_dict()
        assert result["metadata"] == {"source": "test", "index": 1}


@pytest.mark.unit
class TestRecursiveChunker:
    def test_chunk_small_text(self) -> None:
        chunker = RecursiveChunker(chunk_size=10, overlap=3)
        chunks = chunker.chunk("one two three four five")
        assert len(chunks) >= 1
        assert all(isinstance(c, TextChunk) for c in chunks)

    def test_chunk_with_page_number(self) -> None:
        chunker = RecursiveChunker(chunk_size=5, overlap=2)
        chunks = chunker.chunk("a b c d e f g", page_number=5)
        assert all(c.page_number == 5 for c in chunks)

    def test_chunk_empty_text(self) -> None:
        chunker = RecursiveChunker(chunk_size=10, overlap=3)
        chunks = chunker.chunk("")
        assert chunks == []

    def test_chunk_overlap(self) -> None:
        chunker = RecursiveChunker(chunk_size=3, overlap=1)
        text = "w1 w2 w3 w4 w5 w6"
        chunks = chunker.chunk(text)
        assert len(chunks) >= 2
        first_content = chunks[0].content
        second_content = chunks[1].content
        overlap_words = set(first_content.split()) & set(second_content.split())
        assert len(overlap_words) >= 1


@pytest.mark.unit
class TestNoteEmbedderMockEmbedding:
    def test_embed_note_without_api_key(self) -> None:
        embedder = NoteEmbedder(api_key="")
        result = embedder.embed_note("hello world test content", "note-1")
        assert len(result) >= 1
        assert all(isinstance(e, EmbeddedChunk) for e in result)
        assert all(len(e.embedding) == 16 for e in result)

    def test_embed_note_chunks_have_note_id_prefix(self) -> None:
        embedder = NoteEmbedder(api_key="")
        result = embedder.embed_note("a b c d e", "my-note")
        for chunk in result:
            assert chunk.chunk_id.startswith("my-note-")
            assert chunk.metadata["note_id"] == "my-note"

    def test_mock_embedding_deterministic(self) -> None:
        embedder = NoteEmbedder(api_key="")
        emb1 = embedder._mock_embedding("same text")
        emb2 = embedder._mock_embedding("same text")
        assert emb1 == emb2

    def test_mock_embedding_different_inputs(self) -> None:
        embedder = NoteEmbedder(api_key="")
        emb1 = embedder._mock_embedding("text one")
        emb2 = embedder._mock_embedding("text two")
        assert emb1 != emb2


@pytest.mark.unit
class TestNoteEmbedderRealApi:
    def test_real_api_call_success(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3, 0.4]}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response) as mock_post:
            embedder = NoteEmbedder(api_key="sk-test-key", model="text-embedding-3-small")
            result = embedder._get_embedding("test text")

            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args[1]
            assert call_kwargs["headers"]["Authorization"] == "Bearer sk-test-key"
            assert call_kwargs["json"]["model"] == "text-embedding-3-small"
            assert result == [0.1, 0.2, 0.3, 0.4]

    def test_real_api_truncates_long_text(self) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"embedding": [0.1]}]}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.post", return_value=mock_response) as mock_post:
            embedder = NoteEmbedder(api_key="sk-test")
            long_text = "x " * 5000
            embedder._get_embedding(long_text)

            call_json = mock_post.call_args[1]["json"]
            assert len(call_json["input"]) <= 8000

    def test_real_api_raises_on_error(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock(side_effect=Exception("API error"))

        with patch("httpx.post", return_value=mock_response):
            embedder = NoteEmbedder(api_key="sk-test")
            with pytest.raises(Exception, match="API error"):
                embedder._get_embedding("test")


@pytest.mark.unit
class TestCosineSimilarity:
    def test_identical_vectors(self) -> None:
        v = [1.0, 0.0, 0.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self) -> None:
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_empty_vector_a(self) -> None:
        assert cosine_similarity([], [1.0, 2.0]) == 0.0

    def test_empty_vector_b(self) -> None:
        assert cosine_similarity([1.0, 2.0], []) == 0.0

    def test_both_empty_vectors(self) -> None:
        assert cosine_similarity([], []) == 0.0

    def test_zero_norm_vector(self) -> None:
        zero = [0.0, 0.0, 0.0]
        normal = [1.0, 2.0, 3.0]
        assert cosine_similarity(zero, normal) == 0.0
        assert cosine_similarity(normal, zero) == 0.0

    def test_opposite_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_partial_similarity(self) -> None:
        a = [1.0, 2.0, 3.0]
        b = [2.0, 4.0, 6.0]
        assert cosine_similarity(a, b) == pytest.approx(1.0)
