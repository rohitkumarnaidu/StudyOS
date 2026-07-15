# StudyOS — Database Plan (Governance, Scale, Operations)

**Companion:** `DATABASE_SCHEMA_PLAN.md` (tables, migrations, RLS detail).
**This document:** lifecycle, capacity, **scaling triggers**, backups, and **operational policies**.

---

## 1. Single primary database (Phase 1–6)

**Decision:** one **Supabase PostgreSQL** cluster as **system of record** for transactional data.

**Why:** minimizes distributed consistency problems while the product is still discovering write patterns.

---

## 2. Connection strategy

- **Server runtimes:** Supabase **pooler** (PgBouncer) connection string; short-lived connections.
- **Serverless bursts:** cap concurrent DB connections per Route Handler via **singleton** client pattern.
- **Workers:** smaller connection pools per process; horizontal scale = more processes → watch DB `max_connections`.

**Action item:** monitor `pg_stat_activity`; add **PgBouncer transaction mode** tuning if queuing appears.

---

## 3. Migration schedule (canonical order)

| Migration | Tables | Phase |
|-----------|--------|-------|
| `001_extensions.sql` | pgcrypto, pgvector, moddatetime, uuid-ossp | Phase 0 ✅ |
| `002_audit_row_versioning.sql` | audit_logs, updated_at triggers | Phase 0 ✅ |
| `003_core_tenancy.sql` | institutes, profiles, institute_members, batches | Phase 0 ✅ |
| `004_syllabus.sql` | exam_profiles, subjects, chapters, topics, subtopics | Phase 0 ✅ |
| `005_progress.sql` | user_chapter_progress, subtopic_completions | Phase 0 ✅ |
| `006_auth_credentials_sessions.sql` | auth_credentials, auth_sessions | Phase 0 ✅ |
| `007_profiles_rls_supabase.sql` | RLS for profiles | Phase 0 ✅ |
| `008_on_auth_user_create_profile.sql` | Trigger: auto-create profile | Phase 0 ✅ |
| `009_seed_neet_2026.sql` | NEET syllabus seed (91 chapters) | Phase 0 ✅ |
| `010_syllabus_rls.sql` | RLS for syllabus tables | Phase 0 ✅ |
| `011_progress_rls.sql` | RLS for progress tables | Phase 0 ✅ |
| **`012_seed_topics_subtopics.sql`** | Seed 450+ subtopics for all chapters | Phase 1 |
| **`013_streaks.sql`** | streaks table, fn_compute_streak() | Phase 1 |
| **`014_chat_tables.sql`** | chat_sessions, chat_messages + RLS | Phase 3 |
| **`015_notes_tables.sql`** | notes, note_versions, note_embeddings (pgvector), note_mindmaps + RLS | Phase 4 |
| **`016_study_annotations.sql`** | highlights, personal_notes, bookmarks + RLS | Phase 4 |
| **`017_bulk_import.sql`** | bulk_import_jobs + RLS | Phase 4 |
| **`018_quiz_tables.sql`** | questions, quiz_sessions, quiz_responses, mistake_log + RLS | Phase 5 |
| **`019_roadmap_tables.sql`** | roadmaps, roadmap_items + RLS | Phase 6 |
| **`020_achievements.sql`** | achievements, user_achievements + RLS | Phase 6 |

**Total tables when complete:** ~35
**Total RLS policies when complete:** ~50+

---

## 4. Write volume management

| Hot write | Mitigation |
|-----------|------------|
| Subtopic toggles (high frequency) | Batch sync from client; server upserts idempotent |
| PDF processing (burst) | Async queue; one file at a time per user; progress table |
| AI message logs | Append-only; TOAST compression; consider offload > 100kb to Storage in v2 |
| Highlights/personal notes | Client-side Dexie first, sync to server on reconnect |
| Quiz responses | Batch submit per question or at end of quiz |

---

## 5. Read scaling triggers

| Signal | Response |
|--------|----------|
| sustained CPU > 70% on primary | add **read replica** (Supabase) for reporting queries |
| heavy analytics queries crush OLTP | move aggregates to **materialized views** refreshed by cron |
| cross-region latency complaints | evaluate **read replica** closer to users; not full multi-primary |
| search latency > 500ms across 400+ notes | tune pgvector HNSW, add tsvector full-text index |

