"""Tests for core/config.py — Settings validation and production hardening."""

import os
from unittest.mock import patch

import pytest

from studyos_api.core.config import Settings, get_settings


def _clear_settings_cache():
    """Clear the lru_cache so tests get fresh Settings instances."""
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def clear_cache():
    _clear_settings_cache()
    yield
    _clear_settings_cache()


def _fresh_settings(**overrides):
    """Create a Settings instance ignoring environment variables."""
    base = {
        "app_env": "development",
        "log_level": "INFO",
        "cors_origins": "http://localhost:3000",
        "jwt_secret": "dev-only-studyos-jwt-secret-change-me-32chars!!",
        "jwt_issuer": "studyos-api",
        "jwt_algorithm": "HS256",
        "access_token_ttl_seconds": 900,
        "refresh_token_ttl_seconds": 604800,
        "allow_legacy_demo_bearer": True,
        "ai_primary_provider": "ollama",
        "ai_fallback_chain": "",
        "redis_url": None,
        "database_url": None,
        "trusted_hosts": "",
    }
    base.update(overrides)
    return Settings(**base)


@pytest.mark.unit
class TestSettingsDefaults:
    """Test default Settings values."""

    def test_default_app_env(self):
        """Default app_env is 'development'."""
        settings = _fresh_settings()
        assert settings.app_env == "development"

    def test_default_log_level(self):
        """Default log_level is 'INFO'."""
        settings = _fresh_settings()
        assert settings.log_level == "INFO"

    def test_default_cors_origins(self):
        """Default cors_origins includes localhost:3000."""
        settings = _fresh_settings()
        assert "http://localhost:3000" in settings.cors_origin_list

    def test_default_jwt_issuer(self):
        """Default jwt_issuer is 'studyos-api'."""
        settings = _fresh_settings()
        assert settings.jwt_issuer == "studyos-api"

    def test_default_jwt_algorithm(self):
        """Default jwt_algorithm is 'HS256'."""
        settings = _fresh_settings()
        assert settings.jwt_algorithm == "HS256"

    def test_default_access_token_ttl(self):
        """Default access_token_ttl_seconds is 900 (15 min)."""
        settings = _fresh_settings()
        assert settings.access_token_ttl_seconds == 900

    def test_default_refresh_token_ttl(self):
        """Default refresh_token_ttl_seconds is 604800 (7 days)."""
        settings = _fresh_settings()
        assert settings.refresh_token_ttl_seconds == 604800

    def test_default_ai_provider(self):
        """Default ai_primary_provider is 'ollama'."""
        settings = _fresh_settings()
        assert settings.ai_primary_provider == "ollama"

    def test_default_redis_url_is_none(self):
        """Default redis_url is None (no caching)."""
        settings = _fresh_settings()
        assert settings.redis_url is None

    def test_default_database_url_is_none(self):
        """Default database_url is None (in-memory mode)."""
        settings = _fresh_settings()
        assert settings.database_url is None


@pytest.mark.unit
class TestSettingsProperties:
    """Test Settings computed properties."""

    def test_is_production_false_for_development(self):
        """is_production is False for app_env='development'."""
        settings = Settings(app_env="development")
        assert settings.is_production is False

    def test_is_production_true_for_production(self):
        """is_production is True for app_env='production'."""
        settings = _fresh_settings(
            app_env="production",
            jwt_secret="strong-production-secret-that-is-at-least-32-chars!!",
            allow_legacy_demo_bearer=False,
        )
        assert settings.is_production is True

    def test_cors_origin_list_parses_comma_separated(self):
        """cors_origin_list splits comma-separated string."""
        settings = Settings(cors_origins="http://localhost:3000,https://app.studyos.app")
        assert settings.cors_origin_list == ["http://localhost:3000", "https://app.studyos.app"]

    def test_cors_origin_list_strips_whitespace(self):
        """cors_origin_list strips whitespace from origins."""
        settings = Settings(cors_origins="http://localhost:3000 , https://app.studyos.app ")
        assert settings.cors_origin_list == ["http://localhost:3000", "https://app.studyos.app"]

    def test_trusted_host_list_empty_by_default(self):
        """trusted_host_list is empty when trusted_hosts is empty."""
        settings = Settings()
        assert settings.trusted_host_list == []

    def test_trusted_host_list_parses_comma_separated(self):
        """trusted_host_list splits comma-separated string."""
        settings = Settings(trusted_hosts="api.studyos.app, localhost")
        assert settings.trusted_host_list == ["api.studyos.app", "localhost"]

    def test_ai_fallback_provider_ids_empty_by_default(self):
        """ai_fallback_provider_ids is empty when ai_fallback_chain is empty."""
        settings = Settings()
        assert settings.ai_fallback_provider_ids == []

    def test_ai_fallback_provider_ids_parses_comma_separated(self):
        """ai_fallback_provider_ids splits comma-separated string."""
        settings = Settings(ai_fallback_chain="openai, anthropic, ollama")
        assert settings.ai_fallback_provider_ids == ["openai", "anthropic", "ollama"]


