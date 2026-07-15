"""High-level AI facade — composes prompts, memory, MCP registry, orchestration, usage."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Sequence

import httpx
import structlog

from studyos_api.ai.langsmith_tracing import trace_chat_call, record_trace_outputs
from studyos_api.ai.mcp.registry import MCPConnectorRegistry
from studyos_api.ai.memory.context import SessionConversationMemory
from studyos_api.ai.prompts.registry import PromptRegistry
from studyos_api.ai.protocols import LLMProvider, UsageSink
from studyos_api.ai.provider_factory import build_llm_chain
from studyos_api.ai.retry import FallbackOrchestrator
from studyos_api.ai.types import ChatMessage, CompletionRequest, CompletionResult, StreamChunk
from studyos_api.core.config import Settings

logger = structlog.get_logger(__name__)


class AIService:
    """Application entrypoint for chat + tools (MCP) — keep route handlers thin."""

    def __init__(
        self,
        *,
        settings: Settings,
        http_client: httpx.AsyncClient,
        usage_sink: UsageSink,
        conversation_memory: SessionConversationMemory | None = None,
        mcp_registry: MCPConnectorRegistry | None = None,
        llm_chain: Sequence[LLMProvider] | None = None,
    ) -> None:
        self._settings = settings
        self._usage = usage_sink
        chain = llm_chain if llm_chain is not None else build_llm_chain(settings, http_client)
        self._orch = FallbackOrchestrator(settings=settings, ordered_providers=chain)
        self._prompts = PromptRegistry.default()
        self._memory = conversation_memory or SessionConversationMemory(
            max_messages=settings.ai_memory_max_messages,
            ttl_seconds=settings.ai_memory_session_ttl_seconds,
        )
        self._mcp = mcp_registry or MCPConnectorRegistry(settings=settings, http_client=http_client)

    @property
    def mcp(self) -> MCPConnectorRegistry:
        return self._mcp

    def _session_key(self, user_sub: str | None, conversation_key: str | None) -> str | None:
        if not conversation_key or not user_sub:
            return None
        return f"{user_sub}:{conversation_key}"

    def _merge_messages(
        self,
        *,
        user_sub: str | None,
        conversation_key: str | None,
        incoming: list[ChatMessage],
    ) -> list[ChatMessage]:
        key = self._session_key(user_sub, conversation_key)
        if key is None:
            return incoming[-self._settings.ai_memory_max_messages :]
        prior = self._memory.get_messages(key)
        merged = (prior + incoming)[-self._settings.ai_memory_max_messages :]
        return merged

    def _persist_turn(
        self,
        *,
        user_sub: str | None,
        conversation_key: str | None,
        merged: list[ChatMessage],
        assistant_text: str,
    ) -> None:
        key = self._session_key(user_sub, conversation_key)
        if key is None:
            return
        self._memory.set_messages(
            key, [*merged, ChatMessage(role="assistant", content=assistant_text)]
        )

    async def complete_chat(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None,
        temperature: float,
        max_tokens: int | None,
        prompt_id: str | None,
        prompt_variables: dict[str, str],
        conversation_key: str | None,
        user_sub: str | None,
        request_id: str | None,
    ) -> CompletionResult:
        merged = self._merge_messages(
            user_sub=user_sub,
            conversation_key=conversation_key,
            incoming=messages,
        )
        if prompt_id is not None:
            system_text = self._prompts.render(prompt_id, **prompt_variables)
            merged = [ChatMessage(role="system", content=system_text)] + [
                m for m in merged if m.role != "system"
            ]
        req = CompletionRequest(
            messages=merged,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )
        logger.info("ai.chat_start", request_id=request_id, user_sub=user_sub, model=model)
        with trace_chat_call(
            user_sub=user_sub or "anonymous",
            model=model or "default",
            provider_id="unknown",
            request_id=request_id,
        ) as trace_ctx:
            result = await self._orch.complete(req)
            record_trace_outputs(
                run_id=trace_ctx["run_id"],
                outputs={"text": result.text},
                token_usage={
                    "prompt_tokens": result.usage.prompt_tokens,
                    "completion_tokens": result.usage.completion_tokens,
                    "total_tokens": result.usage.total_tokens,
                },
            )
        self._persist_turn(
            user_sub=user_sub,
            conversation_key=conversation_key,
            merged=merged,
            assistant_text=result.text,
        )
        await self._usage.record(
            provider_id=result.provider_id,
            model=result.model,
            usage=result.usage,
            request_id=request_id,
            user_sub=user_sub,
        )
        return result

    async def stream_chat(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None,
        temperature: float,
        max_tokens: int | None,
        prompt_id: str | None,
        prompt_variables: dict[str, str],
        conversation_key: str | None,
        user_sub: str | None,
        request_id: str | None,
    ) -> AsyncIterator[str]:
        merged = self._merge_messages(
            user_sub=user_sub,
            conversation_key=conversation_key,
            incoming=messages,
        )
        if prompt_id is not None:
            system_text = self._prompts.render(prompt_id, **prompt_variables)
            merged = [ChatMessage(role="system", content=system_text)] + [
                m for m in merged if m.role != "system"
            ]
        req = CompletionRequest(
            messages=merged,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        logger.info("ai.chat_stream_start", request_id=request_id, user_sub=user_sub, model=model)
        full: list[str] = []
        last_usage_chunk: StreamChunk | None = None
        async for chunk in self._orch.complete_stream(req):
            payload = {"delta": chunk.delta, "done": chunk.done}
            if chunk.usage is not None:
                payload["usage"] = {
                    "prompt_tokens": chunk.usage.prompt_tokens,
                    "completion_tokens": chunk.usage.completion_tokens,
                    "total_tokens": chunk.usage.total_tokens,
                }
            full.append(chunk.delta)
            if chunk.done and chunk.usage is not None:
                last_usage_chunk = chunk
            yield f"data: {json.dumps(payload)}\n\n"
        text = "".join(full)
        self._persist_turn(
            user_sub=user_sub,
            conversation_key=conversation_key,
            merged=merged,
            assistant_text=text,
        )
        if last_usage_chunk and last_usage_chunk.usage is not None:
            u = last_usage_chunk.usage
            await self._usage.record(
                provider_id=last_usage_chunk.provider_id or "unknown",
                model=last_usage_chunk.model or model or "unknown",
                usage=u,
                request_id=request_id,
                user_sub=user_sub,
            )
