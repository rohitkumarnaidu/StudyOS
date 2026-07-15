# StudyOS — Database Schema Plan

**Authority:** aligns with `STUDYOS/plan/APP_MAP.md` data layer and `ROADMAP.md` migration groups.
**Implementation:** forward-only SQL in `supabase/migrations/` (see also `docs/database/README.md` and `supabase/README.md`).

**Scope change:** NO payments/billing tables. Platform is free.

---

## 1. Migration grouping (canonical)

| File prefix | Scope | Phase |
|-------------|--------|-------|
| `001_extensions.sql` | pgvector, pg_cron, moddatetime, uuid-ossp, pgcrypto | Phase 0 ✅ |
| `002_audit_row_versioning.sql` | audit_logs, updated_at triggers, row_version | Phase 0 ✅ |
| `003_core_tenancy.sql` | institutes, profiles, institute_members, batches, batch_enrollments | Phase 0 ✅ |
| `004_syllabus.sql` | exam_profiles, subjects, chapters, topics, subtopics | Phase 0 ✅ |
| `005_progress.sql` | user_chapter_progress, subtopic_completions | Phase 0 ✅ |
| `006_auth_credentials_sessions.sql` | auth_credentials (Argon2id), auth_sessions (rotating refresh) | Phase 0 ✅ |
| `007_profiles_rls_supabase.sql` | RLS for profiles (own read/write) | Phase 0 ✅ |
| `008_on_auth_user_create_profile.sql` | Trigger: auto-create profile on Supabase Auth user creation | Phase 0 ✅ |
| `009_seed_neet_2026.sql` | NEET 2026 syllabus seed (91 chapters) | Phase 0 ✅ |
| `010_syllabus_rls.sql` | RLS: public SELECT on syllabus tables | Phase 0 ✅ |
| `011_progress_rls.sql` | RLS: own read/write on progress tables | Phase 0 ✅ |
| **`012_seed_topics_subtopics.sql`** | Seed 450+ subtopics for all 91 chapters | Phase 1 |
| **`013_streaks.sql`** | streaks table, fn_compute_streak(), nightly cron | Phase 1 |
| **`014_chat_tables.sql`** | chat_sessions, chat_messages + RLS | Phase 3 |
| **`015_notes_tables.sql`** | notes, note_versions, note_embeddings (pgvector 1536), note_mindmaps + RLS | Phase 4 |
| **`016_study_annotations.sql`** | highlights, personal_notes, bookmarks + RLS | Phase 4 |
| **`017_bulk_import.sql`** | bulk_import_jobs + RLS | Phase 4 |
| **`018_quiz_tables.sql`** | questions, quiz_sessions, quiz_responses, mistake_log + RLS | Phase 5 |
| **`019_roadmap_tables.sql`** | roadmaps, roadmap_items + RLS | Phase 6 |
| **`020_achievements.sql`** | achievements, user_achievements + RLS | Phase 6 |

**Why split:** independent review (security team reads `001`–`003` first), faster CI parallelization of lint checks.

**Removed:** `009_payments.sql` (plans, subscriptions, invoices) — platform is free.

---

## 2. Core entities (logical)

- **User profile:** 1:1 with `auth.users.id`; stores exam, dates, locale, `institute_id` nullable, `app_role`.
- **Institute:** branding, slug, seat caps (future B2B).
- **Syllabus:** versioned `exam_profiles`; soft-delete topics per NEET guide (`is_deleted`, `deleted_reason`).
- **Progress:** idempotent unique `(user_id, subtopic_id)` on completions.
- **Streaks:** daily activity tracking, computed from subtopic completions.
- **Notes:** Storage path + extracted JSON + embeddings + mind map structure.
  - `notes`: metadata (title, file_path, file_type, status, chapter_id, topic_id, page_count)
  - `note_versions`: versioned extracted content (text, structure JSON)
  - `note_embeddings`: pgvector chunks (200 tokens, 50 overlap, dimension 1536)
  - `note_mindmaps`: nodes (JSONB array), edges (JSONB array), layout_type, central_concept
