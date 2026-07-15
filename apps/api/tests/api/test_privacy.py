"""Tests for privacy endpoints — GDPR export and account deletion."""

import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture
def client():
    """Create test client with trusted hosts disabled."""
    import os
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""
    os.environ["STUDYOS_DATABASE_URL"] = ""
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app, base_url="http://testserver") as c:
        yield c


class TestPrivacyExport:
    def test_export_requires_auth(self, client) -> None:
        resp = client.get("/v1/privacy/export")
        assert resp.status_code in (401, 403)


class TestPrivacyAccountDelete:
    def test_delete_requires_auth(self, client) -> None:
        resp = client.delete("/v1/privacy/account")
        assert resp.status_code in (401, 403)
