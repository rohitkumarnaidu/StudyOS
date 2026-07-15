# StudyOS database (PostgreSQL / Supabase)

This folder holds **forward-only SQL migrations** and a **dev seed** aligned with:

- `docs/architecture/DATABASE_SCHEMA_PLAN.md` (logical grouping)
- `docs/architecture/DATABASE_PLAN.md` (operations & scale)

## Layout

| Path | Purpose |
|------|---------|
| `migrations/*.sql` | Ordered, idempotent-friendly DDL (extensions → helpers → domain). |
| `seed.sql` | Small deterministic graph for local dev (no secrets). |
| `config.toml` | Supabase CLI local defaults (edit `project_id` after `supabase link`). |

## Commands (Supabase CLI)

From repo root `STUDYOS/`:

```bash
# Local stack + apply migrations + seed
supabase start
supabase db reset

# Linked project (staging/prod) — requires manual approval in CI/CD
supabase db push
```

## Commands (plain `psql` + Docker Compose)

If you use `docker/docker-compose.yml` **postgres** service (no Supabase auth schema):

```bash
docker compose -f docker/docker-compose.yml --profile local-deps up -d postgres
# apply each migration in timestamp order
psql "postgresql://studyos:studyos@localhost:5432/studyos" -f supabase/migrations/20250613120000_extensions.sql
# ...remaining files in order
psql "postgresql://studyos:studyos@localhost:5432/studyos" -f supabase/seed.sql
```

> **Note:** `profiles` → `auth.users` FK is applied **only** when the `auth` schema exists (Supabase). Plain Postgres skips that block.

## Type generation (optional)

```bash
supabase gen types typescript --linked > packages/database/src/types.gen.ts
```

(Create `packages/database` when you wire this into CI.)
