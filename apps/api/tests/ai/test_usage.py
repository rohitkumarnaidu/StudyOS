"""Tests for AI usage tracking."""

import asyncio

from studyos_api.ai.types import TokenUsage
from studyos_api.ai.usage import (
    CompositeUsageSink,
    InMemoryUsageStore,
    LoggingUsageSink,
)


class TestInMemoryUsageStore:
    def test_record_and_retrieve(self):
        store = InMemoryUsageStore(max_events=10)
        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                store.record(
                    provider_id="openai",
                    model="gpt-4",
                    usage=usage,
                    request_id="req-1",
                    user_sub="user-1",
                )
            )
            events = loop.run_until_complete(store.recent(limit=10))
        finally:
            loop.close()
        assert len(events) == 1
        assert events[0].provider_id == "openai"
        assert events[0].model == "gpt-4"

    def test_record_multiple_events(self):
        store = InMemoryUsageStore(max_events=10)
        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            for i in range(5):
                loop.run_until_complete(
                    store.record(
                        provider_id="openai",
                        model="gpt-4",
                        usage=usage,
                        request_id=f"req-{i}",
                        user_sub="user-1",
                    )
                )
            events = loop.run_until_complete(store.recent(limit=10))
        finally:
            loop.close()
        assert len(events) == 5

    def test_recent_with_limit(self):
        store = InMemoryUsageStore(max_events=100)
        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            for i in range(20):
                loop.run_until_complete(
                    store.record(
                        provider_id="openai",
                        model="gpt-4",
                        usage=usage,
                        request_id=f"req-{i}",
                        user_sub="user-1",
                    )
                )
            events = loop.run_until_complete(store.recent(limit=5))
        finally:
            loop.close()
        assert len(events) == 5

    def test_max_events_bounded(self):
        store = InMemoryUsageStore(max_events=5)
        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            for i in range(10):
                loop.run_until_complete(
                    store.record(
                        provider_id="openai",
                        model="gpt-4",
                        usage=usage,
                        request_id=f"req-{i}",
                        user_sub="user-1",
                    )
                )
            events = loop.run_until_complete(store.recent(limit=100))
        finally:
            loop.close()
        assert len(events) == 5

    def test_empty_store(self):
        store = InMemoryUsageStore()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            events = loop.run_until_complete(store.recent(limit=10))
        finally:
            loop.close()
        assert events == []


class TestLoggingUsageSink:
    def test_record_logs_usage(self):
        sink = LoggingUsageSink()
        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                sink.record(
                    provider_id="ollama",
                    model="llama3",
                    usage=usage,
                    request_id=None,
                    user_sub=None,
                )
            )
        finally:
            loop.close()


class TestCompositeUsageSink:
    def test_record_to_multiple_sinks(self):
        store = InMemoryUsageStore(max_events=10)
        logger_sink = LoggingUsageSink()
        composite = CompositeUsageSink(store, logger_sink)
        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                composite.record(
                    provider_id="openai",
                    model="gpt-4",
                    usage=usage,
                    request_id="req-1",
                    user_sub="user-1",
                )
            )
            events = loop.run_until_complete(store.recent(limit=10))
        finally:
            loop.close()
        assert len(events) == 1
