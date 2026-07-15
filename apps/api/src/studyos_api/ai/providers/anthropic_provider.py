"""Anthropic Messages API (Claude)."""

from __future__ import annotations

import httpx

from studyos_api.ai.providers.base import AbstractLLMProvider
from studyos_api.ai.types import ChatMessage, CompletionRequest, CompletionResult, TokenUsage


def _split_system(messages: list[ChatMessage]) -> tuple[str, list[dict[str, str]]]:
    system_parts: list[str] = []
    out: list[dict[str, str]] = []
    for m in messages:
        if m.role == "system":
            system_parts.append(m.content)
        elif m.role in ("user", "assistant"):
            out.append({"role": m.role, "content": m.content})
    return "\n\n".join(system_parts), out


class AnthropicProvider(AbstractLLMProvider):
    """Claude via Anthropic Messages API (non-stream uses native HTTP; stream reuses base)."""

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
        return "anthropic"

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self._key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def _model(self, req: CompletionRequest) -> str:
        return req.model or self._default_model

    async def complete(self, req: CompletionRequest) -> CompletionResult:
        system, msgs = _split_system(req.messages)
        body: dict[str, object] = {
            "model": self._model(req),
            "max_tokens": req.max_tokens if req.max_tokens is not None else 4096,
            "messages": msgs,
            "temperature": req.temperature,
        }
        if system:
            body["system"] = system
        r = await self._http.post(
            f"{self._base}/v1/messages",
            json=body,
            headers=self._headers(),
        )
        r.raise_for_status()
        data = r.json()
        parts: list[str] = []
        for block in data.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text") or ""))
        text = "".join(parts)
        u = data.get("usage") or {}
        usage = TokenUsage(
            prompt_tokens=int(u.get("input_tokens") or 0),
            completion_tokens=int(u.get("output_tokens") or 0),
            total_tokens=int(u.get("input_tokens") or 0) + int(u.get("output_tokens") or 0),
        )
        return CompletionResult(
            text=text,
            usage=usage,
            provider_id=self.provider_id,
            model=self._model(req),
            finish_reason=str(data.get("stop_reason") or "") or None,
        )
