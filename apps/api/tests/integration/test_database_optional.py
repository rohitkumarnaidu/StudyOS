"""Optional integration tests — opt in with `STUDYOS_DATABASE_URL` (or markers in CI)."""

import os

import pytest


@pytest.fixture(autouse=True)
def reset_env():
    """Reset environment for each test."""
    original = os.environ.get("STUDYOS_DATABASE_URL")
    yield
    if original is not None:
        os.environ["STUDYOS_DATABASE_URL"] = original
    elif "STUDYOS_DATABASE_URL" in os.environ:
        del os.environ["STUDYOS_DATABASE_URL"]


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("STUDYOS_DATABASE_URL", "") == "",
    reason="STUDYOS_DATABASE_URL not set or empty",
)
async def test_database_url_is_configured() -> None:
    """Verify DATABASE_URL format when running integration tests."""
    db_url = os.environ.get("STUDYOS_DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    assert db_url.startswith("postgresql"), f"Invalid DATABASE_URL format: {db_url}"
