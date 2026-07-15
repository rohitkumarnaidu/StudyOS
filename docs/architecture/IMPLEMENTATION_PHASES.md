# StudyOS — Implementation Phases (Technical Milestones)

**Purpose:** order-of-operations for engineering to go from **empty repo** to **launch-ready**, aligned with `FINAL_ARCHITECTURE.md`.
**Scope:** Free platform — NO payments, NO subscriptions. Full PDF + Mind Map pipeline (400+ files).
**Not:** sprint planning (see `DEVELOPMENT_PHASES.md` and `IMPLEMENTATION_ROADMAP.md`).

---

## Phase 0 — Foundation (Week 0) ✅ COMPLETE

**Exit criteria**

- Monorepo boots: `pnpm install`, `turbo run lint`, `turbo run build` (stub apps OK).
- Supabase **staging** project; `supabase link`; **CI** runs migrations against ephemeral DB or dry-run.
- Vercel project connected; **preview** deploys per PR.
- Sentry + PostHog **DSN wired** (no PII in client identify).

**Deliverables**

- Repo skeleton per `MONOREPO_STRUCTURE.md`
- `.env.example` documented in `DEVOPS_PLAN.md`
- **RLS template** smoke test pattern established
- 11 database migrations written (extensions, tenancy, syllabus, progress, auth, RLS, seed)
- CI/CD pipeline (JS + Python + E2E)

---

## Phase 1 — Identity + Syllabus + Progress (Week 1–2)

**Exit criteria**

- Sign up / sign in / sign out; profile row with exam + dates.
- **All 450+ subtopics seeded** for 91 chapters.
- Subtopic toggle writes through RLS; dashboard rings reflect aggregates.
- Streak computation idempotent (server authoritative).
- Chapter detail page with topics/subtopics tree.

**Deliverables**

- Migration `012_seed_topics_subtopics.sql`
- Migration `013_streaks.sql`
- `features/progress/api.ts` — toggleSubtopic(), getChapterProgress()
- `features/progress/hooks/use-progress.ts` — TanStack Query with optimistic updates
- `features/progress/components/progress-ring.tsx`
- `features/progress/components/streak-badge.tsx`
- `features/syllabus/components/chapter-list.tsx` — enable checkboxes, wire to progress
- `features/dashboard/components/study-stats.tsx`
- `features/dashboard/components/quick-actions.tsx`
- Playwright smoke: complete subtopic → refresh → still complete

---

## Phase 2 — Offline + PWA + Settings (Week 3–4)

**Exit criteria**

- PWA installable on mobile.
- Offline: toggle subtopics → banner shows → reconnect → syncs.
- Settings page: profile, notifications, appearance, data export.
- Syllabus loads from Dexie cache when offline.

**Deliverables**

- `public/manifest.json` + app icons
- `src/app/sw.ts` — Serwist service worker
- `features/offline/dexie.ts` — Dexie DB schema
- `features/offline/sync-queue.ts` — Outbox pattern
- `features/offline/components/sync-indicator.tsx`
- `app/(app)/settings/page.tsx` + settings feature components
- `features/syllabus/hooks/use-syllabus-cache.ts`

---

## Phase 3 — Platform AI Tutor (Week 5–7)

**Exit criteria**

- Streaming chat with **chapter context**; messages persisted.
- LangSmith traces on all server-side runs.
- Token budget + rate limit enforced.
- Chapter detail page with embedded chat panel.

**Deliverables**

- Migration `014_chat_tables.sql`
- `features/chat/components/chat-window.tsx`
- `features/chat/components/message-bubble.tsx` (markdown + KaTeX)
- `features/chat/components/chat-input.tsx`
- `features/chat/components/chat-sidebar.tsx`
- `features/chat/hooks/use-chat.ts` — SSE streaming hook
- `features/chat/api.ts`
- `app/api/ai/chat/stream/route.ts` — SSE proxy
- `app/(app)/chat/page.tsx`
- `app/(app)/syllabus/[chapterId]/page.tsx` — chapter detail with embedded chat
- `features/syllabus/components/chapter-detail.tsx`

---

## Phase 4 — PDF + Mind Map Notes Pipeline (Week 8–12)

**Exit criteria**

- Upload PDF → processing → structured notes visible in <60s.
- Mind map PDF → interactive viewer with nodes/edges.
- Bulk import 400+ PDFs → progress tracking → all processed.
- Study mode: full-screen, highlights, personal notes, bookmarks.
- Global search: Cmd+K across all 400+ PDFs, instant results.
- Download: original PDF, summary PDF, mind map image, highlights, bulk ZIP.
- PDF viewer: smooth, zoomable, searchable (PW-quality).
- AI chat can reference uploaded notes.

**Deliverables**

### Database
- Migration `015_notes_tables.sql` — notes, note_versions, note_embeddings, note_mindmaps
- Migration `016_study_annotations.sql` — highlights, personal_notes, bookmarks
- Migration `017_bulk_import.sql` — bulk_import_jobs

### Backend
- `services/pdf_processor.py` — Main orchestrator (detect type → extract → structure → embed)
- `services/pdf_text_extractor.py` — Text PDF extraction (pdfplumber)
- `services/pdf_vision_ocr.py` — Vision model OCR for scanned PDFs
- `services/mindmap_parser.py` — Vision model mind map parsing → JSON tree
- `services/note_structurer.py` — AI structuring: tag chapter, extract concepts, summary
- `services/note_embedder.py` — Chunk + embed + store in pgvector
- `services/bulk_import_service.py` — Queue-based bulk processing
- `services/note_search.py` — Hybrid search (tsvector + pgvector)
- `services/note_export.py` — Export: summary PDF, mind map image, highlights, bulk ZIP
- `api/v1/routes/notes.py` — Note CRUD
- `api/v1/routes/bulk_import.py` — Bulk import endpoints
- `api/v1/routes/note_search.py` — Search endpoint
- `api/v1/routes/note_export.py` — Export endpoints

