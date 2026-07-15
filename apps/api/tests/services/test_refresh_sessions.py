"""Tests for refresh session stores — MemoryRefreshStore."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from studyos_api.services.refresh_sessions import (
    MemoryRefreshStore,
    RefreshContext,
    hash_refresh,
)


class TestHashRefresh:
    def test_deterministic(self) -> None:
        h1 = hash_refresh("token123")
        h2 = hash_refresh("token123")
        assert h1 == h2

    def test_different_tokens(self) -> None:
        h1 = hash_refresh("token1")
        h2 = hash_refresh("token2")
        assert h1 != h2

    def test_sha256_length(self) -> None:
        h = hash_refresh("test")
        assert len(h) == 64


class TestMemoryRefreshStore:
    @pytest.fixture
    def store(self) -> MemoryRefreshStore:
        return MemoryRefreshStore()

    @pytest.mark.asyncio
    async def test_create_session(self, store: MemoryRefreshStore) -> None:
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

    @pytest.mark.asyncio
    async def test_create_session_with_family_id(self, store: MemoryRefreshStore) -> None:
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

    @pytest.mark.asyncio
    async def test_validate_and_rotate_success(self, store: MemoryRefreshStore) -> None:
        profile_id = uuid.uuid4()
        token, _ = await store.create_session(
            profile_id=profile_id,
            sub="user@example.com",
            roles=["user"],
            family_id=None,
            user_agent="test",
            ip="127.0.0.1",
            ttl_seconds=3600,
        )
        result = await store.validate_and_rotate(
            token,
            user_agent="test",
            ip="127.0.0.1",
            ttl_seconds=3600,
        )
        assert result is not None
        ctx, new_token, new_exp = result
        assert isinstance(ctx, RefreshContext)
        assert ctx.profile_id == profile_id
        assert ctx.sub == "user@example.com"
        assert ctx.roles == ["user"]
        assert new_token != token
        assert new_exp > datetime.now(tz=UTC)

    @pytest.mark.asyncio
    async def test_validate_and_rotate_invalid_token(self, store: MemoryRefreshStore) -> None:
        result = await store.validate_and_rotate(
            "invalid:token",
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_malformed(self, store: MemoryRefreshStore) -> None:
        result = await store.validate_and_rotate(
            "no-colon",
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_bad_uuid(self, store: MemoryRefreshStore) -> None:
        result = await store.validate_and_rotate(
            "not-a-uuid:secret",
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_expired(self, store: MemoryRefreshStore) -> None:
        profile_id = uuid.uuid4()
        token, _ = await store.create_session(
            profile_id=profile_id,
            sub="user@example.com",
            roles=["user"],
            family_id=None,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        # Manually expire the session
        parts = token.split(":", 1)
        sid = uuid.UUID(parts[0])
        store._sessions[sid]["expires_at"] = datetime.now(tz=UTC) - timedelta(seconds=1)

        result = await store.validate_and_rotate(
            token,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_and_rotate_already_revoked(self, store: MemoryRefreshStore) -> None:
        profile_id = uuid.uuid4()
        token, _ = await store.create_session(
            profile_id=profile_id,
            sub="user@example.com",
            roles=["user"],
            family_id=None,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        # Revoke first
        await store.revoke_refresh(token)
        # Try to use revoked token
        result = await store.validate_and_rotate(
            token,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_revoke_refresh(self, store: MemoryRefreshStore) -> None:
        token, _ = await store.create_session(
            profile_id=uuid.uuid4(),
            sub="user@example.com",
            roles=["user"],
            family_id=None,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        await store.revoke_refresh(token)
        # After revocation, validate should fail
        result = await store.validate_and_rotate(
            token,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_revoke_refresh_malformed(self, store: MemoryRefreshStore) -> None:
        await store.revoke_refresh("no-colon")  # Should not raise

    @pytest.mark.asyncio
    async def test_revoke_refresh_bad_uuid(self, store: MemoryRefreshStore) -> None:
        await store.revoke_refresh("not-a-uuid:secret")  # Should not raise

    @pytest.mark.asyncio
    async def test_revoke_family(self, store: MemoryRefreshStore) -> None:
        family_id = uuid.uuid4()
        token1, _ = await store.create_session(
            profile_id=uuid.uuid4(),
            sub="user@example.com",
            roles=["user"],
            family_id=family_id,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        token2, _ = await store.create_session(
            profile_id=uuid.uuid4(),
            sub="user@example.com",
            roles=["user"],
            family_id=family_id,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        await store.revoke_family(family_id)
        # Both should fail
        r1 = await store.validate_and_rotate(token1, user_agent=None, ip=None, ttl_seconds=3600)
        r2 = await store.validate_and_rotate(token2, user_agent=None, ip=None, ttl_seconds=3600)
        assert r1 is None
        assert r2 is None

    @pytest.mark.asyncio
    async def test_rotation_preserves_family(self, store: MemoryRefreshStore) -> None:
        family_id = uuid.uuid4()
        token1, _ = await store.create_session(
            profile_id=uuid.uuid4(),
            sub="user@example.com",
            roles=["user"],
            family_id=family_id,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        result = await store.validate_and_rotate(
            token1,
            user_agent=None,
            ip=None,
            ttl_seconds=3600,
        )
        assert result is not None
        ctx, new_token, _ = result
        assert ctx.family_id == family_id
        assert ctx.session_id != uuid.UUID(token1.split(":")[0])

    @pytest.mark.asyncio
    async def test_revoke_nonexistent(self, store: MemoryRefreshStore) -> None:
        fake_token = f"{uuid.uuid4()}:secret"
        await store.revoke_refresh(fake_token)  # Should not raise
