# StudyOS — Final Canonical Architecture (Lead Decision Record)

**Status:** authoritative for new implementation  
**Quick reference:** See [docs/STUDYOS_COMPLETE_SUMMARY.md](../STUDYOS_COMPLETE_SUMMARY.md) for master overview.  
**Supersedes:** conflicting fragments in `STUDYOS/MASTER_README.md`, `STUDYOS/plan/ROADMAP.md` stack lines, and `APP_PROMPT.prompt` where they disagree with this file.  
**Companion docs:** `SYSTEM_DESIGN.md`, `MONOREPO_STRUCTURE.md`, `ENTERPRISE_ARCHITECTURE.md`

---

## 1. Documentation conflicts resolved

| Conflict | Resolution | Rationale |
|----------|------------|-----------|
| **Vite + React Router** vs **Next.js** (MASTER diagram) | **Next.js 15 (App Router) + React 19 + TypeScript strict** | Enterprise deployment on Vercel, **middleware** for auth + tenant routing, **Server Actions / Route Handlers** as BFF (hide service role, centralize validation), **RSC** for dashboard/syllabus reads to cut client JS, SEO for marketing and institute landing. Original Vite guidance remains valid for **embedded widgets** or a future lightweight shell only if product demands it—not the main product line. |
| `SKILL_AI_AGENTS.md` / `SKILL_DATABASE.md` vs actual `skills-app/` | Canonical names: **`SKILL_AGENTS.md`**, **`SKILL_DATABASE.md`** ✅ created, **`SKILL_BACKEND.md`** | Single naming scheme complete; `SKILL_DATABASE.md` contains migrations + RLS + indexing patterns (ready for development). |
| ROADMAP `[✅]` MVP items vs empty repo | Checkmarks are **non-authoritative** until linked to merged code | Replace with issue IDs in tracker; this architecture doc is the engineering north star. |
| “NotebookLM API” | **No dependency** on private Google APIs | Export-only markdown/ZIP pipeline owned by StudyOS. |

---

## 2. Repository strategy: **monorepo (canonical)**

**Decision:** **Turborepo + pnpm** in one git repository (`studyos`).

**Why (not polyrepo):**

- Shared **types**, **Zod contracts**, **UI**, and **AI prompts** across web, workers, and admin surfaces.  
- Atomic refactors across API + DB + client.  
- One CI pipeline with affected-only builds (`turbo run build --filter=...`).  

**Polyrepo only** for legally isolated PCI-heavy services or acquired products—out of scope until payment/compliance audit demands separation.

---

## 3. Frontend (canonical)

| Item | Choice |
|------|--------|
| Framework | **Next.js 15 App Router** |
| Language | **TypeScript (strict)** |
| Styling | **Tailwind CSS** + **shadcn/ui** (Radix primitives) |
| Data fetching | **TanStack Query v5** + Server Components where appropriate |
| Client global UI state | **Zustand** (minimal: UI chrome, ephemeral wizard state) |
| URL state | **nuqs** (or equivalent) for shareable filters |
| Forms | **React Hook Form** + **Zod** |
| i18n | **next-intl** (App Router–native) — English first; Tamil/Hindi/Telugu phased per `ROADMAP.md` |
| Markdown / math | **react-markdown** + **KaTeX**; **sanitize** with DOMPurify server/client policy in `SYSTEM_DESIGN.md` |
| Offline | **Dexie** + **Serwist** (Workbox-compatible) for PWA shell and checklist/notes queue (see `SYSTEM_DESIGN.md`) |
| Mobile | **Mobile-first** layouts; PWA install; no React Native in Phase 1–2 (TWA acceptable later) |

**Why not Vite SPA as primary:** At millions of users, **security headers, SSR for first paint, and BFF** matter more than Vite’s marginal dev-speed advantage; Turborepo restores fast incremental dev.

---

## 4. Backend architecture (canonical)

**Pattern:** **Supabase-centric BaaS + thin application backends**

