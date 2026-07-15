# StudyOS — authentication & security architecture

This document explains **security decisions**, **attack surfaces**, and **mitigations** for the StudyOS stack (Next.js BFF + FastAPI + PostgreSQL). It complements `supabase/migrations/*` (sessions, credentials) and the API modules under `apps/api/src/studyos_api/security/` and `api/v1/routes/auth.py`.

**Matrix vs formal requirements:** [docs/engineering/ENTERPRISE_READINESS.md](../engineering/ENTERPRISE_READINESS.md) (section B).

---

## 1. Strategy: JWT access + rotating refresh

| Artifact | Role | Properties |
|----------|------|------------|
| **Access JWT** | Short-lived API credential | HS256, `iss`, `sub`, `roles`, `typ=access`, `exp` |
| **Refresh opaque token** | Long-lived rotation handle | Stored server-side as **SHA-256 hash** only; `family_id` groups rotations |
| **Password** | User secret | **Argon2id** (PHC string) in `auth_credentials.password_hash` |

**Why not long-lived JWT-only?** Revocation and device/session control require server-side state for refresh material. Access JWT stays stateless for fast API validation.

**Mitigations**

- **Theft of access JWT** — Short TTL limits window; HTTPS + `HttpOnly` cookies (Next BFF) reduce XSS exfiltration vs `localStorage`. Next **middleware** re-validates the access JWT on each navigation; if it is expired but the refresh cookie is still valid, the BFF performs a **silent refresh** against `/v1/auth/refresh` and re-issues cookies before the request continues.
- **Theft of refresh token** — Rotation on each refresh; reuse of a revoked refresh revokes the **entire `family_id`** (detects replay).
- **DB compromise** — Refresh table stores **hashes only**; passwords use Argon2id with per-hash salt.

---

## 2. BFF (Next.js) vs browser → API

**Decision:** Browser calls Next Route Handlers (`/api/auth/*`); Next server calls FastAPI with server-side `fetch`. Tokens are set as **HttpOnly** cookies: `studyos_access` (JWT), `studyos_refresh` (opaque). The legacy `studyos_session` cookie is still accepted by middleware for older demos. In production, set `STUDYOS_INTERNAL_API_BASE_URL` to a reachable API hostname (not `localhost` from Edge/serverless unless you use a VPC connector or same-host deployment).

**Attack:** CSRF against login/refresh/logout.

**Mitigations**

- `SameSite=Lax` (default) on cookies for cross-site request restrictions.
- Add **double-submit CSRF** (cookie + `X-CSRF-Token` header) on mutating routes when moving beyond same-site-only clients.
- For third-party SPAs, prefer **Authorization Code + PKCE** with your IdP instead of password POST from untrusted origins.

---

## 3. RBAC

- API encodes **roles** in the access JWT (`roles: string[]`).
- FastAPI maps roles → **permissions** via `ROLE_PERMISSIONS` (`deps/rbac.py`).
- Prefer **permission checks** (`require_permissions`) over raw role string compares for new endpoints.

**Attack:** privilege escalation via forged JWT.

**Mitigations**

- Verify **signature** (`STUDYOS_JWT_SECRET`), **issuer**, **exp**, and `typ=access` on every protected call.
- In production, **disable** `STUDYOS_ALLOW_LEGACY_DEMO_BEARER` (non-JWT demo tokens).

---

## 4. Rate limiting & abuse

- SlowAPI default limits + stricter limits on `/v1/auth/login` and `/v1/auth/refresh`.
- Add account-level lockout / exponential backoff at the IdP or API gateway for repeated failures (future hardening).

---

## 5. Audit & device/session tracking

- **Structured logs** (`structlog`) on login success/failure (`auth.login_*`).
- DB table `auth_sessions` records **user-agent** and **IP** (nullable `inet`) for refresh issuance (when using Postgres store).
- Global `audit_log` + triggers exist for high-value tables (see migration `20250613120001_*`); extend to auth tables if compliance requires immutable DB audit.

---

## 6. Secrets & environments

| Variable | Purpose |
|----------|---------|
| `STUDYOS_JWT_SECRET` | HS256 signing key (**≥32 chars**, unique per env) — **must match** Next middleware if verifying JWT at the edge. |
| `STUDYOS_DATABASE_URL` | Enables Postgres-backed refresh + password lookup. |
| `STUDYOS_INTERNAL_API_BASE_URL` | Next BFF → FastAPI base URL (server-only). |
| `STUDYOS_REFRESH_COOKIE_MAX_AGE` | Optional refresh cookie `max-age` override (seconds). |
| `STUDYOS_ALLOW_LEGACY_DEMO_BEARER` | Must be **false** in production. |

**Attack:** leaked `.env` or CI logs.

**Mitigations**

- GitHub/Vault secret stores; never commit real secrets.
- Production `Settings` validation rejects weak JWT secrets and demo bearer mode.

---

## 7. Transport & headers

- Next `next.config.ts` sets baseline security headers (frame, MIME sniffing, referrer, permissions).
- FastAPI `SecurityHeadersMiddleware` mirrors defense-in-depth for API responses.
- **CORS** restricted to configured browser origins; **TrustedHost** optional for host-header attacks behind misconfigured proxies.

---

## 8. Known follow-ups (enterprise backlog)

- **Key rotation** (`kid` header + JWKS or multi-secret validation).
- **OAuth2 / OIDC** (Supabase Auth, Auth0, Keycloak) replacing password POST.
- **Redis** denylist for revoked JWT `jti` when moving to fully stateless access tokens at scale.
- **mTLS** or **service mesh** for internal `web → api` calls in Kubernetes.
