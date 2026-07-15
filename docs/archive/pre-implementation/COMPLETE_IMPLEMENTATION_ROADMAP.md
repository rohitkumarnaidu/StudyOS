# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# StudyOS — Complete Implementation Roadmap & Architecture Overview

**Master document:** Comprehensive guide to the complete StudyOS system architecture, phase sequencing, and long-term roadmap.

**Audience:** CTOs, engineering leads, product managers, DevOps engineers  
**Last updated:** 2026-05-14  
**Status:** Ready for Phase 1 execution

---

## Part 1: Architecture Overview

### 1.1 System Vision

StudyOS is an **AI-first, mobile-first learning platform** designed for students preparing for competitive exams (MVP: NEET 2026). The platform combines:

- **Student core loop:** Structured syllabus → chapter checklist → AI tutoring → self-assessment → progress tracking → streaks/motivation
- **AI differentiator:** Multi-provider LLM routing (Anthropic primary, OpenAI fallback, Ollama for inference), RAG over NCERT, adaptive quizzes
- **Offline-first:** PWA with Dexie + Serwist, checklist works without network
- **Scale path:** B2B (coaching institutes), teacher dashboards, batch analytics by Phase 3+

### 1.2 Canonical Stack (FINAL_ARCHITECTURE.md)

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js 15 App Router + React 19 + TypeScript strict | Vercel deployment, Server Components reduce JS, SEO for landing |
| **Styling** | Tailwind CSS + shadcn/ui (Radix) | Enterprise UI library, themeable |
| **Client state** | TanStack Query v5 (server), Zustand (UI), Dexie (offline) | Proven, composable |
| **Backend (BFF)** | Next.js Route Handlers (Node) | Thin, auth-gated, hides Supabase service role |
| **Backend (workers)** | FastAPI + Python + LangGraph | AI agents, bulk jobs, type-safe |
| **Database** | Supabase (PostgreSQL + RLS) | Managed Postgres, built-in Auth + Storage + Realtime |
| **Auth** | Supabase Auth (email/password, Google OAuth) | No token management, Postgres-native |
| **Vector DB** | pgvector (Postgres extension) | RAG, chunk search, no separate vector DB |
| **Cache** | Upstash Redis | Rate limits, idempotency keys, session data |
| **Jobs** | Inngest (or self-hosted Trigger.dev) | Roadmap generation, bulk indexing, cron |
| **Deployment** | Vercel (frontend) + Railway/Fly (FastAPI) + Supabase | Zero-config scaling, managed services |
| **Observability** | Sentry (errors), PostHog (analytics), LangSmith (AI traces) | Production-grade monitoring |

---

## Part 2: Phase Sequencing

### Phase 0 — Foundation ✅ **COMPLETE**

**Duration:** 1 week  
**Deliverable:** Runnable monorepo with CI/CD

**Completed:**
- ✅ Monorepo setup (pnpm + Turborepo)
- ✅ Next.js 15 (App Router) boilerplate
- ✅ FastAPI service scaffolding
- ✅ GitHub Actions CI pipeline
- ✅ Test suites wired (Vitest + pytest)
- ✅ Lint + typecheck passing
- ✅ Database migrations system (Supabase)
- ✅ Documentation (ARCHITECTURE.md + README.md)

**Blockers removed:**
- Fixed lint error in web auth session handler
- Fixed test environment (trusted hosts + DATABASE_URL)
- Configured conftest.py for lifespan initialization

**Exit criteria met:** All checks pass ✅

---

### Phase 1 — Identity + Syllabus Read Model (3 weeks)

**Goal:** User can sign up, see chapter list, understand progress tracking architecture.

**Engineering milestones:**

