"""Rotating refresh sessions (opaque tokens) — memory (dev/tests) or Postgres (prod)."""

from __future__ import annotations

import asyncio
import hashlib
import secrets
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import asyncpg


def hash_refresh(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RefreshContext:
    profile_id: uuid.UUID
    sub: str
    roles: list[str]
    family_id: uuid.UUID
    session_id: uuid.UUID


class RefreshSessionStore(ABC):
    @abstractmethod
    async def create_session(
        self,
        *,
        profile_id: uuid.UUID,
        sub: str,
        roles: list[str],
        family_id: uuid.UUID | None,
        user_agent: str | None,
        ip: str | None,
        ttl_seconds: int,
    ) -> tuple[str, datetime]:
        """Return opaque refresh token and absolute expiry."""

    @abstractmethod
    async def validate_and_rotate(
        self,
        refresh_token: str,
        *,
        user_agent: str | None,
        ip: str | None,
        ttl_seconds: int,
    ) -> tuple[RefreshContext, str, datetime] | None:
        """
        Validate refresh token, revoke the old row, issue a new token (same family_id).
        Returns (context, new_refresh_token, new_expires_at) or None.
        """

    @abstractmethod
    async def revoke_refresh(self, refresh_token: str) -> None:
        """Invalidate the presented refresh session and its rotation family."""

    @abstractmethod
    async def revoke_family(self, family_id: uuid.UUID) -> None:
        """Invalidate all refresh sessions in a rotation family (reuse / theft)."""


class MemoryRefreshStore(RefreshSessionStore):
    """In-process store — single worker only; use Postgres in production."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._sessions: dict[uuid.UUID, dict[str, Any]] = {}
        self._hash_index: dict[str, uuid.UUID] = {}

    async def create_session(
        self,
        *,
        profile_id: uuid.UUID,
        sub: str,
        roles: list[str],
        family_id: uuid.UUID | None,
        user_agent: str | None,
        ip: str | None,
        ttl_seconds: int,
    ) -> tuple[str, datetime]:
        sid = uuid.uuid4()
        fam = family_id or uuid.uuid4()
        secret = secrets.token_urlsafe(32)
        raw = f"{sid}:{secret}"
        h = hash_refresh(raw)
        exp = datetime.now(tz=UTC) + timedelta(seconds=ttl_seconds)
        async with self._lock:
            self._sessions[sid] = {
                "profile_id": profile_id,
                "sub": sub,
                "roles": roles,
                "family_id": fam,
                "hash": h,
                "expires_at": exp,
                "revoked": False,
                "user_agent": user_agent,
                "ip": ip,
            }
            self._hash_index[h] = sid
        return raw, exp

    async def _revoke_family_unlocked(self, family_id: uuid.UUID) -> None:
        for rec in self._sessions.values():
            if rec["family_id"] == family_id:
                rec["revoked"] = True

    async def revoke_family(self, family_id: uuid.UUID) -> None:
        async with self._lock:
            await self._revoke_family_unlocked(family_id)

    async def validate_and_rotate(
        self,
        refresh_token: str,
        *,
        user_agent: str | None,
        ip: str | None,
        ttl_seconds: int,
    ) -> tuple[RefreshContext, str, datetime] | None:
        parts = refresh_token.split(":", 1)
        if len(parts) != 2:
            return None
        try:
            sid = uuid.UUID(parts[0])
        except ValueError:
            return None
        h = hash_refresh(refresh_token)
        async with self._lock:
            rec = self._sessions.get(sid)
            if rec is None:
                return None
            if rec["revoked"]:
                await self._revoke_family_unlocked(rec["family_id"])
                return None
            if not secrets.compare_digest(rec["hash"], h):
                return None
            if rec["expires_at"] < datetime.now(tz=UTC):
                rec["revoked"] = True
                return None
            fam: uuid.UUID = rec["family_id"]
            profile_id: uuid.UUID = rec["profile_id"]
            sub: str = rec["sub"]
            roles: list[str] = list(rec["roles"])
            rec["revoked"] = True
            new_sid = uuid.uuid4()
            new_secret = secrets.token_urlsafe(32)
            new_raw = f"{new_sid}:{new_secret}"
            new_h = hash_refresh(new_raw)
            exp = datetime.now(tz=UTC) + timedelta(seconds=ttl_seconds)
            self._sessions[new_sid] = {
                "profile_id": profile_id,
                "sub": sub,
                "roles": roles,
                "family_id": fam,
                "hash": new_h,
                "expires_at": exp,
                "revoked": False,
                "user_agent": user_agent,
                "ip": ip,
            }
            self._hash_index[new_h] = new_sid
            ctx = RefreshContext(
                profile_id=profile_id,
                sub=sub,
                roles=roles,
                family_id=fam,
                session_id=new_sid,
            )
            return ctx, new_raw, exp

    async def revoke_refresh(self, refresh_token: str) -> None:
        parts = refresh_token.split(":", 1)
        if len(parts) != 2:
            return
        try:
            sid = uuid.UUID(parts[0])
        except ValueError:
            return
        h = hash_refresh(refresh_token)
        async with self._lock:
            rec = self._sessions.get(sid)
            if rec is None:
                return
            if not secrets.compare_digest(rec["hash"], h):
                return
            await self._revoke_family_unlocked(rec["family_id"])

    async def revoke_all_for_profile(self, profile_id: uuid.UUID) -> None:
        async with self._lock:
            for rec in self._sessions.values():
                if rec["profile_id"] == profile_id:
                    rec["revoked"] = True


class PostgresRefreshStore(RefreshSessionStore):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create_session(
        self,
        *,
        profile_id: uuid.UUID,
        sub: str,
        roles: list[str],
        family_id: uuid.UUID | None,
        user_agent: str | None,
        ip: str | None,
        ttl_seconds: int,
    ) -> tuple[str, datetime]:
        _ = sub
        _ = roles
        sid = uuid.uuid4()
        fam = family_id or uuid.uuid4()
        secret = secrets.token_urlsafe(32)
        raw = f"{sid}:{secret}"
        h = hash_refresh(raw)
        exp = datetime.now(tz=UTC) + timedelta(seconds=ttl_seconds)
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO public.auth_sessions (
                  id, profile_id, family_id, refresh_token_hash, user_agent, ip, expires_at
                )
                VALUES ($1, $2, $3, $4, $5, $6::inet, $7)
                """,
                sid,
                profile_id,
                fam,
                h,
                user_agent,
                ip,
                exp,
            )
        return raw, exp

    async def revoke_family(self, family_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE public.auth_sessions
                SET revoked_at = now()
                WHERE family_id = $1 AND revoked_at IS NULL
                """,
                family_id,
            )

    async def validate_and_rotate(
        self,
        refresh_token: str,
        *,
        user_agent: str | None,
        ip: str | None,
        ttl_seconds: int,
    ) -> tuple[RefreshContext, str, datetime] | None:
        parts = refresh_token.split(":", 1)
        if len(parts) != 2:
            return None
        try:
            old_id = uuid.UUID(parts[0])
        except ValueError:
            return None
        h = hash_refresh(refresh_token)
        new_sid = uuid.uuid4()
        new_secret = secrets.token_urlsafe(32)
        new_raw = f"{new_sid}:{new_secret}"
        new_h = hash_refresh(new_raw)
        new_exp = datetime.now(tz=UTC) + timedelta(seconds=ttl_seconds)
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    """
                    SELECT
                      s.id,
                      s.profile_id,
                      s.family_id,
                      s.refresh_token_hash,
                      s.revoked_at,
                      s.expires_at,
                      p.email::text AS email,
                      p.app_role::text AS app_role
                    FROM public.auth_sessions s
                    JOIN public.profiles p ON p.id = s.profile_id
                    WHERE s.id = $1
                    FOR UPDATE
                    """,
                    old_id,
                )
                if row is None:
                    return None
                if row["revoked_at"] is not None:
                    await conn.execute(
                        """
                        UPDATE public.auth_sessions
                        SET revoked_at = now()
                        WHERE family_id = $1 AND revoked_at IS NULL
                        """,
                        row["family_id"],
                    )
                    return None
                if row["expires_at"] < datetime.now(tz=UTC):
                    await conn.execute(
                        "UPDATE public.auth_sessions SET revoked_at = now() WHERE id = $1",
                        old_id,
                    )
                    return None
                if not secrets.compare_digest(row["refresh_token_hash"], h):
                    return None
                roles = [row["app_role"]]
                sub = row["email"] or str(row["profile_id"])
                profile_id = row["profile_id"]
                fam = row["family_id"]
                await conn.execute(
                    """
                    UPDATE public.auth_sessions
                    SET revoked_at = now(), replaced_by = $2
                    WHERE id = $1
                    """,
                    old_id,
                    new_sid,
                )
                await conn.execute(
                    """
                    INSERT INTO public.auth_sessions (
                      id, profile_id, family_id, refresh_token_hash, user_agent, ip, expires_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6::inet, $7)
                    """,
                    new_sid,
                    profile_id,
                    fam,
                    new_h,
                    user_agent,
                    ip,
                    new_exp,
                )
        ctx = RefreshContext(
            profile_id=profile_id,
            sub=sub,
            roles=roles,
            family_id=fam,
            session_id=new_sid,
        )
        return ctx, new_raw, new_exp

    async def revoke_refresh(self, refresh_token: str) -> None:
        h = hash_refresh(refresh_token)
        async with self._pool.acquire() as conn:
            fid = await conn.fetchval(
                """
                SELECT family_id
                FROM public.auth_sessions
                WHERE refresh_token_hash = $1 AND revoked_at IS NULL
                LIMIT 1
                """,
                h,
            )
            if fid is None:
                return
            await conn.execute(
                """
                UPDATE public.auth_sessions
                SET revoked_at = now()
                WHERE family_id = $1 AND revoked_at IS NULL
                """,
                fid,
            )

    async def revoke_all_for_profile(self, profile_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE public.auth_sessions
                SET revoked_at = now()
                WHERE profile_id = $1 AND revoked_at IS NULL
                """,
                profile_id,
            )
