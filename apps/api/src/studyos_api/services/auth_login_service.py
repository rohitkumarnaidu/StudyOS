"""Email/password login orchestration (DB or demo fallback)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import structlog

from studyos_api.core.config import Settings
from studyos_api.security.passwords import verify_password
from studyos_api.services.refresh_sessions import RefreshSessionStore

if TYPE_CHECKING:
    import asyncpg

logger = structlog.get_logger(__name__)

# Must match `supabase/seed.sql` demo password (`demo`) Argon2id string.
_DEMO_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$ryKpKxCo8Vg4v8L9tA6ksA$"
    "hoWXAqDmIYqdNtx+DaVYnLAB8qxginedT2utnPISbHA"
)


def _roles_from_app_role(app_role: str) -> list[str]:
    return [app_role]


class AuthLoginService:
    def __init__(
        self,
        *,
        pool: asyncpg.Pool | None,
        refresh_store: RefreshSessionStore,
        settings: Settings,
    ) -> None:
        self._pool = pool
        self._store = refresh_store
        self._settings = settings

    async def authenticate(
        self,
        *,
        email: str,
        password: str,
        user_agent: str | None,
        ip: str | None,
    ) -> tuple[uuid.UUID, str, list[str]] | None:
        """
        Validate credentials.
        Returns (profile_id, subject, roles) or None.
        """
        if self._pool is None:
            if email.strip().lower() != self._settings.demo_login_email.lower():
                return None
            if not verify_password(password, _DEMO_PASSWORD_HASH):
                logger.info("auth.login_failed", reason="bad_password", mode="memory_demo")
                return None
            # Deterministic demo profile id from seed.sql
            demo_id = uuid.UUID("77777777-7777-4777-8777-777777777777")
            logger.info("auth.login_ok", mode="memory_demo", profile_id=str(demo_id))
            return demo_id, self._settings.demo_login_email, _roles_from_app_role("student")

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT p.id, p.email, p.app_role::text AS app_role, ac.password_hash
                FROM public.profiles p
                INNER JOIN public.auth_credentials ac ON ac.profile_id = p.id
                WHERE lower(p.email) = lower($1) AND p.deleted_at IS NULL
                """,
                email.strip(),
            )
        if row is None:
            logger.info("auth.login_failed", reason="unknown_user")
            return None
        if not verify_password(password, row["password_hash"]):
            logger.info("auth.login_failed", reason="bad_password")
            return None
        profile_id: uuid.UUID = row["id"]
        email_out: str = row["email"] or str(profile_id)
        roles = _roles_from_app_role(row["app_role"])
        logger.info("auth.login_ok", profile_id=str(profile_id))
        return profile_id, email_out, roles
