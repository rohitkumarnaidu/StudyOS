# STUDYOS — Agent Guide

> **CRITICAL**: This is a pnpm + Turborepo monorepo. Always run commands from the repo root. Node 20, Python 3.12.

## Quick Commands

| Task | Command |
|------|---------|
| Install deps | `pnpm install` |
| Dev (all) | `pnpm dev` |
| Dev (web only) | `pnpm --filter @studyos/web dev` |
| Dev (api only) | `pnpm --filter @studyos/api dev` |
| Lint (all) | `pnpm turbo run lint --continue` |
| Typecheck (all) | `pnpm turbo run typecheck --continue` |
| Test (all) | `pnpm turbo run test --continue` |
| Build (all) | `pnpm turbo run build --continue` |
| DB migrate | `pnpm supabase migration up` (or `supabase/migrations/*.sql`) |
| Docker dev | `docker compose -f docker/docker-compose.yml up` |

### API-specific (apps/api)
```bash
cd apps/api
uv run ruff check src
uv run mypy src
uv run pytest
uv run uvicorn studyos_api.main:create_app --factory --reload
```

### Web-specific (apps/web)
```bash
cd apps/web
pnpm exec next lint
pnpm exec tsc --noEmit
pnpm exec vitest run
pnpm exec playwright test
```

## Architecture

### Monorepo Structure
```
apps/
  web/          Next.js 16 (React 19) — BFF + frontend
  api/          FastAPI (Python 3.12) — business logic
packages/
  config/       Zod-validated env config
  tsconfig/     Shared TS configs
supabase/
  migrations/   SQL migrations (sequential naming)
docker/         docker-compose.yml for local dev
```

### Auth Flow (BFF Pattern)
- **Cookies**: `studyos_access` (JWT), `studyos_refresh` (opaque), `studyos_session` (legacy demo)
- **Middleware** (`apps/web/middleware.ts`): Edge runtime, verifies JWT, silent refresh, sets HttpOnly cookies
- **Route handlers**: `/api/auth/login`, `/api/auth/signup`, `/api/auth/logout`, `/api/auth/refresh`, `/api/auth/session`
- **Upstream API**: Proxied to FastAPI (`/v1/auth/*`) via `internalApiBaseUrl()`
- **Supabase OAuth**: Google sign-in via `@supabase/supabase-js` (browser client), callback → `/api/auth/callback`
- **Session provider**: `SessionProvider` (client context), `AppSessionGate` (protected route wrapper)
- **Demo credentials**: `demo@studyos.app` / `demo`

### Web (`apps/web`)
- **Next.js 16** with App Router, Turbopack, React 19
- **`@/` alias** → `src/`
- **`"use client"` / `"use server"`** directives required for client/server boundaries
- **Tailwind v4** — CSS-first config, no `tailwind.config.js`
- **UI components**: `@/shared/components/ui/` — Radix primitives + `cva` variants (shadcn pattern)
- **Form components**: `@/shared/components/form/` — RHF + Zod integration
- **State**: Zustand (`@/shared/stores/`) for client state, React Query for server state
- **Routes**: `@/shared/config/routes.ts` — centralized route constants
- **Error handling**: `ErrorBoundary` class component, `notifyError`/`notifySuccess` toast helpers
- **Supabase**: Optional browser client (`@/shared/lib/supabase/browser-client.ts`)
- **Monitoring**: Sentry (`@/shared/lib/sentry.ts`) — error boundaries + replay
- **Analytics**: PostHog (`@/shared/lib/posthog.tsx`) + typed events (`@/shared/lib/analytics.ts`)
- **i18n**: `@/shared/config/i18n.ts` + `@/shared/config/translations.ts` (en, hi, ta)
- **Animations**: `framer-motion` via `@/shared/components/ui/animated-page.tsx`

### API (`apps/api`)
- **FastAPI** with structlog (JSON logging), SlowAPI (rate limits)
- **Env prefix**: All vars use `STUDYOS_` prefix (validated in `packages/config`)
- **Auth endpoints**: `/v1/auth/login`, `/v1/auth/register`, `/v1/auth/refresh`, `/v1/auth/logout`
- **Middleware**: Request ID, request logging (timing), CSRF double-submit cookie, security headers
- **AI**: Multi-provider (Ollama/OpenAI/Anthropic), `FallbackOrchestrator`, MCP registry
- **Pydantic v2** for request/response validation
- **Caching**: Redis with in-memory fallback (`services/cache.py`)
- **Upload security**: Magic-byte validation, size limits, MIME checks (`services/upload_security.py`)

