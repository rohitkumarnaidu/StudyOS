# StudyOS — enterprise performance report

This document summarizes **bottleneck analysis**, **optimizations applied** in this iteration, and a **prioritized backlog** for continued enterprise hardening. It complements `docs/architecture/` and the AI design notes.

---

## 1. Executive summary

StudyOS is a **monorepo** (Next.js web + FastAPI API + Supabase/Postgres). The main runtime costs are:

1. **Browser**: JavaScript bundle size, hydration, and redundant client fetches.
2. **API**: Connection pool behavior behind PgBouncer, per-request object churn on hot paths, and AI orchestration.
3. **Data plane**: Query shape and indexes (migrations define indexes; application SQL should stay index-friendly).

This pass focused on **high-leverage, low-risk** changes: HTTP caching for health probes, **shared AI conversation memory + MCP registry** in the API process, **singleton default prompt registry**, safer **asyncpg pool** defaults for poolers, **React Query** defaults, **deduplicated session fetches**, **lazy-loaded Sonner**, **Next.js `optimizePackageImports`**, optional **`STUDYOS_AI_WARM_ON_START`** LLM chain warm-up, **bundle analyzer** wiring, and an **async RSC dashboard shell** for read-heavy layout data.

---

## 2. Bottleneck analysis

| Area | Symptom | Root cause (typical) | Severity | Mitigation (this PR / backlog) |
|------|---------|----------------------|----------|--------------------------------|
| Web — session | Extra `/api/auth/session` calls | Strict Mode + multiple consumers | Medium | In-flight dedupe + `cache: "no-store"` |
| Web — TanStack Query | Refetch on tab focus | `refetchOnWindowFocus: true` in prod | Medium | Disable in production; longer `staleTime` |
| Web — bundle | Slow TTI on marketing | Eager `sonner` + full package imports | Medium | `next/dynamic` Toaster; `optimizePackageImports` |
| API — health | Load balancer hammers `/healthz` | No HTTP cache headers | Low | `Cache-Control: public, max-age=5, stale-while-revalidate=30` |
| API — Postgres | Latency / prepared statement errors | PgBouncer + asyncpg statement cache | High | `statement_cache_size=0`; document `max` pool tuning |
| API — AI memory | Conversation “forgot” between requests | New `SessionConversationMemory` per `AIService` | High | Shared `app.state.ai_conversation_memory` |
| API — AI MCP | Repeated JSON parse of MCP config | New registry per request | Low | Shared `app.state.mcp_registry` |
| API — prompts | Tiny CPU on each AI call | New `PromptRegistry` from dict | Low | Singleton `PromptRegistry.default()` |
| API — AI chain | Provider list rebuilt | `build_llm_chain` per request | Medium | Optional **`STUDYOS_AI_WARM_ON_START`**: pre-build chain at startup (shared httpx client) |
| DB — queries | Slow lists as data grows | Missing indexes / wide selects | TBD | Audit with `EXPLAIN`; add covering indexes per route |

---

## 3. Optimization summary (implemented)

### Web (`apps/web`)

- **`next.config.ts`**: `experimental.optimizePackageImports` for `@tanstack/react-query`, `sonner`, `react-hook-form`, `@hookform/resolvers` to improve tree-shaking; **`@next/bundle-analyzer`** when `ANALYZE=true` (run `pnpm run analyze` from `apps/web`).
- **Dashboard**: async **RSC shell** (`DashboardShell` + `server-only` `getDashboardShellContext`) so read-heavy copy and future DB/API reads stay off the client bundle; keep interactive widgets in separate `use client` islands.
- **`providers.tsx`**: `next/dynamic` for `<Toaster />` (`ssr: false`) to trim initial JS and defer toast UI.
- **`query-client.ts`**: `staleTime` 120s, `gcTime` 10m, `refetchOnWindowFocus` **only in development**, `networkMode: "online"`.
- **`session-provider.tsx`**: single-flight session probe + `fetch(..., { cache: "no-store" })`.
- **`use-api-health.ts`**: longer `staleTime` / `gcTime` for the example health probe.

### API (`apps/api`)

- **`/v1/healthz` & `/v1/readyz`**: `JSONResponse` with short public cache + `stale-while-revalidate` to absorb LB polling.
- **`lifespan`**: shared `SessionConversationMemory` + `MCPConnectorRegistry` on `app.state` (used by `AIService` when present).
- **`PromptRegistry.default()`**: process-wide singleton template map.
- **`asyncpg.create_pool`**: `max_inactive_connection_lifetime` + `statement_cache_size=0` (PgBouncer-safe default).
- **`STUDYOS_AI_WARM_ON_START`**: when `true`, `build_llm_chain` runs at startup; `AIService` reuses `app.state.llm_chain` with the shared httpx client (faster first token, slightly slower boot).

### AI request handling

- Conversation transcripts keyed by `user_sub` + `conversation_key` now persist **across requests** in a long-lived process (until TTL eviction), reducing repeated context loss and duplicate user turns.
- MCP connector config is parsed once per process lifetime (when lifespan runs).

---

## 4. Performance report (how to measure)

| Metric | Tool / approach | Target (indicative) |
|--------|-----------------|---------------------|
| Web TTFB / LCP | Lighthouse CI, Web Vitals | LCP < 2.5s on broadband for marketing |
| JS bundle | `next build` output, `@next/bundle-analyzer` | Reduce main-thread long tasks |
| API latency | OpenTelemetry + histograms on route + provider | p95 chat < SLO per model tier |
| DB | `EXPLAIN (ANALYZE, BUFFERS)` on hot queries | Seq scans only where expected |
| AI | Tokens/sec, time-to-first-byte streaming, error rate | Dashboards per provider |

---

## 5. Prioritized backlog

**Recently completed:** bundle analyzer (`pnpm run analyze` in `apps/web`), dashboard async RSC shell, `STUDYOS_AI_WARM_ON_START`.

1. **Route-level code splitting**: `next/dynamic` for authenticated dashboard modules once they grow (charts, editors).
2. **Server Components**: extend RSC pattern to list/detail pages; keep mutations in server actions or small client islands.
3. **API response caching**: Redis for idempotent GETs (non-user-specific) with ETag.
4. **DB**: add query module with prepared statements where safe; review `auth_sessions` / `profiles` access paths under load.
5. **CDN / edge**: cache static assets aggressively; keep HTML dynamic.

---

## 6. Notes

- **Security vs caching**: never apply public `Cache-Control` to authenticated JSON; health endpoints are the exception.
- **PgBouncer**: keep `statement_cache_size=0` unless you run session-mode pooling with asyncpg compatibility guarantees.
