# StudyOS — Executive Summary & Quick Reference

**Document:** Master overview for stakeholders, investors, and team leads
**Status:** Phase 0 complete, Phase 1 in progress
**Audience:** Non-technical stakeholders, CTOs, investors

---

## The Vision

**StudyOS** is an **AI-powered, mobile-first learning platform** designed specifically for students preparing for competitive exams (MVP: NEET 2026).

**What makes it different:**
1. **Offline-first checklist** — PWA that works without internet (critical for India's connectivity)
2. **AI tutoring** — Multi-provider LLM routing (Anthropic primary, fallback chain)
3. **PDF + Mind Map pipeline** — 400+ notes processed, structured, searchable, interactive viewer like Physics Wallah
4. **Study mode** — Full-screen reading, highlights, personal notes, bookmarks
5. **NEET-specific** — 91 chapters, 450+ subtopics, tier-based weightage
6. **Streaks + gamification** — Daily login motivation, progress rings, achievement badges
7. **Free platform** — No paywalls, no subscriptions, accessible to all

---

## Market Opportunity

**Total addressable market (TAM):** ~14 million NEET aspirants in India (2026 exam cycle)

**MVP focus:**
- **Primary user:** Individual NEET student (urban, >15 Mbps internet OR offline capable)
- **Secondary:** Coaching institutes (B2B batch management, post-launch)
- **Tertiary:** Parents (push notifications on progress, post-launch)

**Revenue model:** Free platform. Monetization deferred to post-launch (institute tier, sponsorships, or grants).

---

## Technical Foundation

**Monorepo:** Single Git repository, atomic deployments
**Frontend:** Next.js 16 (React 19) deployed to Vercel
**Backend:** FastAPI (Python) + Supabase (PostgreSQL)
**AI:** Multi-provider (Anthropic, OpenAI, Ollama) with fallback + streaming
**Infrastructure:** Supabase + Vercel + Upstash (Redis)
**Team:** 2–3 full-stack engineers

**Why this stack:**
- Zero-config scaling (Vercel + Supabase managed services)
- Type-safe end-to-end (TypeScript + Python type hints)
- AI-native (multi-provider routing, RAG, LangGraph)
- Offline-capable (PWA + Dexie IndexedDB)
- Cost-efficient (free tier for Vercel, Supabase connection pooling)

---

## Timeline (22 weeks to launch)

| Phase | Focus | Weeks | Team |
|-------|-------|-------|------|
| **Phase 0** | Monorepo setup, CI/CD | 1 | 1 DevOps |
| **Phase 1** | Auth + Syllabus + Progress + Streaks | 2 | 2 FE/BE |
| **Phase 2** | Offline + PWA + Settings | 2 | 2 FE/BE |
| **Phase 3** | AI Tutor Chat | 3 | 2–3 FE/BE |
| **Phase 4** | PDF + Mind Map Pipeline | 4 | 2–3 FE/BE |
| **Phase 5** | Quizzes + Mock Tests | 4 | 2–3 FE/BE |
| **Phase 6** | Analytics + Roadmap + Motivation | 3 | 2 FE/BE |
| **Phase 7** | Scale + Polish + Launch | 3 | 1–2 DevOps/QA |
| **TOTAL** | **Launch-ready** | **22 weeks** | **2–3 FTE** |

---

## Phase 0: What's Done

**Status:** 100% complete, all checks passing

### Infrastructure
- GitHub Actions CI/CD (lint, typecheck, test, build)
- Monorepo structure (pnpm + Turborepo)
- Docker skeleton (Supabase local, API, web, redis, postgres)

### Code quality
- TypeScript strict mode (100% coverage)
- Python type-checking with mypy (69 source files)
- Unit tests wired (15/15 passing)
- E2E test scaffolding (Playwright ready)

### Auth + Syllabus (Phase 1 partial)
- Login/signup forms + BFF routes + JWT + rotating refresh tokens
- Google OAuth with PKCE flow
- Dashboard shell with chapter list
- Syllabus API (91 chapters seeded)
- Progress API (toggle subtopic, get summaries)
- 11 database migrations with RLS policies
- AI backend module (multi-provider, streaming, MCP)

### Current capability
- Build time: ~90 seconds
- Test execution: <10 seconds
- CI pipeline: <30 seconds (cached)

---

## Phase 1: Next Milestone (Week 1-2)

**Goal:** User can sign up → see syllabus → mark topics complete → see progress rings + streak

**Key deliverables:**
1. Seed 450+ subtopics for all 91 chapters
2. Wire progress UI (enable checkboxes, optimistic updates)
3. Streak system (table, computation, dashboard badge)
4. Dashboard enhancement (progress rings, study stats)
5. Chapter detail page with topics/subtopics tree

**Success criteria:**
- New user signup → dashboard in <2 seconds
- Toggle subtopic → progress ring updates live
- Refresh page → progress persists
- Zero data leaks (RLS tested)
- 20+ integration tests passing

---

## Cost Estimate

### Monthly (at 10k active users)

| Service | Cost | Notes |
|---------|------|-------|
| **Vercel** | $10–50 | Serverless, auto-scaling |
| **Supabase** | $50–200 | Postgres + Auth + Storage |
| **Upstash Redis** | $10–30 | Rate limits, cache |
| **Anthropic API** | $100–300 | AI calls (budget-gated) |
| **OpenAI API** | $20–50 | Fallback + vision model |
| **Sentry** | $20 | Error tracking |
| **PostHog** | $0 (free tier) | Analytics |
| **Domain + CDN** | $10/month | Cloudflare, DNS |
| **Total** | **$220–660/month** | ~$0.02–0.07 per active user |

**Scaling to 1M users:** ~$5k–10k/month (cost per user stays flat due to managed services)

---

## Top Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Supabase data leak** (RLS bug) | Critical | Early RLS boundary tests, security audit |
| **AI token cost overrun** | High | Hard budget caps, real-time tracking |
| **Offline sync conflicts** | High | Idempotency keys, timestamp-based CRDTs |
| **PDF processing failures** | Medium | Retry logic, error recovery, manual reprocess |
| **400+ PDF bulk import performance** | Medium | Async queue, progress tracking, resume on failure |
| **pgvector search quality at scale** | Medium | HNSW tuning, hybrid search, chapter filtering |
| **Syllabus inaccuracy** | Medium | Domain expert review, community feedback |

---

## Go/No-Go Checklist for Phase 1

- [x] All Phase 0 tests passing
- [x] GitHub Actions CI pipeline verified
- [x] Monorepo builds locally (`pnpm dev`)
- [x] All engineers read `FINAL_ARCHITECTURE.md`
- [ ] Supabase staging project created
- [ ] Database migrations run against staging
- [ ] Topics/subtopics seed data ready
- [ ] API contracts finalized (request/response schemas)
- [ ] Security review of auth flow scheduled
- [ ] Capacity: 2+ engineers available for 2 weeks

**Current status:** 5/10 items ready (Supabase + seed data + security review TBD)

---

## Documentation Map

**Quick links for team members:**

| Role | Start here |
|------|-----------|
| **CTO / Architect** | `FINAL_ARCHITECTURE.md` (15 min) |
| **Full-stack engineer** | `SYSTEM_DESIGN.md` (1 hour) |
| **Frontend engineer** | `MONOREPO_STRUCTURE.md` (20 min) |
| **Backend engineer** | `API_ARCHITECTURE.md` + `DATABASE_PLAN.md` (45 min) |
| **DevOps engineer** | `DEVOPS_PLAN.md` (30 min) |
| **QA engineer** | `IMPLEMENTATION_ROADMAP.md` (30 min) |
| **New team member** | `README.md` → `EXECUTIVE_SUMMARY.md` (1 hour) |

---

## Success Metrics (Launch)

### User engagement
- **Daily active users:** 1,000+ (Phase 1 launch)
- **Chapter views/day:** 5,000+
- **AI chat usage:** 20+ conversations/active user/week
- **Notes uploaded:** 50+ per active user
- **Session duration:** >15 min average

### Technical KPIs
- **API p99 latency:** <500ms
- **Page load (FCP):** <1.5s
- **Offline capability:** 100% of core features work without internet
- **PDF processing:** <60s per file
- **Search latency:** <200ms across 400+ notes
- **Uptime:** 99.9%
- **Error rate:** <0.1%

---

**Last updated:** 2026-05-16
**Next review:** Phase 1 completion
**Status:** Phase 0 complete, Phase 1 in progress