### Database
- **PostgreSQL** via Supabase
- **Migrations**: `supabase/migrations/YYYYMMDDHHMMSS_description.sql` (sequential, idempotent)
- **Soft deletes**: `deleted_at` column + triggers (auto-set on DELETE, filter in queries)
- **RLS**: Row-level security enforced on all tenant-scoped tables
- **Key tables**: `profiles`, `exam_profiles`, `subjects`, `chapters`, `topics`, `subtopics`, `subtopic_completions`, `user_chapter_progress`, `streaks`, `ai_token_usage`, `refresh_sessions`, `auth_credentials`
- **Phase 1 migrations**: 14 total (001-011 Phase 0, 012 seed topics/subtopics, 013 streaks, 012_phase1 improvements)

## Testing

### Web
- **Unit/Integration**: Vitest + Testing Library (`pnpm exec vitest run`)
- **E2E**: Playwright (`pnpm exec playwright test`)
- **Test files**: `*.test.ts` / `*.test.tsx` alongside source or in `__tests__/`

### API
- **Test runner**: pytest (`uv run pytest`)
- **HTTP testing**: httpx ASGI test client
- **Mocking**: respx for external API calls
- **Test files**: `tests/` directory under `apps/api/`

## CI/CD
- **GitHub Actions**: `.github/workflows/ci.yml`
- **Pipeline**: lint → typecheck → test → build (all with `--continue`)
- **Node**: 20.x, **Python**: 3.12
- **Caching**: pnpm store, pip/uv cache, Next.js build cache

## Important Conventions

### Breaking Change Warning
> **`apps/web/AGENTS.md` exists** — read it before making changes to the web app. It contains Next.js-specific constraints and patterns.

### File Naming
- Web: kebab-case for routes, PascalCase for components
- API: snake_case for modules, PascalCase for classes
- Migrations: `YYYYMMDDHHMMSS_description.sql`

### Env Variables
- **Public (web)**: `NEXT_PUBLIC_*` prefix (exposed to browser)
- **Private**: `STUDYOS_*` prefix (validated via Zod in `packages/config`)
- **Never** commit `.env` files; use `.env.example` as template

### API Communication
- Web → API: Internal fetch via `internalApiBaseUrl()` (not public URL)
- All API responses: JSON, Pydantic-validated
- Error format: `{ detail: string }` or `{ error: string }`

### Component Patterns
- UI primitives: `@/shared/components/ui/` — do not modify directly; extend via composition
- Feature components: `@/features/{feature}/components/`
- Feature hooks: `@/features/{feature}/hooks/` — React Query + optimistic updates
- Feature API: `@/features/{feature}/api.ts` — typed API client functions
- Server actions: `"use server"` at top of file, validate inputs with Zod
- Progress system: `@/features/progress/` — `toggleSubtopic()`, `ProgressRing`, `StreakBadge`, auto-computed from completions

### Phase 7 Additions
- **Error monitoring**: Sentry SDK init + `sentry.client.config.ts` with tunnel route
- **Product analytics**: PostHog provider + typed `StudyOSEvent` union for all tracked events
- **CSP headers**: Added to `next.config.ts` — restricts script/style/connect sources
- **Redis caching**: `services/cache.py` with in-memory fallback, TTL, pattern invalidation
- **Upload security**: `services/upload_security.py` — magic bytes, 50MB limit, MIME validation
- **i18n**: Locale config (en/hi/ta) + translations + `useTranslation` hook
- **Animations**: Framer Motion `AnimatedPage` + `AnimatedCard` components
- **A11y**: Smooth transitions, reduced motion, high contrast support in `globals.css`

## Docker
- `docker/docker-compose.yml`: postgres, redis, api, web
- API: `uvicorn` with reload in dev
- Web: `next dev` with Turbopack
- Volumes: postgres data, api source, web source
