# StudyOS — Implementation Roadmap (MVP → Launch)

**Quick reference:** See [docs/STUDYOS_COMPLETE_SUMMARY.md](../STUDYOS_COMPLETE_SUMMARY.md) for master overview.

**Scope:** Free platform — NO payments, NO subscriptions. Full PDF + Mind Map pipeline (400+ files), interactive study mode, AI tutor, quizzes, analytics.

**Use:** sequencing work; each step should become **trackable issues** with acceptance tests.

---

## Guiding rules

1. **Ship the core study loop** before secondary intelligence.
2. **RLS before scale** — no feature ships without policy tests.
3. **AI platform path** before BYOK polish (BYOK can ship as beta parallel).
4. **Measure everything** — PostHog events land in Week 1 scaffolding, not "later".
5. **PDF pipeline is the moat** — 400+ notes + mind maps must feel like Physics Wallah quality.

---

## Wave A — Product foundation (Weeks 1–2)

**Scope:** Finish Phase 1 — Auth + Syllabus + Progress + Streaks

| Step | Outcome | Depends on |
|------|---------|------------|
| A1 | Seed topics/subtopics for all 91 chapters (450+ subtopics) | existing migrations |
| A2 | Wire progress UI — enable checkboxes, optimistic updates | A1 |
| A3 | Streak system — table, computation, dashboard badge | A2 |
| A4 | Dashboard enhancement — progress rings, study stats, quick actions | A2, A3 |
| A5 | Chapter detail page — topics/subtopics tree with progress | A1 |
| A6 | RLS tests for all progress tables | A2 |
| A7 | PostHog + Sentry wired; baseline event catalog | — |

**Exit:** a student can sign in, open any chapter, toggle subtopics, see progress rings + streak, refresh without data loss.

---

## Wave B — Offline + PWA + Settings (Weeks 3–4)

| Step | Outcome |
|------|---------|
| B1 | Serwist PWA setup — manifest, service worker, install prompt |
| B2 | Dexie offline DB — syllabus cache, progress outbox, draft notes |
| B3 | Sync engine — queue mutations offline, replay on reconnect, conflict resolution |
| B4 | Online/offline banner + sync indicator |
| B5 | Settings page — profile, notifications, appearance, data export |
| B6 | Offline-first syllabus — loads from Dexie cache when network down |

**Exit:** PWA installable on mobile; toggle subtopics offline → reconnect → syncs; settings page functional.

---

## Wave C — AI Tutor Chat (Weeks 5–7)

| Step | Outcome |
|------|---------|
| C1 | Chat UI — message list, input, streaming display, markdown + KaTeX rendering |
| C2 | BFF SSE streaming route — proxy to FastAPI `/v1/ai/chat/stream` |
| C3 | Chat history persistence — `chat_sessions`, `chat_messages` tables + RLS |
| C4 | Chapter context injection — AI knows which chapter user is studying |
| C5 | Chapter detail page with embedded chat panel |
| C6 | Rate limiting per user on AI endpoints |

**Exit:** open chapter → type question → stream response in <5s; chat history persists; chapter context injected.

---

## Wave D — PDF + Mind Map Notes Pipeline (Weeks 8–12) ⭐

**Scope:** Upload 400+ PDFs → AI structures → searchable + interactive viewer like Physics Wallah

| Step | Outcome |
|------|---------|
| D1 | PDF upload — drag-drop modal, upload queue, Storage integration |
| D2 | PDF processing pipeline — text extraction (pdfplumber), vision OCR for scanned, mind map parser for digital mind maps |
| D3 | AI structuring — tag chapter/topic, extract key concepts, create hierarchical summary |
| D4 | Embedding pipeline — chunk text, generate embeddings, store in pgvector |
| D5 | Bulk import system — accept multiple PDFs/ZIP, progress tracking, realtime status |
| D6 | Notes library UI — grid/list view, filters (chapter, type, date), note cards |
| D7 | PDF viewer — react-pdf based, page thumbnails, zoom, search, smooth transitions (PW-quality) |
| D8 | Mind map viewer — interactive canvas, zoomable/pannable, click to expand/collapse, color-coded branches |
| D9 | Structured notes view — AI-extracted hierarchy, formula cards, definition cards |
| D10 | **Study mode** — full-screen distraction-free, highlights (color-coded), personal notes on pages, bookmarks |
| D11 | **Global search** — Cmd+K across all 400+ PDFs, hybrid keyword+vector, instant results with snippets |
| D12 | **Download system** — original PDF, summary PDF, mind map PNG/SVG, highlights export, bulk ZIP, chapter compilation |
| D13 | AI chat references uploaded notes — RAG over note embeddings |