1. **Supabase project + migrations (5 days)**
   - Create staging project (ProjectRef + API key)
   - Run 001–002 migrations (users, profiles, syllabus hierarchy)
   - Seed NEET 2026 syllabus (79 chapters)
   - Test RLS policies (student can't see other profiles)
   - Generate Postgres types → TypeScript

2. **Auth flow (5 days)**
   - Implement `POST /api/auth/login` (email/password + Google OAuth)
   - Implement middleware (cookie refresh, RLS session var injection)
   - Client: `SessionProvider` + `useSession` hook
   - Implement protected route gate: `/dashboard` requires auth
   - E2E test: signup → login → dashboard loads

3. **Syllabus read model (5 days)**
   - API: `GET /api/syllabus/chapters` (RSC server component)
   - API: `GET /api/syllabus/chapter/:id/topics` (nested)
   - Client: Mobile-first chapter list with hierarchical collapse
   - Performance: Cache with Next.js ISR + TanStack Query
   - E2E test: chapters load, can drill into topics

**Acceptance criteria:**
- New user signs up → onboarding selects exam → redirected to /dashboard
- Dashboard shows 79 NEET chapters, organized by subject
- Chapter click → shows 500+ topics nested
- No SQL in client, all queries via middleware-gated API
- RLS enforced (user cannot query other users' profiles)
- Tests: 20+ unit tests (auth, RLS, syllabus), E2E smoke test

**Database additions:**
```sql
001-users-and-auth.sql
  - public.users
  - public.profiles (app_role, exam, preferences)
  - RLS policies

002-syllabus.sql
  - public.exams, subjects, chapters, topics, subtopics
  - Seed NEET 2026 data
  - Indexes on foreign keys
```

---

### Phase 2 — Progress Tracking + Offline Checklist (2 weeks)

**Goal:** User can mark subtopics complete, see progress ring, data syncs offline.

**Engineering milestones:**

1. **Progress model + mutations (5 days)**
   - Migration `003` (progress table, RLS, streaks)
   - API: `POST /api/progress` (upsert progress with RLS)
   - Idempotency keys (Upstash Redis)
   - Client: Optimistic UI update (Zustand + TanStack Query)
   - Streak computation (nightly job + server-side)

2. **Offline-first PWA (5 days)**
   - Dexie schema for progress + notes
   - Serwist service worker (offline cache + sync)
   - Outbox pattern (queue mutations until online)
   - Conflict resolution (last-write-wins with timestamps)
   - Offline banner + sync indicator
   - E2E: complete subtopic offline → refresh → still complete

3. **Dashboard analytics (3 days)**
   - Progress ring (chapters % complete)
   - Streak counter + calendar heatmap
   - Time-on-app graphs (PostHog events)
   - Performance optimization (memoization, virtual lists for 1000+ items)

**Acceptance criteria:**
- User marks 10 subtopics → progress ring updates live
- Network disabled → marks 5 more → offline banner shows → network enabled → syncs
- No data loss in offline scenario
- Streak appears after 2+ days of activity
- Dashboard loads <1s (memoized)
- Tests: RLS boundary tests, offline sync tests (Playwright)

**Database additions:**
```sql
003-progress-and-streaks.sql
  - public.progress
  - public.streak_snapshots
  - RLS policies
  - Cron job for nightly reconciliation
```

---

### Phase 3 — Platform AI Tutor (3 weeks)

**Goal:** User opens chapter → "Ask me anything" chat → streams response with NCERT context.

**Engineering milestones:**

1. **RAG + pgvector (7 days)**
   - Seed pgvector with NCERT chunks (~50k vectors, 200 tokens each)
   - Implement `search_chapter_embeddings` RPC for cosine similarity
   - Cache hot chapters in Upstash (1h TTL)
   - Benchmark: <100ms latency for search

2. **LangGraph tutor agent (7 days)**
   - Tutor agent (retrieve → validate → generate → extract)
   - Model router (Anthropic primary, OpenAI fallback)
   - Token budgeting (daily limit, per-user config)
   - Output validator (Zod schema extraction)
   - LangSmith tracing for all invokes

3. **Streaming API + client (5 days)**
   - Route Handler: `POST /api/ai/chat` (SSE streaming)
   - Client: stream → typed response → Dexie save
   - Chat history UI (messages with metadata)
   - E2E: ask question → stream response → history persists

**Acceptance criteria:**
- User opens "Photosynthesis" chapter → types "What is photosynthesis?" → gets tutor response in <5s
- Response includes NCERT context + structured answer
- Token budget enforced (e.g., 100 tokens/day for free tier)
- Chat history saved and queryable
- BYOK works (user can paste their own Anthropic key, no tokens stored server-side)
- Tests: Agent tests (mocked LLM), budget enforcement tests, streaming tests

**Services added:**
```
apps/api/src/studyos_api/ai/
  - agents/tutor_agent.py
  - provider_factory.py (router logic)
  - budget/token_accounting.py
```

---

### Phase 4 — Notes + OCR + Storage (2.5 weeks)

**Goal:** User uploads handwritten notes → OCR extracts text → AI tags by chapter.

**Engineering milestones:**

1. **Storage infrastructure (5 days)**
   - Supabase Storage bucket (private per user)
   - Signed URLs (1-hour expiry for client read)
   - Virus scan policy (ClamAV worker or vendor)
   - Migration `004` (notes metadata table)

2. **Client-side OCR (5 days)**
   - Tesseract.js integration (browser-based)
   - Progress UX (animated upload + OCR bar)
   - Optimistic preview (show raw OCR before server processing)
   - Offline: queue uploads in Dexie, retry when online

3. **Structured extraction agent (3 days)**
   - Note-extraction agent (chapter linking, tagging, summary)
   - Embed notes → pgvector (searchable)
   - Version control (note_versions table for undo)
   - E2E: upload image → OCR → extraction → query by chapter

**Acceptance criteria:**
- Upload 2MB NEET notes PDF → <30s OCR + extraction
- Notes searchable by chapter + topic (vector similarity)
- Can revert note (versions table)
- Virus scan blocks malicious files
- Offline upload queuing works
- Tests: Storage RLS tests, OCR mock tests, version control tests

**Database additions:**
```sql
004-notes-and-storage.sql
  - public.notes
  - public.note_versions
  - public.note_embeddings
  - RLS policies
```

---

### Phase 5 — Adaptive Quizzes + Roadmap (3 weeks)

**Goal:** User takes quiz → weak areas identified → roadmap suggests focus chapters.

**Engineering milestones:**

1. **Quiz generation agent (7 days)**
   - Quiz agent (topic → 5–10 question generation)
   - Question types (MCQ, fill-blank, passage-based)
   - Difficulty adaptation (based on accuracy)
   - Scoring + mistake tracking
   - Migration `005` (quiz_sessions, quiz_responses)

2. **Roadmap generation (7 days)**
   - Roadmap agent (user profile + progress → study plan)
   - Async job (Inngest enqueue)
   - UI: Roadmap view with interactive timeline
   - Realtime updates (Supabase Realtime subscription)
   - Migration `006` (roadmaps table)

3. **Analytics dashboard (3 days)**
   - Weak area detector (low quiz scores by topic)
   - Recommendations engine (suggest chapters)
   - Streak leaderboards (optional, optional for motivation)
   - Performance: <200ms query for all analytics

**Acceptance criteria:**
- User takes quiz on "Photosynthesis" → 6/10 correct → marked as weak
- Roadmap generation triggered → <10s job → shows study plan
- Leaderboard shows top 100 students (anonymized)
- Tests: Agent tests (mocked LLM), analytics aggregation tests

**Database additions:**
```sql
005-quizzes.sql
  - public.quiz_sessions
  - public.quiz_responses
  - RLS policies

006-roadmaps.sql
  - public.roadmaps
  - public.roadmap_items
```

---

### Phase 6 — Admin + Teacher Tools (2 weeks)

**Goal:** Coaching institutes can track batches, view student progress, send announcements.

**Engineering milestones:**

1. **Institute multi-tenancy (5 days)**
   - Subdomain routing: `inst-name.studyos.app` → institute context
   - Institute profile + branding (logo, colors)
   - Migration `007` (institutes, batches, batch_students)
   - RLS multi-tenant scope (teachers see only their batch)

2. **Teacher dashboard (5 days)**
   - Batch overview (progress aggregates, attendance)
   - Student progress drilldown
   - Bulk messaging (Twilio/WhatsApp for announcements)
   - Custom syllabus override (institute-specific topics)
   - E2E: teacher logs in → sees batch → selects student → views details

3. **Payments foundation (2 days)**
   - Razorpay integration (webhook verified)
   - Subscription model (free / premium)
   - Payment analytics (PostHog events)

**Acceptance criteria:**
- Institute admin creates batch → assigns students → students see custom logo
- Teacher sees 50-student batch overview + drill-in
- Message sent via WhatsApp to batch
- Free students see watermark, premium students see full features
- Tests: Multi-tenant RLS boundary tests, payment webhook tests

**Database additions:**
```sql
007-multi-tenancy.sql
  - public.institutes
  - public.batches
  - public.batch_students
  - public.subscriptions
  - RLS multi-tenant scope
```

---

### Phase 7 — Scale + Polish (2 weeks)

**Goal:** System ready for 100k+ users. Performance, security hardening, launch.

**Engineering milestones:**

1. **Performance optimization (5 days)**
   - Database query analysis (slow logs)
   - Read replica for analytics queries
   - Connection pooling tuning
   - CDN for static assets (Cloudflare)
   - API response compression

2. **Security hardening (5 days)**
   - OWASP Top 10 audit
   - WAF rules (Cloudflare)
   - Rate limiting tuning
   - Secrets rotation (GitHub Actions secrets)
   - Penetration testing (third-party)

3. **Monitoring + alerts (2 days)**
   - Sentry error budgets
   - Uptime monitoring (Uptime Robot)
   - Alert rules (Slack/Pagerduty)
   - SLA documentation (99.9% uptime target)
   - Runbook templates

**Acceptance criteria:**
- p99 API latency <500ms (NEET load ~50k concurrent at peak)
- Zero security vulnerabilities (pen test clean)
- Monitoring + alerting in place
- SLA documentation
- Incident response playbook

---

## Part 3: Critical Dependencies & Sequencing

```
Phase 0 ✅
  ↓
Phase 1 (Identity) — required by all downstream
  ├→ Phase 2 (Progress) — required by Phase 3+
  ├→ Phase 3 (AI Tutor)
  │  └→ Phase 4 (Notes + OCR)
  │     └→ Phase 5 (Quizzes + Roadmap)
  │        └→ Phase 6 (Admin + Payments)
  │           └→ Phase 7 (Scale + Polish)
```

**Cannot skip:** Phase 0, Phase 1, Phase 2 foundation  
**Parallelizable:** Phase 3 & 4 can overlap with Phase 2 tail

---

## Part 4: Resource Allocation (24-week roadmap)

| Phase | Duration | Team Size | Focus |
|-------|----------|-----------|-------|
| Phase 0 | 1 week | 1 (DevOps + Full-stack) | Setup, CI/CD |
| Phase 1 | 3 weeks | 2 (1 FE, 1 BE) | Auth, core models |
| Phase 2 | 2 weeks | 2 (1 FE, 1 BE) | Offline-first, progress |
| Phase 3 | 3 weeks | 2–3 (1 FE, 2 BE) | AI integration |
| Phase 4 | 2.5 weeks | 2 (1 FE, 1 BE) | Storage, OCR |
| Phase 5 | 3 weeks | 2–3 (1 FE, 2 BE) | Quizzes, roadmap |
| Phase 6 | 2 weeks | 2 (1 FE, 1 BE) | Multi-tenancy |
| Phase 7 | 2 weeks | 1–2 (DevOps, QA) | Performance, hardening |
| **Total** | **24 weeks** | **2–3 FTE (avg)** | MVP → launch-ready |

---

## Part 5: Risk Assessment

### High risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Supabase RLS incorrectly scoped | Data leak | Early RLS boundary testing, security audit |
| AI token budget exhaustion | Cost overrun | Hard caps per user, real-time accounting |
| Offline sync conflicts | Data inconsistency | Idempotency keys + timestamp-based CRDTs |
| NEET syllabus changes (post-Phase 1) | Rework scope | Syllabus as data, versioned migrations |

### Medium risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| pgvector scaling (1M+ chunks) | Performance | Partition by exam, reranking layer |
| Teacher batch size >1000 | UI/UX degradation | Virtual scrolling, aggregation, caching |
| Payment gateway uptime | Revenue risk | Fallback to manual reconciliation |

### Low risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| TypeScript version mismatch | Compile errors | strict tsconfig, CI check |
| Vercel build timeout | Deployment failure | Code splitting, lazy loading |

---

## Part 6: Success Metrics (Phase 1 launch)

- ✅ Signup flow: <2s from landing to onboarding
- ✅ Auth: <500ms login latency, <1s session validation
- ✅ Syllabus: 79 chapters load in <1s (RSC)
- ✅ Offline: checklist works with SW enabled, manual verify
- ✅ Security: RLS boundary test passes, no cross-user reads
- ✅ Tests: 80%+ code coverage (unit + E2E smoke)
- ✅ Uptime: 99.5% (Phase 1 baseline)

---

## Part 7: Documentation Artifacts

### Architecture docs (finalized)

| Document | Purpose |
|----------|---------|
| `FINAL_ARCHITECTURE.md` | Canonical technology choices (authoritative) |
| `SYSTEM_DESIGN.md` | Deep technical flows (APIs, RLS, AI agents) |
| `MONOREPO_STRUCTURE.md` | File layout + import aliases |
| `DATABASE_PLAN.md` | Schema, migrations, indexing strategy |
| `DEVOPS_PLAN.md` | Deployment, secrets, CI/CD, monitoring |
| `AI_SYSTEM_DESIGN.md` | LangGraph, routing, token budgeting |
| `API_ARCHITECTURE.md` | Route Handlers vs FastAPI, BFF pattern |
| `IMPLEMENTATION_PHASES.md` | Week-by-week milestones (technical) |
| `IMPLEMENTATION_ROADMAP.md` | Product roadmap (non-technical) |

### Team docs (to create)

- [ ] `ONBOARDING.md` — New dev setup (<1h)
- [ ] `TESTING_STRATEGY.md` — Unit + E2E + performance testing
- [ ] `SECURITY_CHECKLIST.md` — OWASP, secrets, RLS verification
- [ ] `DEPLOYMENT_RUNBOOK.md` — Prod deployment steps
- [ ] `INCIDENT_RESPONSE.md` — Escalation paths, communication

---

## Part 8: Success Handoff to Phase 1 Team

**Before kickoff, confirm:**

1. Supabase staging project created + linked
2. GitHub repo public + CI passing
3. All architects + engineers read `FINAL_ARCHITECTURE.md`
4. Database migrations `001–002` drafted (not yet run)
5. Figma designs ready for auth screens
6. API contracts (OpenAPI/GraphQL) signed off
7. E2E test plan documented (Playwright scenarios)

**Kickoff meeting agenda (30 min):**
- [ ] Architecture Q&A (10 min)
- [ ] Phase 1 scope review (10 min)
- [ ] Risk mitigation (5 min)
- [ ] First-week tasks assigned (5 min)

---

*Final document: 2026-05-14. Status: Ready for Phase 1. All Phase 0 blockers cleared.*
