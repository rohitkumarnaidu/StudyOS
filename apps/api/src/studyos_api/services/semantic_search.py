"""Semantic search service — pgvector-backed semantic search with RAG."""

from __future__ import annotations

import structlog

from studyos_api.services.embedding_pipeline import EmbeddingPipeline

logger = structlog.get_logger(__name__)


class SemanticSearchService:
    """Semantic search over embedded document chunks."""

    def __init__(self, pipeline: EmbeddingPipeline | None = None) -> None:
        self._pipeline = pipeline or EmbeddingPipeline()
        self._store: dict[str, list[dict]] = {}

    async def index_document(
        self,
        text: str,
        source_id: str,
        metadata: dict | None = None,
    ) -> int:
        """Index a document by chunking and embedding it."""
        results = await self._pipeline.process_document(text, source_id, metadata)
        self._store[source_id] = results
        logger.info("semantic_search.indexed", source_id=source_id, chunks=len(results))
        return len(results)

    async def search(
        self,
        query: str,
        source_ids: list[str] | None = None,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[dict]:
        """Search across indexed documents semantically."""
        all_embeddings = []
        if source_ids:
            for sid in source_ids:
                if sid in self._store:
                    all_embeddings.extend(self._store[sid])
        else:
            for chunks in self._store.values():
                all_embeddings.extend(chunks)

        if not all_embeddings:
            return []

        results = await self._pipeline.search_by_similarity(query, all_embeddings, top_k * 2)
        filtered = [r for r in results if r["similarity_score"] >= min_score]
        return filtered[:top_k]

    async def remove_document(self, source_id: str) -> bool:
        """Remove a document from the search index."""
        if source_id in self._store:
            del self._store[source_id]
            logger.info("semantic_search.removed", source_id=source_id)
            return True
        return False

    async def get_index_stats(self) -> dict:
        """Get statistics about the search index."""
        total_chunks = sum(len(chunks) for chunks in self._store.values())
        return {
            "document_count": len(self._store),
            "total_chunks": total_chunks,
            "source_ids": list(self._store.keys()),
        }


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for NotebookLM-style Q&A."""

    def __init__(
        self,
        search_service: SemanticSearchService | None = None,
        max_context_chunks: int = 5,
    ) -> None:
        self._search = search_service or SemanticSearchService()
        self._max_context_chunks = max_context_chunks

    async def query(
        self,
        question: str,
        source_ids: list[str] | None = None,
    ) -> dict:
        """Retrieve relevant context and prepare for AI generation."""
        context_chunks = await self._search.search(
            question,
            source_ids=source_ids,
            top_k=self._max_context_chunks,
        )

        context_text = self._build_context(context_chunks)

        return {
            "question": question,
            "context": context_text,
            "source_chunks": context_chunks,
            "chunk_count": len(context_chunks),
            "prompt": self._build_prompt(question, context_text),
        }

    async def query_with_sources(
        self,
        question: str,
        source_ids: list[str] | None = None,
    ) -> dict:
        """Query with source attribution for each chunk."""
        result = await self.query(question, source_ids)
        result["sources"] = [
            {
                "source_id": c["source_id"],
                "chunk_index": c["chunk_index"],
                "similarity_score": round(c["similarity_score"], 4),
                "preview": c["content"][:200],
            }
            for c in result["source_chunks"]
        ]
        return result

    def _build_context(self, chunks: list[dict]) -> str:
        if not chunks:
            return ""
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(f"[{i}] {chunk['content']}")
        return "\n\n".join(parts)

    def _build_prompt(self, question: str, context: str) -> str:
        if not context:
            return f"Question: {question}\n\nNo relevant context found."

        return (
            f"Use the following context to answer the question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
