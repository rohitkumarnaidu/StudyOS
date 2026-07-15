# API test suite

## Commands

From `apps/api` (with `uv sync --all-groups`):

| Command | Purpose |
|---------|---------|
| `uv run pytest` | Full suite (integration tests skip without env). |
| `uv run pytest -q -m "not integration"` | Same as default CI — no `integration`-marked tests. |
| `uv run pytest -m unit` | Unit tests only. |
| `uv run pytest -m api` | HTTP tests via ASGI. |

## Layout

| Path | Role |
|------|------|
| `conftest.py` | `app` fixture (`create_app()`), `api_client` (`httpx.AsyncClient` + `ASGITransport`). |
| `support/auth_tokens.py` | JWT helpers for RBAC tests (`bearer_token`). |
| `support/http_mocks.py` | Notes and patterns for **respx** outbound mocks. |
| `api/` | API, auth, health, OpenAPI validation. |
| `unit/` | Domain and pure-Python tests. |
| `integration/` | Tests that need `STUDYOS_DATABASE_URL` or other real services. |

Import test helpers as `from support.…` (not `tests.support`), because `pythonpath` includes `tests`.

Env templates use **active `KEY=value` lines** (see `apps/api/.env.example`); comments are section headers only.

## Guidelines

See [docs/engineering/TESTING.md](../../../docs/engineering/TESTING.md).
