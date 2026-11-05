"""LangSmith tracing integration for AI service calls."""

from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY", "")
LANGSMITH_TRACING_ENABLED = os.environ.get("LANGSMITH_TRACING", "false").lower() == "true"
LANGSMITH_PROJECT = os.environ.get("LANGSMITH_PROJECT", "studyos")
LANGSMITH_ENDPOINT = os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")


@contextmanager
def trace_chat_call(
    *,
    user_sub: str,
    model: str,
    provider_id: str,
    request_id: str | None = None,
    chapter_context: str | None = None,
):
    """Context manager that wraps a chat call with LangSmith tracing."""
    run_id = str(uuid.uuid4())
    trace_id = request_id or run_id

    if not LANGSMITH_TRACING_ENABLED or not LANGSMITH_API_KEY:
        yield {"run_id": run_id, "trace_id": trace_id}
        return

    trace_payload = {
        "name": "chat_completion",
        "run_type": "llm",
        "id": run_id,
        "trace_id": trace_id,
        "session_id": LANGSMITH_PROJECT,
        "inputs": {
            "model": model,
            "provider": provider_id,
            "user_sub": user_sub,
            "chapter_context": chapter_context,
        },
        "tags": [provider_id, model, f"user:{user_sub}"],
        "extra": {
            "metadata": {
                "request_id": request_id,
                "project": LANGSMITH_PROJECT,
            },
        },
    }

    try:
        _send_trace("start", trace_payload)
        yield {"run_id": run_id, "trace_id": trace_id}
    except Exception as e:
        trace_payload["outputs"] = {"error": str(e)}
        trace_payload["status"] = "error"
        _send_trace("end", trace_payload)
        raise
    else:
        trace_payload["status"] = "success"
        _send_trace("end", trace_payload)


def record_trace_outputs(
    run_id: str,
    outputs: dict[str, Any],
    token_usage: dict[str, int] | None = None,
) -> None:
    """Record the outputs and token usage for a traced run."""
    if not LANGSMITH_TRACING_ENABLED or not LANGSMITH_API_KEY:
        return

    payload = {
        "id": run_id,
        "outputs": outputs,
        "events": [{"name": "token_usage", "data": token_usage}] if token_usage else [],
    }
    _send_trace("patch", payload)


def _send_trace(event_type: str, payload: dict[str, Any]) -> None:
    """Send a trace event to LangSmith API."""
    if not LANGSMITH_API_KEY:
        return

    headers = {
        "x-api-key": LANGSMITH_API_KEY,
        "Content-Type": "application/json",
    }

    url = f"{LANGSMITH_ENDPOINT}/runs"
    if event_type == "patch":
        url = f"{LANGSMITH_ENDPOINT}/runs/{payload.pop('id', '')}"

    try:
        import httpx

        with httpx.Client(timeout=5.0) as client:
            if event_type == "patch":
                client.patch(url, headers=headers, json=payload)
            else:
                client.post(url, headers=headers, json=payload)
    except Exception:
        logger.exception("langsmith.trace_failed", event_type=event_type)