### Frontend
- `features/notes/components/upload-dialog.tsx`
- `features/notes/components/upload-queue.tsx`
- `features/notes/components/notes-library.tsx`
- `features/notes/components/note-card.tsx`
- `features/notes/components/note-viewer.tsx` (tabs: PDF, Structured, Mind Map, Search)
- `features/notes/components/pdf-viewer.tsx` (react-pdf, thumbnails, zoom, search)
- `features/notes/components/mindmap-viewer.tsx` (@xyflow/react, zoomable, pannable)
- `features/notes/components/structured-notes.tsx` (hierarchy, formula cards)
- `features/notes/components/study-mode.tsx` (full-screen, highlights, personal notes, bookmarks)
- `features/notes/components/highlights-manager.tsx`
- `features/notes/components/personal-notes.tsx`
- `features/notes/components/bookmarks.tsx`
- `features/notes/components/global-search.tsx` (Cmd+K, hybrid search, snippets)
- `features/notes/components/download-dialog.tsx`
- `app/(app)/notes/page.tsx`
- `app/(app)/notes/[noteId]/page.tsx`

---

## Phase 5 — Quizzes + Adaptive Learning (Week 13–16)

**Exit criteria**

- Select chapter → generate quiz → answer → see results with explanations.
- Timed mode with countdown.
- Mock test: 180Q / 3hr with OMR navigation.
- Mistake log: review past mistakes, track improvement.
- Weak area detection on dashboard.

**Deliverables**

- Migration `018_quiz_tables.sql` — questions, quiz_sessions, quiz_responses, mistake_log
- `services/quiz_service.py` — Quiz generation + scoring
- `services/quiz_generator.py` — AI-powered question generation
- `services/weak_area_detector.py` — Analyze quiz results + progress
- `api/v1/routes/quizzes.py` — Quiz endpoints
- `features/quiz/components/quiz-setup.tsx`
- `features/quiz/components/quiz-player.tsx`
- `features/quiz/components/quiz-results.tsx`
- `features/quiz/components/mistake-log.tsx`
- `features/quiz/components/mock-test.tsx`
- `features/quiz/components/omr-sheet.tsx`
- `features/quiz/components/timer-bar.tsx`
- `features/quiz/hooks/use-quiz-session.ts`
- `app/(app)/quiz/page.tsx`
- `app/(app)/quiz/session/[id]/page.tsx`

---

## Phase 6 — Analytics + Roadmap + Motivation (Week 17–19)

**Exit criteria**

- Analytics dashboard with charts (progress, subjects, quiz trends, heatmap).
- AI generates personalized study roadmap.
- Roadmap updates based on progress.
- Achievement badges for milestones.
- Streak calendar with visual fire animation.

**Deliverables**

- Migration `019_roadmap_tables.sql` — roadmaps, roadmap_items
- Migration `020_achievements.sql` — achievements, user_achievements
- `services/analytics_service.py` — Aggregate analytics queries
- `services/roadmap_generator.py` — AI generates personalized study plan
- `api/v1/routes/analytics.py` — Analytics endpoints
- `api/v1/routes/roadmap.py` — Roadmap endpoints
- `features/analytics/components/analytics-dashboard.tsx`
- `features/analytics/components/progress-chart.tsx`
- `features/analytics/components/subject-breakdown.tsx`
- `features/analytics/components/study-heatmap.tsx`
- `features/analytics/components/quiz-analytics.tsx`
- `features/analytics/components/streak-calendar.tsx`
- `features/analytics/components/weak-areas.tsx`
- `features/roadmap/components/roadmap-timeline.tsx`
- `features/roadmap/components/roadmap-card.tsx`
- `features/motivation/components/achievement-badges.tsx`
- `features/motivation/components/streak-fire.tsx`
- `app/(app)/analytics/page.tsx`
- `app/(app)/roadmap/page.tsx`

---

## Phase 7 — Scale + Polish + Launch (Week 20–22)

**Exit criteria**

- LCP < 2.5s, API p95 < 200ms.
- All security headers in place.
- RLS tests pass for all tables.
- Sentry + PostHog wired.
- Mobile responsive on all screens.
- Accessibility audit passed.
- Production deployment ready.

**Deliverables**

- Bundle splitting optimization
- Database indexes for hot queries
- Redis caching for syllabus + analytics
- CDN caching for public syllabus JSON
- CSP headers in Next.js config
- Rate limiting review + tuning
- Input validation audit (all Zod boundaries)
- RLS policy audit (test all tables)
- File upload security (magic-byte validation, size limits)
- Sentry integration (`lib/sentry.ts`)
- PostHog integration (`lib/posthog.ts`)
- Event catalog: track all key user actions
- Mobile responsiveness audit
- Accessibility (WCAG 2.1 AA)
- Framer Motion animations
- Dark mode polish
- i18n infrastructure (English first, Hindi/Tamil later)

---

## Dependency graph (simplified)

```
Phase0 ✅ → Phase1 → Phase2 → Phase3 → Phase4 → Phase5 → Phase6 → Phase7
```

**Parallelizable:** Phase 3 (AI Chat) and Phase 4 (PDF Pipeline) can overlap at the tail. Phase 5 (Quizzes) can start once Phase 4's note embeddings are wired.

---

*Product prioritization of features within phases: `FEATURE_PRIORITY.md`.*
