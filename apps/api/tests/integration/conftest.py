"""Integration test configuration - use remote Supabase database."""

import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def configure_integration_db():
    """Configure remote Supabase for integration tests only."""
    original = os.environ.get("STUDYOS_DATABASE_URL")
    db_url = os.environ.get("STUDYOS_INTEGRATION_DB_URL", "postgresql://studyos:studyos@localhost:5432/studyos_test")
    os.environ["STUDYOS_DATABASE_URL"] = db_url
    # Clear settings cache
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()
    yield
    # Restore original
    if original is None:
        os.environ.pop("STUDYOS_DATABASE_URL", None)
    else:
        os.environ["STUDYOS_DATABASE_URL"] = original
    get_settings.cache_clear()
