# StudyOS — database documentation

| Document | Contents |
|----------|----------|
| [ERD.md](./ERD.md) | Entity–relationship diagram (Mermaid) for the implemented core. |
| [MIGRATIONS_AND_SEEDS.md](./MIGRATIONS_AND_SEEDS.md) | Migration workflow, seeding, and rollout policy. |
| [INDEXING_AND_QUERIES.md](./INDEXING_AND_QUERIES.md) | Index strategy and query performance notes. |
| [`../product/skills-app/SKILL_DATABASE.md`](../product/skills-app/SKILL_DATABASE.md) | Database patterns, migrations (9 groups), RLS policies, query patterns, performance rules. |
| [`../architecture/DATABASE_SCHEMA_PLAN.md`](../architecture/DATABASE_SCHEMA_PLAN.md) | Full roadmap grouping (future modules). |
| [`../architecture/DATABASE_PLAN.md`](../architecture/DATABASE_PLAN.md) | Capacity, backups, scaling triggers. |

**Canonical SQL:** `STUDYOS/supabase/migrations/`.

**Enterprise checklist (database + auth + testing):** [docs/engineering/ENTERPRISE_READINESS.md](../engineering/ENTERPRISE_READINESS.md).

## Supabase + Next.js (web)

- Env: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` (validated in `@studyos/config`), optional `SUPABASE_SERVICE_ROLE_KEY` (server-only, never `NEXT_PUBLIC_*`).
- Code: `apps/web/src/server/supabase/*` (middleware refresh, server Route Handlers), `apps/web/src/shared/lib/supabase/browser-client.ts`, `SupabaseBrowserProvider` in `apps/web/src/app/providers.tsx`.
- RLS: migration `20260213120000_profiles_rls_supabase.sql` enables owner policies on `public.profiles` when the `auth` schema exists (hosted Supabase or `supabase start`).
- **Google sign-in:** [docs/auth/SUPABASE_GOOGLE.md](../auth/SUPABASE_GOOGLE.md) (Supabase provider + redirect URLs + `public.profiles` bootstrap).
