"""Shared pytest fixtures for StudyOS API tests."""

import os
from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from studyos_api.main import create_app


@pytest.fixture(scope="session", autouse=True)
def configure_test_env() -> None:
    """Configure test environment variables before any imports."""
    # Override production settings for tests
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""  # Allow all hosts in tests
    os.environ["STUDYOS_EXPOSE_ERROR_DETAIL"] = "true"
    # Use local postgres for integration tests, empty for unit tests
    os.environ.setdefault("STUDYOS_DATABASE_URL", "")  # Use in-memory auth by default
    os.environ.setdefault("STUDYOS_ALLOW_LEGACY_DEMO_BEARER", "true")
    # Clear any cached settings
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    """Clear settings cache before each test to prevent pollution."""
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
async def app() -> AsyncIterator[FastAPI]:
    """Create app and run lifespan startup."""
    app_instance = create_app()
    # Manually trigger lifespan startup
    async with app_instance.router.lifespan_context(app_instance):
        yield app_instance


@pytest.fixture()
async def api_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


