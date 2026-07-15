# Enterprise readiness matrix — StudyOS

This document maps **requested enterprise capabilities** to **what exists in the repo today**, with status **Done**, **Partial**, or **Planned** (backlog). It is the single place to answer “is this complete?”

Supporting docs: [database/README.md](../database/README.md), [security/AUTHENTICATION.md](../security/AUTHENTICATION.md), [engineering/TESTING.md](./TESTING.md), [engineering/PRODUCTION_READINESS.md](./PRODUCTION_READINESS.md).

---

## A. Database architecture

| # | Requirement | Status | Where / notes |
|---|-------------|--------|----------------|
| 1 | Optimize schema design | **Partial** | Core tenancy, syllabus, progress, auth tables in `supabase/migrations/20250613120002_*` … `20250613120007_*`; ongoing evolution in [DATABASE_SCHEMA_PLAN.md](../architecture/DATABASE_SCHEMA_PLAN.md). |
| 2 | Normalize where required | **Done** | Institutes ↔ profiles ↔ memberships, syllabus hierarchy, progress keyed by `profile_id`. |
| 3 | Scalable relationships | **Done** | FKs, enums (`app_role`, `member_role`), optional `auth.users` FK when `auth` schema exists. |
| 4 | Indexing strategy | **Done** | Partial uniques (`WHERE deleted_at IS NULL`), hot-path indexes; see [INDEXING_AND_QUERIES.md](../database/INDEXING_AND_QUERIES.md). |
| 5 | Migration system | **Done** | Forward-only SQL under `supabase/migrations/`; workflow in [MIGRATIONS_AND_SEEDS.md](../database/MIGRATIONS_AND_SEEDS.md). |
| 6 | Query performance | **Partial** | Design rules + index doc; no continuous `EXPLAIN` baselines in CI; add when traffic warrants. |
| 7 | Audit logging structure | **Done** | `public.audit_log`, `studyos_audit_row()`, GUCs `studyos.actor_id` / `studyos.request_id` — [20250613120001_audit_and_row_versioning.sql](../../supabase/migrations/20250613120001_audit_and_row_versioning.sql). Not every table is wired yet; extend triggers per domain. |
| 8 | Soft delete support | **Done** | `deleted_at` on domain tables + partial indexes (see migrations + indexing doc). |
| 9 | Timestamps / versioning | **Done** | `created_at` / `updated_at` + `row_version` + triggers `studyos_set_updated_at` / `studyos_bump_row_version`. |
| — | Database documentation | **Done** | `docs/database/*` (README, ERD, migrations, indexing). |
| — | ER diagrams | **Done** | [ERD.md](../database/ERD.md) (Mermaid). |
| — | Migration structure | **Done** | Timestamped files under `supabase/migrations/`. |
| — | Seed strategy | **Done** | `supabase/seed.sql` + strategy table in [MIGRATIONS_AND_SEEDS.md](../database/MIGRATIONS_AND_SEEDS.md). |
| — | Supabase Auth + RLS | **Partial** | `20260213120000_profiles_rls_supabase.sql`, `20260213120001_on_auth_user_create_profile.sql`; extend RLS to other tables as features ship. |

---

## B. Authentication & security

