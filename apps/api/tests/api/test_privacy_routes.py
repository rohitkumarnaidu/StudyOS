"""Tests for privacy routes — covering uncovered lines with mocked auth and DB pool."""

import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture(autouse=True)
def configure_test_env() -> None:
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""
    os.environ["STUDYOS_DATABASE_URL"] = ""
    os.environ["STUDYOS_JWT_SECRET"] = "test-jwt-secret-for-testing-only"
    os.environ["STUDYOS_JWT_ISSUER"] = "studyos-test"
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def auth_token():
    from studyos_api.core.config import get_settings
    from studyos_api.security.tokens import mint_access_token
    settings = get_settings()
    return mint_access_token(settings, sub=str(uuid.uuid4()), roles=["student"])


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


def _mock_pool_for_app(app_instance):
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.execute = AsyncMock(return_value="")
    mock_tx = AsyncMock()
    mock_tx.__aenter__ = AsyncMock(return_value=None)
    mock_tx.__aexit__ = AsyncMock(return_value=False)
    mock_conn.transaction = MagicMock(return_value=mock_tx)
    
    mock_pool = AsyncMock()
    mock_pool.acquire = MagicMock()
    mock_acq = AsyncMock()
    mock_acq.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_acq.__aexit__ = AsyncMock(return_value=False)
    mock_pool.acquire.return_value = mock_acq
    
    app_instance.state.db_pool = mock_pool
    return mock_pool


class TestPrivacyRoutesExport:
    def test_export_requires_auth(self, app) -> None:
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.get("/v1/privacy/export")
            assert resp.status_code in (401, 403)

    def test_export_no_pool_returns_503(self, app, auth_headers) -> None:
        app.state.db_pool = None
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.get("/v1/privacy/export", headers=auth_headers)
            assert resp.status_code == 503

    def test_export_success_empty_data(self, app, auth_headers) -> None:
        _mock_pool_for_app(app)
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.get("/v1/privacy/export", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert "data" in data

    def test_export_with_profile_data(self, app, auth_headers) -> None:
        mock_pool = _mock_pool_for_app(app)
        from datetime import datetime
        mock_profile = {
            "id": uuid.uuid4(),
            "email": "test@example.com",
            "display_name": "Test User",
            "app_role": "student",
            "created_at": datetime.now(),
        }
        mock_completion = {
            "id": uuid.uuid4(),
            "subtopic_id": uuid.uuid4(),
            "completed_at": datetime.now(),
            "source": "manual",
        }
        mock_streak = {
            "current_streak": 5,
            "longest_streak": 10,
            "last_study_date": datetime.now(),
        }
        mock_usage = {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
            "created_at": datetime.now(),
        }
        
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(side_effect=[mock_profile, mock_streak])
        mock_conn.fetch = AsyncMock(side_effect=[
            [mock_completion],
            [mock_usage],
        ])
        mock_conn.execute = AsyncMock(return_value="")
        
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.get("/v1/privacy/export", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["data"]["profile"] is not None


class TestPrivacyRoutesDelete:
    def test_delete_requires_auth(self, app) -> None:
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.delete("/v1/privacy/account")
            assert resp.status_code in (401, 403)

    def test_delete_no_pool_returns_503(self, app, auth_headers) -> None:
        app.state.db_pool = None
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.delete("/v1/privacy/account", headers=auth_headers)
            assert resp.status_code == 503

    def test_delete_success(self, app, auth_headers) -> None:
        mock_pool = _mock_pool_for_app(app)
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.delete("/v1/privacy/account", headers=auth_headers)
            assert resp.status_code == 204

    def test_delete_with_refresh_store(self, app, auth_headers) -> None:
        mock_pool = _mock_pool_for_app(app)
        mock_refresh_store = AsyncMock()
        mock_refresh_store.revoke_all_for_profile = AsyncMock()
        app.state.refresh_store = mock_refresh_store
        
        with TestClient(app, base_url="http://testserver") as client:
            resp = client.delete("/v1/privacy/account", headers=auth_headers)
            assert resp.status_code == 204
            mock_refresh_store.revoke_all_for_profile.assert_called_once()