- **Study annotations:** highlights (color-coded), personal notes (per page), bookmarks.
- **Chat:** session metadata + message rows; TOAST compression; offload > 100kb to Storage in v2.
- **Quiz:** separate **question bank** from **sessions**; support PYQ + AI sources; mistake log.
- **Roadmap:** append new roadmap version; mark previous inactive for auditability.
- **Achievements:** badge definitions + user unlock tracking.

---

## 3. RLS policy matrix (summary)

| Table | student | teacher | institute_admin | platform_admin |
|-------|---------|---------|-------------------|------------------|
| profiles (self) | CRUD own | R own | R own | R all (support) |
| institute_members | R own | R batch | CRUD institute | R all |
| subtopic_completions | CRUD own | R students in batch | R institute | R all |
| streaks | CRUD own | R students in batch | R institute | R all |
| notes | CRUD own | R if shared policy | R institute content | R all |
| note_embeddings | — (server only) | — | — | — |
| note_mindmaps | CRUD own | R if shared | R institute | R all |
| highlights | CRUD own | R if shared | R institute | R all |
| personal_notes | CRUD own | R if shared | R institute | R all |
| bookmarks | CRUD own | — | — | R all |
| chat_sessions | CRUD own | — | — | audit only |
| chat_messages | CRUD own (via session) | — | — | audit only |
| questions (bank) | R | R | R | CRUD |
| quiz_sessions | CRUD own | R students in batch | R institute | R all |
| quiz_responses | CRUD own | R students in batch | R institute | R all |
| mistake_log | CRUD own | R students in batch | R institute | R all |
| roadmaps | CRUD own | R students in batch | R institute | R all |
| achievements | R all | R all | R all | CRUD |
| user_achievements | CRUD own | R students in batch | R institute | R all |
| bulk_import_jobs | CRUD own | — | — | R all |

**Rule:** default **deny**; explicit policies per command (SELECT/INSERT/UPDATE/DELETE).

---

## 4. Indexing strategy

### Hot paths
- `(user_id, chapter_id)` on progress
- `(user_id, created_at desc)` on messages, quiz_sessions, notes
- `(user_id, chapter_id, topic_id)` on highlights, personal_notes
- `(user_id, date)` on streaks

### Search indexes
- **pgvector HNSW** on `note_embeddings.embedding` (created after bulk seed)
- **tsvector** on `notes.title` + `note_versions.extracted_text` for full-text search
- **Partial indexes:** `WHERE is_deleted = false` on syllabus
- **GIN** on `note_mindmaps.nodes` for mind map node search

### Vector index
- Create **after** bulk seed — not during initial insert.
- Use **HNSW** if Postgres version supports; else IVFFlat with `lists` tuned from row count.
- Always filter by `chapter_id` or `note_id` to reduce search space.

---

## 5. Functions (SQL)

Implement in DB where set-based wins:

- `fn_recompute_chapter_progress(p_user uuid, p_chapter uuid)`
- `fn_compute_streak(p_user uuid)` — computes current + longest streak from completions
- `fn_weak_chapters(p_user uuid, p_limit int)` — returns chapters with lowest completion + quiz scores
- `fn_search_notes(p_user uuid, p_query text, p_chapter_id uuid DEFAULT NULL)` — hybrid tsvector + vector search

**Why:** fewer round trips; single transactional updates from workers.

---

## 6. Realtime channels

- Enable for: `bulk_import_jobs` (progress updates), `notifications` (if table), or filtered `profiles` updates.
- **Minimize** broad subscriptions to reduce fanout cost.

---

## 7. Data retention

| Table | Retention | Action |
|-------|-----------|--------|
| chat_messages | 90 days | Anonymize summary, delete raw |
| bulk_import_jobs | 30 days | Auto-cleanup completed jobs |
| note_versions | User lifetime | Keep all versions for undo |
| quiz_responses | User lifetime | Keep for analytics |
| Deleted user | Hard-delete | Cascade all UGC; anonymize audit logs |

---

## 8. Type generation

- `supabase gen types typescript --linked > packages/database/src/types.gen.ts` in CI check (drift fails build).

---

*Operational scaling (replicas, backups): `DATABASE_PLAN.md`.*
