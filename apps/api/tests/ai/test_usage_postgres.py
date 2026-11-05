"""Tests for PostgresUsageStore."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.ai.types import TokenUsage
from studyos_api.ai.usage_postgres import PostgresUsageStore


class _MockAcquireCtx:
    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, *args):
        pass


class TestPostgresUsageStoreRecord:
    @pytest.fixture
    def mock_conn(self):
        conn = AsyncMock()
        conn.execute = AsyncMock()
        return conn

    @pytest.fixture
    def mock_pool(self, mock_conn):
        pool = MagicMock()
        pool.acquire = MagicMock(return_value=_MockAcquireCtx(mock_conn))
        return pool

    @pytest.mark.asyncio
    async def test_record_success(self, mock_pool, mock_conn):
        store = PostgresUsageStore(pool=mock_pool)
        usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)

        await store.record(
            provider_id="openai",
            model="gpt-4",
            usage=usage,
            request_id="req-1",
            user_sub="user-123",
        )

        mock_conn.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_record_with_none_user_sub(self, mock_pool, mock_conn):
        store = PostgresUsageStore(pool=mock_pool)
        usage = TokenUsage(prompt_tokens=5, completion_tokens=10, total_tokens=15)

        await store.record(
            provider_id="ollama",
            model="llama3",
            usage=usage,
            request_id=None,
            user_sub=None,
        )

        mock_conn.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_record_exception_logged(self, mock_pool, mock_conn):
        mock_conn.execute = AsyncMock(side_effect=Exception("DB error"))
        store = PostgresUsageStore(pool=mock_pool)
        usage = TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2)

        await store.record(
            provider_id="openai",
            model="gpt-4",
            usage=usage,
            request_id="req-1",
            user_sub="user-123",
        )


class TestPostgresUsageStoreUserSummary:
    @pytest.fixture
    def mock_conn(self):
        conn = AsyncMock()
        conn.fetch = AsyncMock(return_value=[])
        return conn

    @pytest.fixture
    def mock_pool(self, mock_conn):
        pool = MagicMock()
        pool.acquire = MagicMock(return_value=_MockAcquireCtx(mock_conn))
        return pool

    @pytest.mark.asyncio
    async def test_user_usage_summary_empty(self, mock_pool, mock_conn):
        store = PostgresUsageStore(pool=mock_pool)
        result = await store.user_usage_summary("user-123", days=30)
        assert result == []

    @pytest.mark.asyncio
    async def test_user_usage_summary_with_data(self, mock_pool, mock_conn):
        mock_conn.fetch = AsyncMock(
            return_value=[
                {
                    "provider": "openai",
                    "model": "gpt-4",
                    "request_count": 10,
                    "total_input_tokens": 100,
                    "total_output_tokens": 200,
                    "total_tokens": 300,
                }
            ]
        )
        store = PostgresUsageStore(pool=mock_pool)
        result = await store.user_usage_summary("user-123", days=7)

        assert len(result) == 1
        assert result[0]["provider"] == "openai"
        assert result[0]["total_tokens"] == 300

    @pytest.mark.asyncio
    async def test_user_usage_summary_default_days(self, mock_pool, mock_conn):
        store = PostgresUsageStore(pool=mock_pool)
        await store.user_usage_summary("user-123")
        mock_conn.fetch.assert_awaited_once()


class TestPostgresUsageStoreGlobalDaily:
    @pytest.fixture
    def mock_conn(self):
        conn = AsyncMock()
        conn.fetch = AsyncMock(return_value=[])
        return conn

    @pytest.fixture
    def mock_pool(self, mock_conn):
        pool = MagicMock()
        pool.acquire = MagicMock(return_value=_MockAcquireCtx(mock_conn))
        return pool

    @pytest.mark.asyncio
    async def test_global_daily_usage_empty(self, mock_pool, mock_conn):
        store = PostgresUsageStore(pool=mock_pool)
        result = await store.global_daily_usage(days=7)
        assert result == []

    @pytest.mark.asyncio
    async def test_global_daily_usage_with_data(self, mock_pool, mock_conn):
        mock_conn.fetch = AsyncMock(
            return_value=[
                {
                    "usage_date": "2024-01-01",
                    "provider": "openai",
                    "request_count": 50,
                    "total_tokens": 5000,
                }
            ]
        )
        store = PostgresUsageStore(pool=mock_pool)
        result = await store.global_daily_usage(days=7)

        assert len(result) == 1
        assert result[0]["provider"] == "openai"

    @pytest.mark.asyncio
    async def test_global_daily_usage_default_days(self, mock_pool, mock_conn):
        store = PostgresUsageStore(pool=mock_pool)
        await store.global_daily_usage()
        mock_conn.fetch.assert_awaited_once()
