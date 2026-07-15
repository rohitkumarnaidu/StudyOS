"""Tests for PostgresRefreshStore."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.services.refresh_sessions import (
    PostgresRefreshStore,
    RefreshContext,
    hash_refresh,
)


class _MockAcquireCtx:
    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, *args):
        pass


class _MockTxCtx:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class TestPostgresRefreshStore:
    @pytest.fixture
    def mock_conn(self):
        conn = AsyncMock()
        conn.execute = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)
        conn.fetchval = AsyncMock(return_value=None)
        conn.transaction = MagicMock(return_value=_MockTxCtx())
        return conn

    @pytest.fixture
    def mock_pool(self, mock_conn):
        pool = MagicMock()
        pool.acquire = MagicMock(return_value=_MockAcquireCtx(mock_conn))
        return pool

    @pytest.fixture
    def store(self, mock_pool):
        return PostgresRefreshStore(pool=mock_pool)

    @pytest.mark.asyncio
    async def test_create_session(self, store, mock_pool, mock_conn):
        profile_id = uuid.uuid4()
        token, exp = await store.create_session(
            profile_id=profile_id,
            sub="user@example.com",
            roles=["user"],
            family_id=None,
            user_agent="test",
            ip="127.0.0.1",
            ttl_seconds=3600,
        )

        assert ":" in token
        assert exp > datetime.now(tz=UTC)
        mock_conn.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_session_with_family_id(self, store, mock_pool, mock_conn):
        family_id = uuid.uuid4()
        token, exp = await store.create_session(
            profile_id=uuid.uuid4(),
            sub="user@example.com",
            roles=["user"],
            family_id=family_id,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )

        assert ":" in token
        mock_conn.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_revoke_family(self, store, mock_pool, mock_conn):
        family_id = uuid.uuid4()
        await store.revoke_family(family_id)
        mock_conn.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_validate_and_rotate_malformed_token(self, store):
        result = await store.validate_and_rotate(
            "no-colon",
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_bad_uuid(self, store):
        result = await store.validate_and_rotate(
            "not-a-uuid:secret",
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_session_not_found(self, store, mock_conn):
        mock_conn.fetchrow = AsyncMock(return_value=None)
        token = f"{uuid.uuid4()}:secret"
        result = await store.validate_and_rotate(
            token,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_revoked_session(self, store, mock_conn):
        sid = uuid.uuid4()
        fam = uuid.uuid4()
        mock_conn.fetchrow = AsyncMock(return_value={
            "id": sid,
            "profile_id": uuid.uuid4(),
            "family_id": fam,
            "refresh_token_hash": "wrong_hash",
            "revoked_at": datetime.now(tz=UTC),
            "expires_at": datetime.now(tz=UTC) + timedelta(hours=1),
            "email": "user@example.com",
            "app_role": "student",
        })
        token = f"{sid}:secret"
        result = await store.validate_and_rotate(
            token,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_expired_session(self, store, mock_conn):
        sid = uuid.uuid4()
        mock_conn.fetchrow = AsyncMock(return_value={
            "id": sid,
            "profile_id": uuid.uuid4(),
            "family_id": uuid.uuid4(),
            "refresh_token_hash": "wrong_hash",
            "revoked_at": None,
            "expires_at": datetime.now(tz=UTC) - timedelta(seconds=1),
            "email": "user@example.com",
            "app_role": "student",
        })
        token = f"{sid}:secret"
        result = await store.validate_and_rotate(
            token,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_hash_mismatch(self, store, mock_conn):
        sid = uuid.uuid4()
        mock_conn.fetchrow = AsyncMock(return_value={
            "id": sid,
            "profile_id": uuid.uuid4(),
            "family_id": uuid.uuid4(),
            "refresh_token_hash": hash_refresh("different_secret"),
            "revoked_at": None,
            "expires_at": datetime.now(tz=UTC) + timedelta(hours=1),
            "email": "user@example.com",
            "app_role": "student",
        })
        token = f"{sid}:secret"
        result = await store.validate_and_rotate(
            token,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_success(self, store, mock_conn):
        sid = uuid.uuid4()
        profile_id = uuid.uuid4()
        fam = uuid.uuid4()
        secret = "my_secret_value"
        raw = f"{sid}:{secret}"
        h = hash_refresh(raw)

        mock_conn.fetchrow = AsyncMock(return_value={
            "id": sid,
            "profile_id": profile_id,
            "family_id": fam,
            "refresh_token_hash": h,
            "revoked_at": None,
            "expires_at": datetime.now(tz=UTC) + timedelta(hours=1),
            "email": "user@example.com",
            "app_role": "student",
        })

        result = await store.validate_and_rotate(
            raw,
            user_agent="test",
            ip="127.0.0.1",
            ttl_seconds=3600,
        )

        assert result is not None
        ctx, new_token, new_exp = result
        assert isinstance(ctx, RefreshContext)
        assert ctx.profile_id == profile_id
        assert ctx.sub == "user@example.com"
        assert ctx.roles == ["student"]
        assert ctx.family_id == fam
        assert new_token != raw

    @pytest.mark.asyncio
    async def test_revoke_refresh_not_found(self, store, mock_conn):
        mock_conn.fetchval = AsyncMock(return_value=None)
        await store.revoke_refresh(f"{uuid.uuid4()}:secret")
        mock_conn.fetchval.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_revoke_refresh_success(self, store, mock_conn):
        fam = uuid.uuid4()
        mock_conn.fetchval = AsyncMock(return_value=fam)
        await store.revoke_refresh(f"{uuid.uuid4()}:secret")
        assert mock_conn.execute.await_count >= 1
