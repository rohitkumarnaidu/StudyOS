"""Application settings (12-factor) — loaded via STUDYOS_* environment variables."""

from functools import lru_cache
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment (12-factor)."""

    model_config = SettingsConfigDict(
        env_prefix="STUDYOS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", description="development|staging|production")
    log_level: str = Field(default="INFO")

    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated browser origins allowed for CORS",
    )

    rate_limit_default: str = Field(
        default="120/minute",
        description="Default SlowAPI limit string (SlowAPI / limits library notation).",
    )

    trusted_hosts: str = Field(
        default="",
        description="Comma-separated hostnames for TrustedHostMiddleware; empty disables.",
    )

    expose_error_detail: bool = Field(
        default=False,
        description="When true, non-production responses may include more diagnostic fields.",
    )

    database_url: str | None = Field(
        default=None,
        description="Postgres DSN for refresh sessions + credentials (asyncpg). Optional in dev.",
    )

    jwt_secret: str = Field(
        default="dev-only-studyos-jwt-secret-change-me-32chars!!",
        min_length=32,
        description="HS256 signing key for access JWTs (must match Next middleware).",
    )

    jwt_issuer: str = Field(default="studyos-api", description="JWT iss claim")

    jwt_algorithm: str = Field(default="HS256")

    access_token_ttl_seconds: int = Field(default=900, ge=60, le=3600)

    refresh_token_ttl_seconds: int = Field(default=604800, ge=3600, le=1209600)

    allow_legacy_demo_bearer: bool = Field(
        default=True,
        description="If true, accept legacy demo/admin bearer tokens (non-JWT) — dev only.",
    )

    demo_login_email: str = Field(
        default="demo@studyos.app",
        description="When DATABASE_URL unset, allow password login for this email only.",
    )

    # --- AI / LLM (provider-agnostic orchestration) ---
    ai_ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        description="Ollama daemon base URL (no /v1 suffix).",
    )
    ai_openai_api_key: str | None = Field(default=None, description="OpenAI API key (optional).")
    ai_openai_base_url: str = Field(default="https://api.openai.com/v1")
    ai_anthropic_api_key: str | None = Field(
        default=None, description="Anthropic API key (optional)."
    )
    ai_anthropic_base_url: str = Field(default="https://api.anthropic.com")
    ai_primary_provider: str = Field(
        default="ollama",
        description="Primary provider id: ollama | openai | anthropic",
    )
    ai_fallback_chain: str = Field(
        default="",
        description="Comma-separated provider ids to try after primary (e.g. openai,ollama).",
    )
    ai_default_model_ollama: str = Field(default="llama3.2")
    ai_default_model_openai: str = Field(default="gpt-4o-mini")
    ai_default_model_anthropic: str = Field(default="claude-3-5-haiku-20241022")
    ai_max_retries: int = Field(default=2, ge=0, le=8)
    ai_retry_base_seconds: float = Field(default=0.5, ge=0.05, le=30.0)
    ai_mcp_servers_json: str = Field(
        default="[]",
        description='JSON array of MCP connectors, e.g. [{"id":"docs","url":"http://localhost:8080/mcp"}]',
    )
    ai_memory_max_messages: int = Field(default=40, ge=4, le=200)
    ai_memory_session_ttl_seconds: int = Field(default=3600, ge=60, le=86400)
    ai_warm_on_start: bool = Field(
        default=False,
        description=(
            "If true, build LLM provider chain at API startup "
            "(faster first AI request; slower boot)."
        ),
    )

    # --- Cache ---
    redis_url: str | None = Field(
        default=None,
        description="Redis DSN for caching (e.g. redis://localhost:6379/0). Optional.",
    )

    # --- Celery / Task Queue ---
    celery_broker_url: str | None = Field(
        default=None,
        description="Redis/AMQP broker URL for Celery (e.g. redis://localhost:6379/1).",
    )
    celery_result_backend: str | None = Field(
        default=None,
        description="Redis/DB backend for Celery results.",
    )
    celery_task_default_retry_delay: int = Field(
        default=60,
        ge=10,
        le=600,
        description="Default retry delay in seconds for Celery tasks.",
    )
    celery_task_max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retries for failed Celery tasks.",
    )
    celery_concurrency: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Number of concurrent Celery worker processes.",
    )

    # --- Observability ---
    otel_service_name: str = Field(default="studyos-api")
    otel_exporter_otlp_endpoint: str | None = Field(
        default=None,
        description="OTLP endpoint for traces/metrics (e.g. http://otel-collector:4318)",
    )
    otel_traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)

    @property
    def ai_fallback_provider_ids(self) -> list[str]:
        return [p.strip().lower() for p in self.ai_fallback_chain.split(",") if p.strip()]

    @model_validator(mode="after")
    def _production_hardening(self) -> Self:
        if self.is_production:
            weak = "change-me" in self.jwt_secret.lower() or "dev-only" in self.jwt_secret.lower()
            if weak or len(self.jwt_secret) < 32:
                msg = "STUDYOS_JWT_SECRET must be a strong secret in production"
                raise ValueError(msg)
            if self.allow_legacy_demo_bearer:
                msg = "STUDYOS_ALLOW_LEGACY_DEMO_BEARER must be false in production"
                raise ValueError(msg)
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def trusted_host_list(self) -> list[str]:
        return [h.strip() for h in self.trusted_hosts.split(",") if h.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