**Exit:** upload PDF → structured in <60s; mind map → interactive viewer; bulk import 400+ files; study mode with highlights; global search across all notes; download in multiple formats.

---

## Wave E — Quiz + Adaptive Learning (Weeks 13–16)

| Step | Outcome |
|------|---------|
| E1 | Quiz tables — `questions`, `quiz_sessions`, `quiz_responses`, `mistake_log` + RLS |
| E2 | Quiz generation — AI-powered from syllabus + notes, difficulty levels |
| E3 | Quiz UI — setup, player with timer, results with explanations |
| E4 | Mistake log — review past mistakes, track improvement, mark reviewed |
| E5 | Mock test mode — 180Q / 3hr with OMR navigation grid |
| E6 | Weak area detector — analyze quiz results + progress, visualize on dashboard |

**Exit:** select chapter → generate quiz → answer → see results; mock test with OMR; mistake log; weak areas on dashboard.

---

## Wave F — Analytics + Roadmap + Motivation (Weeks 17–19)

| Step | Outcome |
|------|---------|
| F1 | Analytics dashboard — progress chart, subject breakdown, study heatmap, quiz trends |
| F2 | Study roadmap — AI generates personalized plan based on exam date, progress, weak areas |
| F3 | Roadmap UI — visual timeline with daily/weekly plans, interactive |
| F4 | Motivation system — achievement badges, streak calendar with fire animation, daily quotes |
| F5 | Streak history — calendar view, milestones |

**Exit:** full analytics dashboard; AI generates study roadmap; achievement badges; streak calendar.

---

## Wave G — Scale + Polish + Launch (Weeks 20–22)

| Step | Outcome |
|------|---------|
| G1 | Performance — bundle splitting, DB indexes, Redis caching for syllabus/analytics, CDN for public assets |
| G2 | Security hardening — CSP headers, rate limit tuning, input validation audit, RLS audit, file upload security |
| G3 | Observability — Sentry error tracking, PostHog event catalog, API observability hooks |
| G4 | Mobile responsiveness audit — all screens tested on mobile |
| G5 | Accessibility — WCAG 2.1 AA core flows, keyboard navigation |
| G6 | Polish — loading states, error states, empty states, Framer Motion animations, dark mode |
| G7 | i18n infrastructure — English first, Hindi/Tamil/Telugu ready |
| G8 | Production deployment — Vercel + Supabase prod, env vars, secrets manager |

**Exit:** LCP < 2.5s, API p95 < 200ms; all security headers; mobile responsive; accessibility passed; production ready.

---

## Cross-cutting checklist (apply every wave)

- [ ] RLS tests updated
- [ ] Security headers + CSP reviewed
- [ ] Runbook updated (`DEVOPS_PLAN.md`)
- [ ] Feature flags for risky changes
- [ ] Accessibility spot-check (critical paths)
- [ ] PostHog events added for new flows

---

## Dependency graph

```
Wave A (Auth + Progress)
    ↓
Wave B (Offline + PWA)
    ↓
Wave C (AI Chat)
    ↓
Wave D (PDF Pipeline) ← biggest, most complex
    ↓
Wave E (Quizzes)
    ↓
Wave F (Analytics + Roadmap)
    ↓
Wave G (Scale + Launch)
```

**Parallelizable:** Wave C (AI Chat) and Wave D (PDF Pipeline) can overlap at the tail. Wave E (Quizzes) can start once Wave D's note embeddings are wired.

---

## Mapping to implementation phases

| Wave | Phase | Duration |
|------|-------|----------|
| A | Phase 1 | 1-2 weeks |
| B | Phase 2 | 1-2 weeks |
| C | Phase 3 | 2-3 weeks |
| D | Phase 4 | 3-4 weeks |
| E | Phase 5 | 3-4 weeks |
| F | Phase 6 | 2-3 weeks |
| G | Phase 7 | 2-3 weeks |
| **TOTAL** | | **14-22 weeks** |

---

*Technical ordering detail: `IMPLEMENTATION_PHASES.md`. Product stack ranks: `FEATURE_PRIORITY.md`.*
