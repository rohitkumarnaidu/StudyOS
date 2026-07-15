"""Contracts for LLM providers and usage sinks — swap implementations without touching callers."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from studyos_api.ai.types import CompletionRequest, CompletionResult, StreamChunk

if TYPE_CHECKING:
    from studyos_api.ai.types import TokenUsage


@runtime_checkable
class LLMProvider(Protocol):
    """Any hosted or local model that speaks chat-style messages."""

    @property
    def provider_id(self) -> str: ...

    async def complete(self, req: CompletionRequest) -> CompletionResult: ...

    def supports_streaming(self) -> bool: ...

    def complete_stream(self, req: CompletionRequest) -> AsyncIterator[StreamChunk]: ...


@runtime_checkable
class UsageSink(Protocol):
    """Record token usage (wire to billing, warehouse, or metrics)."""

    async def record(
        self,
        *,
        provider_id: str,
        model: str,
        usage: "TokenUsage",
        request_id: str | None,
        user_sub: str | None,
    ) -> None: ...
