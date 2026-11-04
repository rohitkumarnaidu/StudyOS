"""Tests for semantic search and RAG pipeline."""

import pytest

from studyos_api.services.semantic_search import RAGPipeline, SemanticSearchService


class MockPipeline:
    """Mock embedding pipeline for testing."""

    def __init__(self) -> None:
        self._dim = 10

    async def process_document(
        self, text: str, source_id: str, metadata: dict | None = None
    ) -> list[dict]:
        chunks = [
            {
                "content": text[i : i + 50],
                "source_id": source_id,
                "chunk_index": j,
                "embedding": [0.1] * self._dim,
                "token_estimate": 12,
                "metadata": metadata or {},
            }
            for j, i in enumerate(range(0, len(text), 50))
        ]
        return chunks

    async def embed(self, text: str) -> list[float]:
        return [0.1] * self._dim

    async def search_by_similarity(
        self, query: str, stored: list[dict], top_k: int = 5
    ) -> list[dict]:
        scored = []
        for item in stored:
            scored.append({**item, "similarity_score": 0.85 - len(scored) * 0.1})
        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:top_k]


class TestSemanticSearchService:
    @pytest.fixture
    def service(self) -> SemanticSearchService:
        return SemanticSearchService(pipeline=MockPipeline())

    @pytest.mark.asyncio
    async def test_index_document(self, service: SemanticSearchService) -> None:
        count = await service.index_document("Test document content here.", "doc-1")
        assert count >= 1

    @pytest.mark.asyncio
    async def test_index_document_with_metadata(self, service: SemanticSearchService) -> None:
        count = await service.index_document(
            "Biology notes on cell structure.",
            "doc-2",
            metadata={"subject": "Biology"},
        )
        assert count >= 1

    @pytest.mark.asyncio
    async def test_search(self, service: SemanticSearchService) -> None:
        await service.index_document(
            "Photosynthesis is the process by which plants convert sunlight.", "doc-1"
        )
        await service.index_document("Mitochondria are the powerhouse of the cell.", "doc-2")

        results = await service.search("plants energy", top_k=2)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_search_by_source_ids(self, service: SemanticSearchService) -> None:
        await service.index_document("Physics content about forces.", "doc-1")
        await service.index_document("Chemistry content about bonds.", "doc-2")

        results = await service.search("forces", source_ids=["doc-1"])
        assert all(r["source_id"] == "doc-1" for r in results)

    @pytest.mark.asyncio
    async def test_search_empty_index(self, service: SemanticSearchService) -> None:
        results = await service.search("query")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_with_min_score(self, service: SemanticSearchService) -> None:
        await service.index_document("Test content.", "doc-1")
        results = await service.search("test", min_score=0.9)
        assert all(r["similarity_score"] >= 0.9 for r in results)

    @pytest.mark.asyncio
    async def test_remove_document(self, service: SemanticSearchService) -> None:
        await service.index_document("Content to remove.", "doc-remove")
        result = await service.remove_document("doc-remove")
        assert result is True

    @pytest.mark.asyncio
    async def test_remove_nonexistent_document(self, service: SemanticSearchService) -> None:
        result = await service.remove_document("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_index_stats(self, service: SemanticSearchService) -> None:
        await service.index_document("Doc one content.", "doc-1")
        await service.index_document("Doc two content.", "doc-2")
        stats = await service.get_index_stats()
        assert stats["document_count"] == 2
        assert stats["total_chunks"] >= 2
        assert "doc-1" in stats["source_ids"]
        assert "doc-2" in stats["source_ids"]


class TestRAGPipeline:
    @pytest.fixture
    def rag(self) -> RAGPipeline:
        search = SemanticSearchService(pipeline=MockPipeline())
        return RAGPipeline(search_service=search, max_context_chunks=3)

    @pytest.mark.asyncio
    async def test_query(self, rag: RAGPipeline) -> None:
        await rag._search.index_document(
            "NEET biology covers cell structure, genetics, and evolution.",
            "doc-1",
        )
        result = await rag.query("What is cell structure?")
        assert result["question"] == "What is cell structure?"
        assert "context" in result
        assert "prompt" in result
        assert "source_chunks" in result

    @pytest.mark.asyncio
    async def test_query_empty_index(self, rag: RAGPipeline) -> None:
        result = await rag.query("Some question?")
        assert result["question"] == "Some question?"
        assert result["context"] == ""
        assert "No relevant context found" in result["prompt"]

    @pytest.mark.asyncio
    async def test_query_with_sources(self, rag: RAGPipeline) -> None:
        await rag._search.index_document(
            "Physics: Newton's laws of motion describe force and acceleration.",
            "doc-physics",
        )
        result = await rag.query_with_sources("Newton's laws?")
        assert "sources" in result
        if result["sources"]:
            source = result["sources"][0]
            assert "source_id" in source
            assert "similarity_score" in source
            assert "preview" in source

    @pytest.mark.asyncio
    async def test_query_by_source_ids(self, rag: RAGPipeline) -> None:
        await rag._search.index_document("Biology content about DNA.", "doc-bio")
        await rag._search.index_document("Physics content about waves.", "doc-phys")

        result = await rag.query("DNA structure?", source_ids=["doc-bio"])
        assert result["question"] == "DNA structure?"

    @pytest.mark.asyncio
    async def test_build_context(self, rag: RAGPipeline) -> None:
        chunks = [
            {"content": "First chunk.", "source_id": "doc-1", "chunk_index": 0},
            {"content": "Second chunk.", "source_id": "doc-1", "chunk_index": 1},
        ]
        context = rag._build_context(chunks)
        assert "[1] First chunk." in context
        assert "[2] Second chunk." in context

    @pytest.mark.asyncio
    async def test_build_context_empty(self, rag: RAGPipeline) -> None:
        context = rag._build_context([])
        assert context == ""

    @pytest.mark.asyncio
    async def test_build_prompt_with_context(self, rag: RAGPipeline) -> None:
        prompt = rag._build_prompt("What is X?", "Context about X.")
        assert "What is X?" in prompt
        assert "Context about X." in prompt
        assert "Use the following context" in prompt

    @pytest.mark.asyncio
    async def test_build_prompt_without_context(self, rag: RAGPipeline) -> None:
        prompt = rag._build_prompt("What is X?", "")
        assert "No relevant context found" in prompt

    @pytest.mark.asyncio
    async def test_max_context_chunks(self) -> None:
        search = SemanticSearchService(pipeline=MockPipeline())
        rag = RAGPipeline(search_service=search, max_context_chunks=2)
        await rag._search.index_document("A" * 200, "doc-1")
        result = await rag.query("test?")
        assert len(result["source_chunks"]) <= 2
