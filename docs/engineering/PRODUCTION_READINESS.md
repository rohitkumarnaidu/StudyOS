# Production readiness — StudyOS (honest audit)

This document answers whether the monorepo is **“enterprise production ready”** as a whole. Short answer: **the stack has production-oriented patterns in place**, but **production go-live still requires** your secrets, hosting choices, database hosting, observability, and (where marked) additional wiring. Use this as a checklist, not a certificate.

## Summary matrix

| Area | Status | Notes |
|------|--------|--------|
| **Backend (FastAPI)** | **Strong baseline** | Typed settings (`STUDYOS_*`), production JWT rules, CORS, optional trusted hosts, SlowAPI limits, structured logging, request IDs, security headers middleware, global error handlers, asyncpg pool with sane limits, health route for Docker. |
| **Database** | **Schema ready, ops on you** | Versioned SQL under `supabase/migrations/`, seed, Supabase-oriented docs. **RLS, backups, pooler URL, and migration apply in prod** are your operational responsibility. |
| **Frontend (Next.js)** | **Strong baseline** | Security headers, `standalone` build, JWT + cookies, **Supabase SSR** (`@supabase/ssr`): middleware session refresh, server + browser clients, `/api/auth/session` merges StudyOS JWT + Supabase user + `profiles` read. Optional `SUPABASE_SERVICE_ROLE_KEY` for admin server code. |
| **Testing** | **Scalable baseline** | Pytest layers + markers, OpenAPI validation, Vitest + Testing Library, Playwright E2E in CI, integration tests opt-in via `STUDYOS_DATABASE_URL`. **Not** full mutation coverage or load testing. |
| **AI** | **Configurable, keys external** | Multi-provider orchestration, retries, MCP registry, env-driven models and keys. **Rate limits per route**, spend caps, and **PII/redaction policies** should be tightened per product policy. |
| **Secrets / env** | **Templates complete** | `apps/api/.env.example`, `apps/web/.env.example`, plus `*.env.production.example`. Fill from a **secret manager** in prod; never commit `.env`. |

## Backend — what is production-grade today

- **Configuration:** `apps/api/src/studyos_api/core/config.py` — Pydantic settings, `STUDYOS_` prefix, `.env` loading, `extra="ignore"`.
- **Production validation:** Rejects weak JWT secrets and blocks `STUDYOS_ALLOW_LEGACY_DEMO_BEARER` when `STUDYOS_APP_ENV=production`.
- **HTTP:** CORS from settings, optional `TrustedHostMiddleware`, `SlowAPIMiddleware`, custom security headers + request ID.
- **Persistence:** Optional Postgres via `STUDYOS_DATABASE_URL`; refresh/session store switches implementation when URL is set.
- **Container:** `docker/Dockerfile.api` runs uvicorn as non-root; healthcheck hits `/v1/healthz`.

**You still must:** set real `STUDYOS_JWT_SECRET`, `STUDYOS_DATABASE_URL`, `STUDYOS_CORS_ORIGINS`, `STUDYOS_TRUSTED_HOSTS` (recommended in prod), and tune rate limits.

## Database — what is production-grade today

- **Migrations + seed** live under `supabase/` with CLI and plain-Postgres paths documented in `supabase/README.md` and `docs/database/*`.
- **Supabase** is the intended hosted shape; the API only needs a **Postgres URL** (pooler + `sslmode=require` in prod).

**You still must:** run migrations in each environment (includes `20260213120000_profiles_rls_supabase.sql` when `auth` schema exists), configure backups and monitoring, and extend **RLS** beyond `profiles` as modules grow.

## Frontend — what is production-grade today

- **Headers:** `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` on all routes.
- **Build:** `output: "standalone"` for minimal production images; `poweredByHeader: false`.
- **Auth cookies:** `Secure` when `NODE_ENV=production`; SameSite=Lax; httpOnly for tokens.
- **Public env:** `@studyos/config` validates `NEXT_PUBLIC_*` so unsafe values fail fast at boot.

**You still must:** align `STUDYOS_JWT_SECRET` / issuer with API, set `STUDYOS_INTERNAL_API_BASE_URL`, set **`NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`** when using Server Actions in production, and add **`NEXT_PUBLIC_SUPABASE_*`** + **`SUPABASE_SERVICE_ROLE_KEY`** (server only) per `apps/web/.env.example`. Use Supabase Auth UI or magic-link/OAuth routes when you expose Supabase sign-in to users (not required if you only use StudyOS API login + DB via service role).

## Testing — what is production-grade today

- **CI** (`.github/workflows/ci.yml`): lint, typecheck, unit/API tests (integration deselected by marker), web build, Playwright smoke.
- **Contracts:** OpenAPI schema validation in tests.
- **Docs:** `docs/engineering/TESTING.md`, `apps/api/tests/README.md`.

**You still must:** add integration job with real Postgres if you want DB tests on every merge; expand E2E for critical business flows; add performance/security testing as needed.

## AI — what is production-grade today

- Provider selection and fallbacks from env; optional warm-up; MCP from JSON config; memory bounds from env.

**You still must:** supply API keys via secrets manager, set quotas/alerts at the provider, and define product policies (logging, retention, blocked content).

## Environment templates — where to look

| File | Purpose |
|------|---------|
| `apps/api/.env.example` | Local/dev — **every `STUDYOS_*` key** on an active `KEY=value` line (empty = unset). |
| `apps/api/.env.production.example` | Prod-oriented names and shapes (no dev shortcuts). |
| `apps/web/.env.example` | Local/dev — public + server-only + optional Supabase placeholders. |
| `apps/web/.env.production.example` | Prod-oriented + **Next production-only** vars. |
| `.env.example` (repo root) | Index of variables; points to per-app templates. |

If a variable appears in `Settings` (API) or in server/public Next code, it should appear in the appropriate template (either set or commented with a placeholder).

## Bottom line

The codebase is **structured for enterprise production** (layering, security middleware, typed config, CI, migrations, AI boundaries). **No template repo is “fully production”** without your environment, SRE practices, and product-specific hardening. Treat **this doc + filled secrets + runbooks** as the production gate.
