"""Postgres-backed AI token usage store for persistent tracking."""

from __future__ import annotations

import asyncpg
import structlog

from studyos_api.ai.protocols import UsageSink
from studyos_api.ai.types import TokenUsage

logger = structlog.get_logger(__name__)


class PostgresUsageStore(UsageSink):
    """Durable Postgres store for AI token usage analytics and billing."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def record(
        self,
        *,
        provider_id: str,
        model: str,
        usage: TokenUsage,
        request_id: str | None,
        user_sub: str | None,
    ) -> None:
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO public.ai_token_usage
                        (user_id, provider, model, request_id,
                         input_tokens, output_tokens, total_tokens)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    user_sub,
                    provider_id,
                    model,
                    request_id,
                    usage.prompt_tokens,
                    usage.completion_tokens,
                    usage.total_tokens,
                )
        except Exception:
            logger.exception("ai.usage.persist_failed", provider=provider_id, model=model)

    async def user_usage_summary(
        self,
        user_id: str,
        *,
        days: int = 30,
    ) -> list[dict[str, object]]:
        """Get usage summary for a user over the last N days."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    provider,
                    model,
                    COUNT(*) AS request_count,
                    SUM(input_tokens) AS total_input_tokens,
                    SUM(output_tokens) AS total_output_tokens,
                    SUM(total_tokens) AS total_tokens
                FROM public.ai_token_usage
                WHERE user_id = $1
                  AND created_at >= now() - INTERVAL '1 day' * $2
                GROUP BY provider, model
                ORDER BY total_tokens DESC
                """,
                user_id,
                days,
            )
            return [dict(r) for r in rows]

    async def global_daily_usage(
        self,
        *,
        days: int = 7,
    ) -> list[dict[str, object]]:
        """Get global daily usage across all users."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    DATE(created_at) AS usage_date,
                    provider,
                    COUNT(*) AS request_count,
                    SUM(total_tokens) AS total_tokens
                FROM public.ai_token_usage
                WHERE created_at >= now() - INTERVAL '1 day' * $1
                GROUP BY DATE(created_at), provider
                ORDER BY usage_date DESC, provider
                """,
                days,
            )
            return [dict(r) for r in rows]
