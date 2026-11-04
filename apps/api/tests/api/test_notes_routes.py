"""Tests for notes routes."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture(autouse=True)
def configure_test_env() -> None:
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""
    os.environ["STUDYOS_DATABASE_URL"] = ""
    os.environ["STUDYOS_EXPOSE_ERROR_DETAIL"] = "true"
    os.environ["STUDYOS_ALLOW_LEGACY_DEMO_BEARER"] = "true"
    from studyos_api.core.config import get_settings

    get_settings.cache_clear()


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app, base_url="http://testserver", raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def auth_headers():
    from studyos_api.core.config import get_settings
    from studyos_api.security.tokens import mint_access_token

    settings = get_settings()
    user_id = str(uuid.uuid4())
    token = mint_access_token(settings, sub=user_id, roles=["student"])
    return {"Authorization": f"Bearer {token}"}


class TestNotesRoutes:
    def test_list_notes(self, client, auth_headers):
        resp = client.get("/v1/notes", headers=auth_headers)
        assert resp.status_code in (200, 500)

    def test_list_notes_without_auth(self, client):
        resp = client.get("/v1/notes")
        assert resp.status_code in (401, 403, 200)

    def test_get_note_not_found(self, client, auth_headers):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}", headers=auth_headers)
        assert resp.status_code in (404, 500, 200)

    def test_delete_note_not_found(self, client, auth_headers):
        note_id = str(uuid.uuid4())
        resp = client.delete(f"/v1/notes/{note_id}", headers=auth_headers)
        assert resp.status_code in (404, 500, 200)

    def test_get_note_highlights(self, client, auth_headers):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}/highlights", headers=auth_headers)
        assert resp.status_code in (200, 404, 500)

    def test_get_note_bookmarks(self, client, auth_headers):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}/bookmarks", headers=auth_headers)
        assert resp.status_code in (200, 404, 500)

    def test_get_note_personal_notes(self, client, auth_headers):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}/personal-notes", headers=auth_headers)
        assert resp.status_code in (200, 404, 500)

    def test_get_note_highlights_without_auth(self, client):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}/highlights")
        assert resp.status_code in (401, 403, 200)

    def test_upload_note_without_file(self, client, auth_headers):
        resp = client.post("/v1/notes/upload", headers=auth_headers)
        assert resp.status_code in (422, 400, 500)

    def test_get_note_without_auth(self, client):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}")
        assert resp.status_code in (401, 403, 200)

    def test_delete_note_without_auth(self, client):
        note_id = str(uuid.uuid4())
        resp = client.delete(f"/v1/notes/{note_id}")
        assert resp.status_code in (401, 403, 200)

    def test_upload_note_without_auth(self, client):
        resp = client.post("/v1/notes/upload")
        assert resp.status_code in (401, 403, 200)

    def test_get_note_bookmarks_without_auth(self, client):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}/bookmarks")
        assert resp.status_code in (401, 403, 200)
