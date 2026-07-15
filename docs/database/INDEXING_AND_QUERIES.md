# Indexing and query performance

## Design rules (implemented)

1. **Partial unique indexes** on business keys **where `deleted_at IS NULL`** — keeps soft-deleted history without blocking re-create.
2. **Composite indexes** matching common filters: `(parent_id, sort_order)` on syllabus tables; `(profile_id, completed_at DESC)` on completions.
3. **Narrow covering** — add INCLUDE columns later when `EXPLAIN (ANALYZE, BUFFERS)` shows heap fetches dominate.

## Hot paths to watch

| Query pattern | Supporting index |
|---------------|------------------|
| Dashboard: “my chapters in progress” | `user_chapter_progress (profile_id, last_studied_at DESC) WHERE deleted_at IS NULL` |
| Syllabus browser: children of a node | `(subject_id|chapter_id|topic_id, sort_order)` partials |
| Completion idempotency | partial unique `(profile_id, subtopic_id)` |

## When to add more

- **BRIN** on append-only tables (`audit_log`, future `events`) if time-range scans dominate and table is huge.
- **Materialized views** for teacher dashboards once OLTP CPU rises (refresh via `pg_cron` / worker).
- **pgvector** (HNSW/IVFFlat) only **after** bulk embedding load; see `DATABASE_SCHEMA_PLAN.md` §4 / `011` group.

## Optimistic locking

Clients sending updates should include the last known `row_version`; server checks `WHERE id = $1 AND row_version = $2` to detect stale writes.
