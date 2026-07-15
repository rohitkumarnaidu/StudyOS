# Testing guidelines — StudyOS

This document describes the testing pyramid, folder layout, commands, and CI behavior for the monorepo. It complements the short summary in [ENGINEERING.md](./ENGINEERING.md).

**Formal checklist:** [ENTERPRISE_READINESS.md](./ENTERPRISE_READINESS.md) (section C).

## Principles

1. **Fast feedback by default.** PR CI runs unit, API, auth, OpenAPI, and frontend unit tests; it skips optional integration tests that need a real database unless you opt in.
2. **One concern per test.** Prefer small tests with explicit names; share setup through fixtures and test utilities, not copy-paste.
3. **Stable boundaries.** Mock outbound HTTP with **respx** (Python) or **MSW** (web) when tests would otherwise depend on third parties; keep contract tests (OpenAPI) green when routes change.

## Pyramid

| Layer | Scope | Where | Typical tools |
|-------|--------|--------|----------------|
| Unit | Pure logic, no ASGI | `apps/api/tests/unit`, `apps/web` `*.spec.tsx` | Pytest + markers; Vitest + Testing Library |
| API / contract | HTTP + ASGI app | `apps/api/tests/api` | httpx `AsyncClient` + `ASGITransport` |
| Auth | Login, JWT, RBAC | `apps/api/tests/api` (`@pytest.mark.auth`) | Same as API + `support.auth_tokens` |
| OpenAPI / Swagger | Generated schema validity | `apps/api/tests/api/test_openapi.py` | `openapi_spec_validator.validate` |
| Integration | DB, queues, real services | `apps/api/tests/integration` | Pytest + env (`STUDYOS_DATABASE_URL`, …) |
| E2E | Browser journeys | `apps/web/e2e` | Playwright |

## Repository layout

```
STUDYOS/
  apps/api/tests/
    conftest.py           # app + api_client fixtures
    support/              # test-only helpers (JWT, respx patterns)
    api/                  # HTTP, auth, OpenAPI
    unit/                 # fast Python unit tests
    integration/          # optional external dependencies
  apps/web/
    e2e/                  # Playwright specs
    src/**/*.spec.tsx     # colocated Vitest component tests (convention)
    src/test/setup.ts     # jest-dom for Vitest
```

## Python (`apps/api`)

- **Run all tests (including integration collection):** from `apps/api`, `uv run pytest`.
- **Match CI (exclude integration marker):** `uv run pytest -q -m "not integration"`.
- **Markers:** `unit`, `api`, `auth`, `openapi`, `integration` — register in `pyproject.toml` and use on tests.
- **Imports:** helpers live under `tests/support/`; pytest `pythonpath = ["tests"]` allows `from support.auth_tokens import …`.
- **Mocks:** use **respx** for outbound HTTP; see `tests/support/http_mocks.py` and `tests/unit/test_http_mocks_respx.py`.

## Web (`apps/web`)

- **Unit / component:** `pnpm run test` (Vitest). Prefer `*.spec.tsx` next to components or under `src/**/__tests__/`.
- **E2E:** `pnpm run test:e2e` (Playwright). Local runs start dev server via `playwright.config.ts`; CI builds then runs `next start` via the same config when `CI=true`.

## CI

GitHub Actions workflow `.github/workflows/ci.yml`:

- **js:** format, then `turbo` lint, typecheck, **test**, build (includes Vitest).
- **python:** Ruff, Ruff format check, mypy on `src`, pytest with `-m "not integration"`.
- **e2e:** builds `@studyos/web`, installs Playwright Chromium, runs Playwright against production server mode.

Add a scheduled or manual workflow later if you want full integration tests against a staging database.

## Swagger / OpenAPI

- Automated validation ensures the FastAPI-generated document is structurally valid and keeps critical paths present (for example `/v1/me`).
- For consumer-driven checks (breaking changes), consider **Schemathesis** or contract tests against a golden export in a follow-up.

## Coverage (targets)

- **API:** 484 tests passing (90.03% coverage). Cover new routes with at least one happy path and one auth or validation failure where applicable.
- **Web:** 218 tests passing (~75% coverage). Cover interactive components (forms, toggles) with Testing Library; reserve Playwright for cross-page flows.
- **E2E:** 6 Playwright spec files covering auth, syllabus, quiz, notes, analytics, settings, and navigation flows.
- **Total:** 702 passing tests across API + Web + E2E.

## Adding a new test

1. Choose the layer (unit vs API vs integration vs E2E).
2. Add the narrowest marker (`@pytest.mark.api`, etc.).
3. Reuse `api_client`, `bearer_token`, or Vitest `render` + `userEvent` from shared setup.
4. Update this doc only when you introduce a new category or command.