---

## 6. Vector index lifecycle (pgvector)

### Embedding strategy

| Content | Model | Dimension | Chunk size |
|---------|-------|-----------|------------|
| NCERT chunks | text-embedding-3-small | 1536 | 200 tokens, 50 overlap |
| Note text chunks | text-embedding-3-small | 1536 | 200 tokens, 50 overlap |
| Mind map node labels | text-embedding-3-small | 1536 | per node (short) |

### Index management

- **Embedding model locked** per environment; dimension fixed in migrations.
- **Create vector index AFTER bulk seed** — not during initial insert.
- Use **HNSW** if Postgres version supports; else IVFFlat with `lists` tuned from row count.
- **Re-embed** on model change via worker job; **blue/green** column or table swap.
- **Vacuum** schedule after bulk index build.
- **Filter by chapter_id** on all vector queries to reduce search space.

---

## 7. Storage strategy (Supabase Storage)

### Bucket layout

```
notes/
  {user_id}/
    {note_id}/
      original.pdf          # Original uploaded file
      extracted.json        # AI-extracted text + structure
      mindmap.json          # Mind map nodes/edges (if applicable)
      thumb.jpg             # Thumbnail for library view
      summary.pdf           # Generated summary (on download)
```

### Access rules

- **Buckets:** `notes` (private, user-scoped)
- **RLS on Storage:** user can only access their own `notes/{user_id}/` path
- **Signed URLs:** 1-hour expiry for PDF viewing
- **Size limits:** 50MB per file (configurable)
- **Allowed types:** `.pdf` only (validated server-side with magic bytes)

---

## 8. Backup & recovery

- Enable **PITR** on production.
- Monthly **restore test** to staging + run smoke SQL.
- Export critical **syllabus seed** to versioned SQL in repo (already done).
- **Note embeddings:** can be regenerated from source PDFs if lost (expensive but possible).

---

## 9. Data governance

### Classification

| Level | Data | Handling |
|-------|------|----------|
| **Public** | syllabus snapshots (versioned) | CDN-cacheable, no auth |
| **PII** | name, phone, email | Encrypted at rest, DPDP consent |
| **UGC** | notes, chats, highlights, personal notes | Highest sensitivity, user-owned, exportable |
| **AI artifacts** | embeddings, structured JSON, mind map trees | Derived from UGC, same sensitivity |

### Retention

| Table | Retention | Action |
|-------|-----------|--------|
| chat_messages | 90 days | Anonymize summary, delete raw |
| events/analytics | 90 days hot | Archive to warehouse if needed |
| notes | User lifetime | Delete on account deletion |
| highlights/personal_notes | User lifetime | Delete on account deletion |
| quiz_responses | User lifetime | Keep for analytics |
| bulk_import_jobs | 30 days | Auto-cleanup completed jobs |

### User data export/delete

- **Export:** ZIP of all notes (PDFs + structured JSON + highlights + bookmarks) + chat history + quiz history
- **Delete:** Hard delete user + cascade all UGC; anonymize audit logs

---

## 10. Multi-tenant operational rules (future)

- **No shared test accounts** across institutes in prod.
- **Support queries** use read-only replica role where possible.
- **Break-glass** access logged with ticket id.

---

## 11. Schema change process

1. PR with migration + RLS tests + rollback/compensating plan.
2. Staging apply + soak **24h minimum** for risky changes.
3. Production apply in maintenance window only if lock-heavy (otherwise online).
4. **Breaking changes:** expand → migrate → contract pattern.

---

## 12. Future splits (only if needed)

- **Analytics warehouse:** BigQuery/Snowflake fed by CDC or nightly export—when event volume makes Postgres painful.
- **Separate vector DB:** only if pgvector tuning fails cost/latency SLOs (unlikely short term).
- **Search engine:** Meilisearch/Typesense if hybrid search quality degrades at scale.

---

*Schema details: `DATABASE_SCHEMA_PLAN.md`.*
