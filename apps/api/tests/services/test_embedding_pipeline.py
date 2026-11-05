"""Tests for embedding_pipeline service."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.services.embedding_pipeline import (
    DEFAULT_EMBEDDING_DIM,
    EmbeddingPipeline,
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
    _cosine_similarity,
)


class TestCosineSimilarity:
    def test_identical_vectors(self):
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        assert _cosine_similarity(a, b) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert _cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = [1.0, 0.0, 0.0]
        b = [-1.0, 0.0, 0.0]
        assert _cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector(self):
        a = [0.0, 0.0, 0.0]
        b = [1.0, 1.0, 1.0]
        assert _cosine_similarity(a, b) == 0.0

    def test_both_zero_vectors(self):
        a = [0.0, 0.0]
        b = [0.0, 0.0]
        assert _cosine_similarity(a, b) == 0.0


class TestOpenAIEmbeddingProvider:
    def test_init_default(self):
        provider = OpenAIEmbeddingProvider()
        assert provider._model == "text-embedding-3-small"
        assert provider._dimensions == DEFAULT_EMBEDDING_DIM
        assert provider._client is None

    def test_init_custom(self):
        provider = OpenAIEmbeddingProvider(
            api_key="sk-test",
            model="text-embedding-3-large",
            dimensions=3072,
        )
        assert provider._api_key == "sk-test"
        assert provider._model == "text-embedding-3-large"
        assert provider._dimensions == 3072

    def test_mock_embedding(self):
        provider = OpenAIEmbeddingProvider(api_key=None)
        result = provider._mock_embedding("test text")
        assert len(result) == DEFAULT_EMBEDDING_DIM
        assert all(0.0 <= v < 1.0 for v in result)

    def test_embed_without_api_key(self):
        provider = OpenAIEmbeddingProvider(api_key=None)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(provider.embed("hello world"))
        finally:
            loop.close()
        assert len(result) == DEFAULT_EMBEDDING_DIM

    def test_embed_batch_without_api_key(self):
        provider = OpenAIEmbeddingProvider(api_key=None)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(provider.embed_batch(["text1", "text2", "text3"]))
        finally:
            loop.close()
        assert len(results) == 3
        assert all(len(r) == DEFAULT_EMBEDDING_DIM for r in results)

    def test_ensure_client_no_api_key(self):
        provider = OpenAIEmbeddingProvider(api_key=None)
        provider._ensure_client()
        assert provider._client is None


class TestEmbeddingProvider:
    def test_base_embed_raises(self):
        provider = EmbeddingProvider()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            with pytest.raises(NotImplementedError):
                loop.run_until_complete(provider.embed("test"))
        finally:
            loop.close()

    def test_base_embed_batch_raises(self):
        provider = EmbeddingProvider()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            with pytest.raises(NotImplementedError):
                loop.run_until_complete(provider.embed_batch(["test"]))
        finally:
            loop.close()


class TestEmbeddingPipeline:
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.embed = AsyncMock(return_value=[0.1] * 10)
        provider.embed_batch = AsyncMock(return_value=[[0.1] * 10, [0.2] * 10])
        return provider

    @pytest.fixture
    def pipeline(self, mock_provider):
        return EmbeddingPipeline(provider=mock_provider, chunk_size=50, chunk_overlap=10)

    def test_process_document(self, pipeline, mock_provider):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                pipeline.process_document("This is a test document with some content.", "doc-1")
            )
        finally:
            loop.close()
        assert len(result) >= 1
        assert "embedding" in result[0]
        assert "content" in result[0]
        assert "chunk_index" in result[0]

    def test_process_document_empty(self, pipeline, mock_provider):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(pipeline.process_document("", "doc-empty"))
        finally:
            loop.close()
        assert result == []

    def test_process_document_with_metadata(self, pipeline, mock_provider):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                pipeline.process_document(
                    "Test content.",
                    "doc-meta",
                    metadata={"author": "test", "version": 1},
                )
            )
        finally:
            loop.close()
        assert len(result) >= 1
        assert result[0]["metadata"] == {"author": "test", "version": 1}

    def test_process_single(self, pipeline, mock_provider):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(pipeline.process_single("Single text embedding"))
        finally:
            loop.close()
        assert len(result) == 10

    def test_search_by_similarity(self, pipeline, mock_provider):
        stored = [
            {"content": "doc1", "embedding": [0.1] * 10},
            {"content": "doc2", "embedding": [0.9] * 10},
            {"content": "doc3", "embedding": [0.5] * 10},
        ]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                pipeline.search_by_similarity("query", stored, top_k=2)
            )
        finally:
            loop.close()
        assert len(result) == 2
        assert "similarity_score" in result[0]
        assert result[0]["similarity_score"] >= result[1]["similarity_score"]

    def test_search_by_similarity_default_top_k(self, pipeline, mock_provider):
        stored = [
            {"content": "doc1", "embedding": [0.1] * 10},
            {"content": "doc2", "embedding": [0.9] * 10},
        ]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(pipeline.search_by_similarity("query", stored))
        finally:
            loop.close()
        assert len(result) == 2