| # | Requirement | Status | Where / notes |
|---|-------------|--------|----------------|
| 1 | JWT / session strategy | **Done** | Access JWT (HS256, short TTL) + opaque refresh; [AUTHENTICATION.md](../security/AUTHENTICATION.md), `apps/api` auth routes + `apps/web` cookies / middleware. |
| 2 | Refresh token flow | **Done** | Rotation, `family_id`, hash-at-rest — `auth_sessions` migration + refresh service; BFF silent refresh in `apps/web/middleware.ts`. |
| 3 | RBAC permissions | **Done** | JWT `roles` → `require_permissions` in `apps/api/src/studyos_api/deps/rbac.py` (+ tests). |
| 4 | Secure password handling | **Done** | Argon2id in `auth_credentials.password_hash` (see migration + `auth_login_service`). |
| 5 | API protection | **Partial** | JWT verification, optional TrustedHost, CORS, rate limits; no API gateway / WAF in repo (deploy-time). |
| 6 | CSRF / XSS / hardening | **Partial** | Next security headers, HttpOnly cookies, SameSite=Lax; **double-submit CSRF** on mutating BFF routes still **recommended** for cross-site clients — called out in [AUTHENTICATION.md §2](../security/AUTHENTICATION.md). |
| 7 | Rate limiting | **Done** | SlowAPI + stricter limits on `/v1/auth/*` and AI routes (`apps/api/src/studyos_api/api/v1/routes/auth.py`, `core/limiter.py`). |
| 8 | Audit logs | **Partial** | DB `audit_log` + API structured logs (`structlog`); immutable append-only compliance tier = extend triggers to all sensitive tables + retention policy. |
| 9 | Device / session tracking | **Done** | `auth_sessions.user_agent`, `ip inet`, `last_used_at` (migration `20250613120007_*`). |
| 10 | Environment / secrets | **Done** | Pydantic `Settings`, production validators, `.env.example` templates; use secret manager in prod. |
| — | Security decisions & attack vectors | **Done** | [AUTHENTICATION.md](../security/AUTHENTICATION.md) (strategy, attacks, mitigations, backlog). |

**Backlog (explicit):** JWT `kid`/rotation, OIDC as primary IdP, Redis JWT denylist, account lockout after repeated failures, full CSRF on all state-changing BFF routes.

---

## C. Testing architecture

| # | Requirement | Status | Where / notes |
|---|-------------|--------|----------------|
| 1 | Unit tests | **Done** | `apps/api/tests/unit`, `apps/web` `*.spec.ts(x)` (Vitest). |
| 2 | Integration tests | **Partial** | `apps/api/tests/integration` opt-in via `STUDYOS_DATABASE_URL`; **no Postgres service in default CI** — run manually or add workflow job. |
| 3 | API tests | **Done** | `apps/api/tests/api` (httpx + ASGI). |
| 4 | Auth tests | **Done** | Marked `@pytest.mark.auth` + JWT helpers in `tests/support/`. |
| 5 | Frontend component tests | **Done** | Vitest + Testing Library (`button.spec.tsx`, etc.). |
| 6 | E2E testing | **Done** | Playwright `apps/web/e2e`; CI job `e2e` in `.github/workflows/ci.yml`. |
| 7 | Mock systems | **Partial** | **respx** for outbound HTTP (`apps/api`); **MSW** for web not wired yet (documented as future in [TESTING.md](./TESTING.md)). |
| 8 | Test utilities | **Done** | `apps/api/tests/support`, `conftest.py`, web `src/test/setup.ts`. |
| — | Testing guidelines | **Done** | [TESTING.md](./TESTING.md), `apps/api/tests/README.md`. |
| — | Testing folder structure | **Done** | Described in TESTING.md + [apps/web/TESTING.md](../../apps/web/TESTING.md) (web layout). |
| — | CI test integration | **Done** | `ci.yml`: js (lint, typecheck, test, build), python (`pytest -m "not integration"`), e2e. |
| — | OpenAPI / Swagger tests | **Done** | `apps/api/tests/api/test_openapi.py`. |

---

## Verdict

| Pillar | Summary |
|--------|---------|
| **Database** | **Production-grade foundation is in place** (migrations, soft delete, versioning, audit framework, indexes, seeds, ERD docs). Ongoing **schema optimization** and **broader RLS / audit coverage** are normal product work, not one-shot “complete.” |
| **Auth & security** | **Core enterprise pattern implemented** (JWT + rotating refresh, RBAC, Argon2, rate limits, session metadata, headers, documented threats). **Hardening gaps** are explicitly listed (CSRF depth, OIDC, key rotation, gateway). |
| **Testing** | **Scalable automation baseline is in place** (markers, layers, CI, E2E). **Integration in CI** and **MSW** are the main **Partial** items. |

Use this file in PRs and audits; update row status when you close backlog items.
