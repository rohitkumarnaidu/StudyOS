# Migrations and seeds

## Principles

1. **Forward-only** migrations — no destructive rewrite of history; use expand → migrate → contract for breaking changes.
2. **One concern per file** — extensions/helpers, tenancy, syllabus, progress (extend with notes/quiz/chat per `DATABASE_SCHEMA_PLAN.md`).
3. **Idempotent guards** — `IF NOT EXISTS`, `DROP TRIGGER IF EXISTS`, and `DO $$ … EXCEPTION duplicate_object` for enums.
4. **Soft delete first** — prefer `deleted_at` + partial indexes over hard `DELETE` for user-visible entities.

## Applying migrations

### Supabase (recommended)

```bash
supabase db reset   # local: migrations + seed.sql
supabase db push     # linked remote (use protected GitHub Environment)
```

### Plain Postgres

Apply files under `supabase/migrations/` in **lexicographic timestamp order**, then `supabase/seed.sql`.

## Seeding strategy

| Layer | Strategy |
|-------|----------|
| **Reference data** | Versioned SQL in `supabase/seed.sql` (small, deterministic UUIDs). |
| **Large syllabus** | Separate `sql/` or `supabase/seeds/` bulk files loaded by job; keep migrations lean. |
| **PII / secrets** | Never in git; use vault + runtime import pipelines. |

## Session context for audit rows

Application code can set per-transaction GUCs (optional):

```sql
SELECT set_config('studyos.actor_id', '<uuid>', TRUE);
SELECT set_config('studyos.request_id', '<correlation-id>', TRUE);
-- then INSERT/UPDATE on audited tables
```

`studyos_audit_row` reads these when present.

## CI (suggested)

- Add a job that starts Postgres 15+ and runs all `supabase/migrations/*.sql` in order (fail on first error).
- Optionally run `supabase db lint` when the project is linked.
