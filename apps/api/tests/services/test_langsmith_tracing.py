"""Tests for langsmith_tracing service."""

import os
from unittest.mock import patch

from studyos_api.ai.langsmith_tracing import trace_chat_call, record_trace_outputs


class TestTraceChatCall:
    def test_trace_chat_call_disabled(self):
        with patch("studyos_api.ai.langsmith_tracing.LANGSMITH_TRACING_ENABLED", False):
            with trace_chat_call(
                user_sub="user-123",
                model="gpt-4",
                provider_id="openai",
                request_id="req-456",
            ) as trace_ctx:
                assert "run_id" in trace_ctx
                assert "trace_id" in trace_ctx

    def test_trace_chat_call_no_api_key(self):
        with patch("studyos_api.ai.langsmith_tracing.LANGSMITH_API_KEY", ""):
            with trace_chat_call(
                user_sub="user-123",
                model="gpt-4",
                provider_id="openai",
                request_id="req-456",
            ) as trace_ctx:
                assert "run_id" in trace_ctx

    def test_trace_chat_call_with_request_id(self):
        with patch("studyos_api.ai.langsmith_tracing.LANGSMITH_TRACING_ENABLED", False):
            with trace_chat_call(
                user_sub="user-123",
                model="gpt-4",
                provider_id="openai",
                request_id="my-req-id",
            ) as trace_ctx:
                assert trace_ctx["trace_id"] == "my-req-id"

    def test_trace_chat_call_without_request_id(self):
        with patch("studyos_api.ai.langsmith_tracing.LANGSMITH_TRACING_ENABLED", False):
            with trace_chat_call(
                user_sub="user-123",
                model="gpt-4",
                provider_id="openai",
                request_id=None,
            ) as trace_ctx:
                assert trace_ctx["trace_id"] == trace_ctx["run_id"]


class TestRecordTraceOutputs:
    def test_record_trace_outputs_disabled(self):
        with patch("studyos_api.ai.langsmith_tracing.LANGSMITH_TRACING_ENABLED", False):
            record_trace_outputs(
                run_id="test-run-id",
                outputs={"text": "Hello world"},
                token_usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            )

    def test_record_trace_outputs_no_api_key(self):
        with patch("studyos_api.ai.langsmith_tracing.LANGSMITH_API_KEY", ""):
            record_trace_outputs(
                run_id="test-run-id",
                outputs={"text": "Hello"},
                token_usage={"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
            )

    def test_record_trace_outputs_without_token_usage(self):
        with patch("studyos_api.ai.langsmith_tracing.LANGSMITH_TRACING_ENABLED", False):
            record_trace_outputs(
                run_id="test-run-id",
                outputs={"text": "Hello"},
                token_usage=None,
            )
