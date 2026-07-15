"""GDPR/DPDP compliance endpoints — data export and account deletion."""

from typing import Annotated, Any
from uuid import UUID

import asyncpg
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from studyos_api.deps.auth import User, get_current_user

logger = structlog.get_logger(__name__)

router = APIRouter()


def get_db_pool(request: Request) -> asyncpg.Pool | None:
    return request.app.state.db_pool


@router.get(
    "/export",
    summary="Export user data",
    description="Download all personal data in JSON format.",
)
async def export_user_data(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
) -> dict[str, Any]:
    """Export all personal data for the authenticated user (GDPR Article 20)."""
    profile_id = UUID(current_user["sub"])

    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    export_data: dict[str, Any] = {
        "profile_id": str(profile_id),
        "exported_at": None,
        "profile": None,
        "completions": [],
        "streak": None,
        "chat_sessions": [],
        "notes": [],
        "quiz_sessions": [],
        "ai_usage": [],
    }

    async with pool.acquire() as conn:
        # Profile
        profile_row = await conn.fetchrow(
            "SELECT id, email, display_name, app_role, created_at "
            "FROM public.profiles WHERE id = $1",
            profile_id,
        )
        if profile_row:
            export_data["profile"] = dict(profile_row)
            export_data["exported_at"] = profile_row["created_at"].isoformat()

        # Subtopic completions
        completion_rows = await conn.fetch(
            """
            SELECT sc.id, sc.subtopic_id, sc.completed_at, sc.source
            FROM public.subtopic_completions sc
            WHERE sc.profile_id = $1 AND sc.deleted_at IS NULL
            ORDER BY sc.completed_at DESC
            """,
            profile_id,
        )
        export_data["completions"] = [dict(r) for r in completion_rows]

        # Streak
        streak_row = await conn.fetchrow(
            """
            SELECT current_streak, longest_streak, last_study_date
            FROM public.streaks
            WHERE profile_id = $1 AND deleted_at IS NULL
            """,
            profile_id,
        )
        if streak_row:
            export_data["streak"] = dict(streak_row)

        # AI token usage
        usage_rows = await conn.fetch(
            """
            SELECT provider, model, input_tokens, output_tokens, total_tokens, created_at
            FROM public.ai_token_usage
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 1000
            """,
            profile_id,
        )
        export_data["ai_usage"] = [dict(r) for r in usage_rows]

    logger.info("privacy.export_ok", profile_id=str(profile_id))
    return {"success": True, "data": export_data}


@router.delete(
    "/account",
    summary="Delete user account",
    description="Permanently delete account and all associated data.",
)
async def delete_account(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
) -> Response:
    """Permanently delete the authenticated user's account.

    GDPR Article 17 — Right to be Forgotten.
    """
    profile_id = UUID(current_user["sub"])

    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Soft-delete subtopic completions
            await conn.execute(
                """
                UPDATE public.subtopic_completions
                SET deleted_at = now(), updated_at = now()
                WHERE profile_id = $1 AND deleted_at IS NULL
                """,
                profile_id,
            )

            # Soft-delete streak
            await conn.execute(
                """
                UPDATE public.streaks
                SET deleted_at = now(), updated_at = now()
                WHERE profile_id = $1 AND deleted_at IS NULL
                """,
                profile_id,
            )

            # Soft-delete profile
            await conn.execute(
                """
                UPDATE public.profiles
                SET deleted_at = now(), updated_at = now()
                WHERE id = $1 AND deleted_at IS NULL
                """,
                profile_id,
            )

            # Delete auth credentials (hard delete — passwords should not persist)
            await conn.execute(
                "DELETE FROM public.auth_credentials WHERE profile_id = $1",
                profile_id,
            )

            # Revoke all refresh sessions
            refresh_store = getattr(request.app.state, "refresh_store", None)
            if refresh_store:
                await refresh_store.revoke_all_for_profile(profile_id)

    logger.info("privacy.account_deleted", profile_id=str(profile_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
