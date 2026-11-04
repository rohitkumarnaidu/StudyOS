"""Embedding pipeline service — generates vector embeddings for text chunks."""

from __future__ import annotations

import structlog

from studyos_api.services.chunker import chunk_document

logger = structlog.get_logger(__name__)

DEFAULT_EMBEDDING_DIM = 1536


class EmbeddingProvider:
    """Base interface for embedding generation."""

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI text-embedding-3-small provider."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "text-embedding-3-small",
        dimensions: int = DEFAULT_EMBEDDING_DIM,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._dimensions = dimensions
        self._client: object | None = None

    def _ensure_client(self) -> None:
        if self._client is None and self._api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self._api_key)
            except ImportError:
                logger.warning("embedding.openai.import_error")

    async def embed(self, text: str) -> list[float]:
        self._ensure_client()
        if self._client is None:
            return self._mock_embedding(text)
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=text,
                dimensions=self._dimensions,
            )
            return response.data[0].embedding
        except Exception:
            logger.exception("embedding.openai.failed")
            return self._mock_embedding(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self._ensure_client()
        if self._client is None:
            return [self._mock_embedding(t) for t in texts]
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=texts,
                dimensions=self._dimensions,
            )
            return [d.embedding for d in response.data]
        except Exception:
            logger.exception("embedding.openai.batch_failed")
            return [self._mock_embedding(t) for t in texts]

    def _mock_embedding(self, text: str) -> list[float]:
        return [hash(text + str(i)) % 1000 / 1000.0 for i in range(self._dimensions)]


class EmbeddingPipeline:
    """Pipeline for chunking documents and generating embeddings."""

    def __init__(
        self,
        provider: EmbeddingProvider | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> None:
        self._provider = provider or OpenAIEmbeddingProvider()
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def process_document(
        self,
        text: str,
        source_id: str,
        metadata: dict | None = None,
    ) -> list[dict]:
        """Chunk a document and generate embeddings for each chunk."""
        chunks = chunk_document(
            text,
            source_id=source_id,
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            metadata=metadata,
        )

        if not chunks:
            return []

        texts = [c.content for c in chunks]
        embeddings = await self._provider.embed_batch(texts)

        results = []
        for chunk, embedding in zip(chunks, embeddings):
            results.append(
                {
                    "source_id": chunk.source_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "embedding": embedding,
                    "token_estimate": chunk.token_estimate,
                    "metadata": chunk.metadata,
                }
            )

        logger.info(
            "embedding_pipeline.processed",
            source_id=source_id,
            chunk_count=len(results),
        )
        return results

    async def process_single(
        self,
        text: str,
        source_id: str = "",
    ) -> list[float]:
        """Generate embedding for a single text (no chunking)."""
        return await self._provider.embed(text)

    async def search_by_similarity(
        self,
        query: str,
        stored_embeddings: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """Find most similar chunks to a query using cosine similarity."""
        query_embedding = await self._provider.embed(query)
        scored = []
        for item in stored_embeddings:
            score = _cosine_similarity(query_embedding, item["embedding"])
            scored.append({**item, "similarity_score": score})

        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:top_k]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
