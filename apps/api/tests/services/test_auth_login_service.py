"""Tests for AuthLoginService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from studyos_api.services.auth_login_service import AuthLoginService, _roles_from_app_role
from studyos_api.services.refresh_sessions import MemoryRefreshStore


class TestRolesFromAppRole:
    def test_student(self):
        assert _roles_from_app_role("student") == ["student"]

    def test_admin(self):
        assert _roles_from_app_role("admin") == ["admin"]


class TestAuthLoginServiceNoPool:
    @pytest.fixture
    def settings(self):
        s = MagicMock()
        s.demo_login_email = "demo@studyos.app"
        return s

    @pytest.fixture
    def service(self, settings):
        store = MemoryRefreshStore()
        return AuthLoginService(pool=None, refresh_store=store, settings=settings)

    @pytest.mark.asyncio
    async def test_demo_login_success(self, service):
        result = await service.authenticate(
            email="demo@studyos.app",
            password="demo",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is not None
        profile_id, sub, roles = result
        assert profile_id == uuid.UUID("77777777-7777-4777-8777-777777777777")
        assert sub == "demo@studyos.app"
        assert roles == ["student"]

    @pytest.mark.asyncio
    async def test_demo_login_wrong_email(self, service):
        result = await service.authenticate(
            email="wrong@studyos.app",
            password="demo",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_demo_login_wrong_password(self, service):
        result = await service.authenticate(
            email="demo@studyos.app",
            password="wrong_password",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_demo_login_case_insensitive_email(self, service):
        result = await service.authenticate(
            email="DEMO@STUDYOS.APP",
            password="demo",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_demo_login_strips_whitespace(self, service):
        result = await service.authenticate(
            email="  demo@studyos.app  ",
            password="demo",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is not None


class _MockAcquireCtx:
    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, *args):
        pass


class TestAuthLoginServiceWithPool:
    @pytest.fixture
    def settings(self):
        s = MagicMock()
        s.demo_login_email = "demo@studyos.app"
        return s

    @pytest.fixture
    def mock_conn(self):
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)
        return conn

    @pytest.fixture
    def mock_pool(self, mock_conn):
        pool = MagicMock()
        pool.acquire = MagicMock(return_value=_MockAcquireCtx(mock_conn))
        return pool

    @pytest.mark.asyncio
    async def test_db_login_user_not_found(self, settings, mock_pool, mock_conn):
        store = MemoryRefreshStore()
        service = AuthLoginService(pool=mock_pool, refresh_store=store, settings=settings)
        mock_conn.fetchrow = AsyncMock(return_value=None)

        result = await service.authenticate(
            email="unknown@example.com",
            password="password",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_db_login_wrong_password(self, settings, mock_pool, mock_conn):
        from studyos_api.security.passwords import hash_password

        hashed = hash_password("correct_password")
        mock_conn.fetchrow = AsyncMock(
            return_value={
                "id": uuid.uuid4(),
                "email": "user@example.com",
                "app_role": "student",
                "password_hash": hashed,
            }
        )

        store = MemoryRefreshStore()
        service = AuthLoginService(pool=mock_pool, refresh_store=store, settings=settings)

        result = await service.authenticate(
            email="user@example.com",
            password="wrong_password",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_db_login_success(self, settings, mock_pool, mock_conn):
        from studyos_api.security.passwords import hash_password

        profile_id = uuid.uuid4()
        hashed = hash_password("correct_password")
        mock_conn.fetchrow = AsyncMock(
            return_value={
                "id": profile_id,
                "email": "user@example.com",
                "app_role": "student",
                "password_hash": hashed,
            }
        )

        store = MemoryRefreshStore()
        service = AuthLoginService(pool=mock_pool, refresh_store=store, settings=settings)

        result = await service.authenticate(
            email="user@example.com",
            password="correct_password",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is not None
        ret_id, sub, roles = result
        assert ret_id == profile_id
        assert sub == "user@example.com"
        assert roles == ["student"]

    @pytest.mark.asyncio
    async def test_db_login_null_email_uses_profile_id(self, settings, mock_pool, mock_conn):
        from studyos_api.security.passwords import hash_password

        profile_id = uuid.uuid4()
        hashed = hash_password("correct_password")
        mock_conn.fetchrow = AsyncMock(
            return_value={
                "id": profile_id,
                "email": None,
                "app_role": "student",
                "password_hash": hashed,
            }
        )

        store = MemoryRefreshStore()
        service = AuthLoginService(pool=mock_pool, refresh_store=store, settings=settings)

        result = await service.authenticate(
            email="user@example.com",
            password="correct_password",
            user_agent="test",
            ip="127.0.0.1",
        )

        assert result is not None
        _, sub, _ = result
        assert sub == str(profile_id)
