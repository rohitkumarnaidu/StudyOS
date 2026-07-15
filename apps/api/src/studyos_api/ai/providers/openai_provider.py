"""OpenAI Chat Completions API (compatible with many OpenAI-style gateways)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from studyos_api.ai.providers.base import AbstractLLMProvider
from studyos_api.ai.types import CompletionRequest, CompletionResult, StreamChunk, TokenUsage


class OpenAIProvider(AbstractLLMProvider):
    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        api_key: str,
        base_url: str,
        default_model: str,
    ) -> None:
        self._http = client
        self._key = api_key
        self._base = base_url.rstrip("/")
        self._default_model = default_model

    @property
    def provider_id(self) -> str:
        return "openai"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
        }

    def _model(self, req: CompletionRequest) -> str:
        return req.model or self._default_model

    async def complete(self, req: CompletionRequest) -> CompletionResult:
        body: dict[str, object] = {
            "model": self._model(req),
            "messages": [{"role": m.role, "content": m.content} for m in req.messages],
            "temperature": req.temperature,
            "stream": False,
        }
        if req.max_tokens is not None:
            body["max_tokens"] = req.max_tokens
        r = await self._http.post(
            f"{self._base}/chat/completions",
            json=body,
            headers=self._headers(),
        )
        r.raise_for_status()
        data = r.json()
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        text = str(msg.get("content") or "")
        u = data.get("usage") or {}
        usage = TokenUsage(
            prompt_tokens=int(u.get("prompt_tokens") or 0),
            completion_tokens=int(u.get("completion_tokens") or 0),
            total_tokens=int(u.get("total_tokens") or 0),
        )
        return CompletionResult(
            text=text,
            usage=usage,
            provider_id=self.provider_id,
            model=str(body["model"]),
            finish_reason=str(choice.get("finish_reason") or "") or None,
        )

    async def complete_stream(self, req: CompletionRequest) -> AsyncIterator[StreamChunk]:
        body: dict[str, object] = {
            "model": self._model(req),
            "messages": [{"role": m.role, "content": m.content} for m in req.messages],
            "temperature": req.temperature,
            "stream": True,
        }
        if req.max_tokens is not None:
            body["max_tokens"] = req.max_tokens
        usage_out: TokenUsage | None = None
        async with self._http.stream(
            "POST",
            f"{self._base}/chat/completions",
            json=body,
            headers=self._headers(),
        ) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line.removeprefix("data: ").strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                u = data.get("usage")
                if isinstance(u, dict):
                    usage_out = TokenUsage(
                        prompt_tokens=int(u.get("prompt_tokens") or 0),
                        completion_tokens=int(u.get("completion_tokens") or 0),
                        total_tokens=int(u.get("total_tokens") or 0),
                    )
                choice = (data.get("choices") or [{}])[0]
                delta = str((choice.get("delta") or {}).get("content") or "")
                if delta:
                    yield StreamChunk(
                        delta=delta,
                        done=False,
                        provider_id=self.provider_id,
                        model=self._model(req),
                    )
        final_usage = usage_out or TokenUsage(0, 0, 0)
        yield StreamChunk(
            delta="",
            done=True,
            usage=final_usage,
            provider_id=self.provider_id,
            model=self._model(req),
        )
