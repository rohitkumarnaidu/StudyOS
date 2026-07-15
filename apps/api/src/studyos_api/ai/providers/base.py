"""Optional base with non-native streaming fallback (single final chunk)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import replace

from studyos_api.ai.types import CompletionRequest, CompletionResult, StreamChunk


class AbstractLLMProvider(ABC):
    """Subclass for each vendor; override `complete` and optionally `complete_stream`."""

    @property
    @abstractmethod
    def provider_id(self) -> str: ...

    @abstractmethod
    async def complete(self, req: CompletionRequest) -> CompletionResult: ...

    def supports_streaming(self) -> bool:
        return True

    async def complete_stream(self, req: CompletionRequest) -> AsyncIterator[StreamChunk]:
        res = await self.complete(replace(req, stream=False))
        yield StreamChunk(
            delta=res.text,
            done=True,
            usage=res.usage,
            provider_id=res.provider_id,
            model=res.model,
        )