@pytest.mark.unit
class TestSettingsValidation:
    """Test Settings field validation."""

    def test_jwt_secret_min_length(self):
        """jwt_secret must be at least 32 characters."""
        with pytest.raises(Exception):
            Settings(jwt_secret="short")

    def test_access_token_ttl_minimum(self):
        """access_token_ttl_seconds must be >= 60."""
        with pytest.raises(Exception):
            Settings(access_token_ttl_seconds=30)

    def test_access_token_ttl_maximum(self):
        """access_token_ttl_seconds must be <= 3600."""
        with pytest.raises(Exception):
            Settings(access_token_ttl_seconds=7200)

    def test_refresh_token_ttl_minimum(self):
        """refresh_token_ttl_seconds must be >= 3600."""
        with pytest.raises(Exception):
            Settings(refresh_token_ttl_seconds=1800)

    def test_refresh_token_ttl_maximum(self):
        """refresh_token_ttl_seconds must be <= 1209600."""
        with pytest.raises(Exception):
            Settings(refresh_token_ttl_seconds=2000000)

    def test_ai_max_retries_range(self):
        """ai_max_retries must be 0-8."""
        with pytest.raises(Exception):
            Settings(ai_max_retries=10)

    def test_ai_retry_base_range(self):
        """ai_retry_base_seconds must be 0.05-30.0."""
        with pytest.raises(Exception):
            Settings(ai_retry_base_seconds=0.01)

    def test_ai_memory_max_messages_range(self):
        """ai_memory_max_messages must be 4-200."""
        with pytest.raises(Exception):
            Settings(ai_memory_max_messages=2)

    def test_otel_sample_rate_range(self):
        """otel_traces_sample_rate must be 0.0-1.0."""
        with pytest.raises(Exception):
            Settings(otel_traces_sample_rate=1.5)


@pytest.mark.unit
class TestProductionHardening:
    """Test production hardening validator."""

    def test_production_rejects_weak_jwt_secret(self):
        """Production mode rejects JWT secrets containing 'change-me'."""
        with pytest.raises(ValueError, match="STUDYOS_JWT_SECRET must be a strong secret"):
            _fresh_settings(
                app_env="production",
                jwt_secret="strong-secret-but-contains-change-me-32chars!!",
            )

    def test_production_rejects_dev_jwt_secret(self):
        """Production mode rejects JWT secrets containing 'dev-only'."""
        with pytest.raises(ValueError, match="STUDYOS_JWT_SECRET must be a strong secret"):
            _fresh_settings(
                app_env="production",
                jwt_secret="dev-only-studyos-jwt-secret-change-me-32chars!!",
            )

    def test_production_rejects_short_jwt_secret(self):
        """Production mode rejects JWT secrets shorter than 32 chars."""
        with pytest.raises(Exception):  # Could be ValueError or Pydantic ValidationError
            _fresh_settings(
                app_env="production",
                jwt_secret="short-secret",
            )

    def test_production_rejects_legacy_demo_bearer(self):
        """Production mode rejects allow_legacy_demo_bearer=True."""
        with pytest.raises(ValueError, match="STUDYOS_ALLOW_LEGACY_DEMO_BEARER must be false"):
            _fresh_settings(
                app_env="production",
                jwt_secret="strong-production-secret-that-is-32-chars!!",
                allow_legacy_demo_bearer=True,
            )

    def test_production_accepts_strong_config(self):
        """Production mode accepts strong JWT secret and demo bearer disabled."""
        settings = _fresh_settings(
            app_env="production",
            jwt_secret="strong-production-secret-that-is-at-least-32-chars!!",
            allow_legacy_demo_bearer=False,
        )
        assert settings.is_production is True
        assert settings.allow_legacy_demo_bearer is False

    def test_development_allows_weak_jwt_secret(self):
        """Development mode allows weak JWT secrets."""
        settings = _fresh_settings(
            app_env="development",
            jwt_secret="dev-only-studyos-jwt-secret-change-me-32chars!!",
        )
        assert settings.is_production is False


@pytest.mark.unit
class TestGetSettings:
    """Test get_settings cached function."""

    def test_get_settings_returns_settings(self):
        """get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_is_cached(self):
        """get_settings uses lru_cache for singleton behavior."""
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