| Layer | Responsibility |
|-------|----------------|
| **Supabase PostgreSQL** | System of record: users profile extension, syllabus, progress, notes metadata, quizzes, chat transcripts, billing refs, analytics backup tables |
| **Supabase Auth** | Identity: email/password, Google OAuth, magic link; **phone OTP** via native hook or custom token (MSG91/Twilio) |
| **Supabase Storage** | Private user notes, institute assets, signed URLs |
| **Supabase Realtime** | Progress/notifications where push beats polling |
| **Supabase Edge Functions (Deno)** | **JWT-verified** webhooks (Razorpay), **short** idempotent tasks, cron **dispatchers** (enqueue work, not 2-minute LLM jobs) |
| **Next.js Route Handlers (Node runtime)** | Thin **BFF** where useful (SSR data, cookie-only flows); heavy AI/webhooks prefer **`apps/api` (FastAPI)** — see `docs/engineering/ADR-001-fastapi-service-layer.md` |
| **Async jobs (scale path)** | **Inngest** (or Trigger.dev) in `apps/workers` or Vercel-hosted worker—**NCERT indexing**, bulk roadmap regen, weekly rollups |

**Why split Edge vs Node:** Deno Edge has **CPU/time limits** and awkward native deps; LangGraph + some PDF/ML stacks fit **Node** better. Edge remains ideal for **payment webhooks** and **fast auth checks**.

---

## 5. Database strategy (canonical)

| Item | Choice |
|------|--------|
| Primary store | **PostgreSQL (Supabase)** |
| Extensions | **pgvector**, **pg_cron**, **uuid-ossp** (or pgcrypto), **moddatetime** |
| Migrations | **Supabase SQL migrations** versioned in repo (`supabase/migrations`)—single pipeline |
| Tenancy | **`institute_id` nullable** on user profile + **RLS**; subdomain routing in Next middleware |
| Read scaling | Start **connection pooling** (Supabase pooler); add **read replica** when analytics crushes primary (Phase 4+) |
| Event analytics | **PostHog** product analytics + **optional** warehouse export (BigQuery/Snowflake) later—not dual-primary-writes on Postgres for every click at day one |

**Why not separate OLTP DB early:** Operational simplicity; Supabase scales to large NEET cohorts if hot paths are cached and writes are shaped.

---

## 6. AI orchestration architecture (canonical)

| Item | Choice |
|------|--------|
| Agent framework | **LangGraph** (TypeScript) in **`packages/ai`** |
| Model routing | **Declarative router** (task class → provider/model/fallback chain) + **budget caps** |
| Structured I/O | **Zod** schemas for all agent outputs persisted to DB |
| RAG | **pgvector** in Supabase; chunk pipeline in workers; **optional** reranker later |
| Tracing | **LangSmith** (required for production AI debugging) |
| **BYOK** | **Browser-direct** to LLM providers from client for user keys (**never** stored server-side); StudyOS server paths only for **platform keys** and **server-side RAG** |
| Guardrails | XML/structured delimiters + max input sizes + **output validators** before DB commit |

**Why AI-first but server-centric for platform AI:** Centralizes policy, logging, PII scrubbing, and spend controls. BYOK remains client-direct per existing security doctrine.

---

## 7. Auth system (canonical)

| Item | Choice |
|------|--------|
| Provider | **Supabase Auth** |
| Web integration | **`@supabase/ssr`** + Next middleware (refresh, protected routes) |
| Sessions | HttpOnly cookie pattern per Supabase SSR guidance |
| MFA | **TOTP** Phase 2+ (teachers/admins earlier if required) |
| Roles | **App roles** in Postgres (`student | teacher | institute_admin | platform_admin`) synced from signup/onboarding + admin tooling—not Supabase custom claims alone |
| Multi-tenant context | Resolved in middleware + injected into **RLS session variables** where needed (`set_config('request.jwt.claims', ...)`) pattern per Supabase best practice |

---

## 8. State management (canonical)

| Concern | Tool |
|---------|------|
| Server data | TanStack Query |
| Auth session | Supabase client + minimal React context |
| UI / layout | Zustand (small slices) |
| Forms | RHF local state |
| Offline queue | Dexie + explicit sync engine (see `SYSTEM_DESIGN.md`) |

