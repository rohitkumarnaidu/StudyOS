"""Ollama HTTP provider."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from studyos_api.ai.providers.base import AbstractLLMProvider
from studyos_api.ai.types import CompletionRequest, CompletionResult, StreamChunk, TokenUsage


class OllamaProvider(AbstractLLMProvider):
    """Local / self-hosted models via Ollama HTTP API."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        *,
        base_url: str,
        default_model: str,
    ) -> None:
        self._http = client
        self._base = base_url.rstrip("/")
        self._default_model = default_model

    @property
    def provider_id(self) -> str:
        return "ollama"

    def _model(self, req: CompletionRequest) -> str:
        return req.model or self._default_model

    def _payload(self, req: CompletionRequest, *, stream: bool) -> dict[str, object]:
        options: dict[str, object] = {"temperature": req.temperature}
        if req.max_tokens is not None:
            options["num_predict"] = req.max_tokens
        return {
            "model": self._model(req),
            "messages": [{"role": m.role, "content": m.content} for m in req.messages],
            "stream": stream,
            "options": options,
        }

    async def complete(self, req: CompletionRequest) -> CompletionResult:
        payload = self._payload(req, stream=False)
        r = await self._http.post(f"{self._base}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
        text = str((data.get("message") or {}).get("content") or "")
        pt = int(data.get("prompt_eval_count") or 0)
        ct = int(data.get("eval_count") or 0)
        if ct == 0 and text:
            ct = max(len(text) // 4, 1)
        usage = TokenUsage(prompt_tokens=pt, completion_tokens=ct, total_tokens=pt + ct)
        return CompletionResult(
            text=text,
            usage=usage,
            provider_id=self.provider_id,
            model=self._model(req),
            finish_reason="stop" if data.get("done") else None,
        )

    async def complete_stream(self, req: CompletionRequest) -> AsyncIterator[StreamChunk]:
        payload = self._payload(req, stream=True)
        last_total = ""
        async with self._http.stream("POST", f"{self._base}/api/chat", json=payload) as r:
            r.raise_for_status()
            async for raw in r.aiter_lines():
                if not raw.strip():
                    continue
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                msg = data.get("message") or {}
                piece = str(msg.get("content") or "")
                if piece.startswith(last_total):
                    delta = piece[len(last_total) :]
                    last_total = piece
                else:
                    delta = piece
                    last_total += piece
                if delta:
                    yield StreamChunk(
                        delta=delta,
                        done=False,
                        provider_id=self.provider_id,
                        model=self._model(req),
                    )
                if data.get("done"):
                    pt = int(data.get("prompt_eval_count") or 0)
                    ct = int(data.get("eval_count") or 0)
                    usage = TokenUsage(prompt_tokens=pt, completion_tokens=ct, total_tokens=pt + ct)
                    yield StreamChunk(
                        delta="",
                        done=True,
                        usage=usage,
                        provider_id=self.provider_id,
                        model=self._model(req),
                    )
                    return