**Why not Redux:** Boilerplate vs benefit; revisit only if time-travel debugging becomes a hard requirement.

---

## 9. Deployment strategy (canonical)

| Surface | Host |
|---------|------|
| Web app | **Vercel** (preview + production environments) |
| DB/Auth/Storage | **Supabase** (staging + production projects) |
| Redis | **Upstash** (rate limit + idempotency keys + short-lived caches) |
| DNS / CDN | **Cloudflare** in front (DNS, WAF rules, optional static NCERT caching) |
| Background jobs | **Inngest Cloud** (or self-hosted later) when cron/LLM workloads exceed limits |

**Regions:** Primary DB closest to **majority users (India)**; accept slightly higher latency for global admins until multi-region is justified.

---

## 10. Observability stack (canonical)

| Concern | Tool |
|---------|------|
| Errors + perf | **Sentry** (Next + Edge Functions) |
| Product analytics | **PostHog** |
| LLM traces | **LangSmith** |
| Web vitals | **Vercel Speed Insights** |
| Logs | **Vercel Runtime Logs** + **Axiom** (optional) for high-volume structured logs |

**Why not 10 tools day one:** Operational fatigue; add OpenTelemetry export when SRE headcount appears.

---

## 11. Testing stack (canonical)

| Layer | Tool |
|-------|------|
| Unit / integration | **Vitest** |
| Components | **Testing Library** |
| E2E | **Playwright** |
| API contracts | **Zod** shared types + **MSW** in tests |
| DB | **Supabase local** + **pgTAP** or SQL assertion tests in CI for RLS |

---

## 12. Security posture (non-negotiables)

- **RLS on every user table**; service role only in server/worker runtimes.  
- **CSP + HSTS** via Next `headers()` + Cloudflare.  
- **No LLM API keys in Postgres**; platform keys in Vercel/Supabase secrets only.  
- **DOMPurify** (or sanitize pipeline) on any user/AI HTML path.  
- **Signed URLs** for Storage; **magic-byte** file checks server-side for uploads that touch Storage.

---

## 13. Scale posture (millions of users)

| Mechanism | Application |
|-----------|-------------|
| Edge caching | Public syllabus JSON CDN-cached |
| Redis | Rate limits, idempotency, hot feature flags |
| Async workers | Heavy AI + indexing off request path |
| Write shaping | Append-only events table or batched metrics—not per-click synchronous writes at peak |
| Feature flags | PostHog or LaunchDarkly later—start PostHog |

---

*This document is the single decision baseline. Update it via PR with an ADR appendix when changing stack.*

---

## 14. Document map (implementation package)

All paths below are under **`docs/architecture/`** unless noted.

| Document | Role |
|----------|------|
| `docs/architecture/SYSTEM_DESIGN.md` | C4 flows, trust boundaries, offline/sync |
| `docs/architecture/MONOREPO_STRUCTURE.md` | Repo layout, package boundaries |
| `docs/architecture/API_ARCHITECTURE.md` | BFF vs Supabase, errors, idempotency |
| `docs/architecture/DATABASE_SCHEMA_PLAN.md` | Migrations, tables, RLS matrix |
| `docs/architecture/DATABASE_PLAN.md` | Ops, scaling triggers, backups |
| `docs/architecture/AI_SYSTEM_DESIGN.md` | LangGraph, RAG, cost, safety |
| `docs/architecture/DEVOPS_PLAN.md` | CI/CD, envs, incidents |
| `docs/architecture/IMPLEMENTATION_PHASES.md` | Technical milestone phases |
| `docs/architecture/IMPLEMENTATION_ROADMAP.md` | MVP → enterprise waves |
| `docs/architecture/ENTERPRISE_ARCHITECTURE.md` | Domains, NFRs, governance |
| `docs/architecture/DEVELOPMENT_PHASES.md` | Team workflow, DoR/DoD |
| `docs/architecture/FEATURE_PRIORITY.md` | P0/P1 stack-ranked |
| `docs/engineering/ADR-001-fastapi-service-layer.md` | Service API choice (FastAPI vs Node-only) |
| `docs/product/plan/*` | Product roadmap & prompts (NEET) |
