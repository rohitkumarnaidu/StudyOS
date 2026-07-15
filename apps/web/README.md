# @studyos/web

Next.js App Router app for StudyOS (marketing, auth, dashboard).

## Commands

```bash
pnpm dev              # Turbopack dev server
pnpm run build        # Production build (webpack)
pnpm run test         # Vitest (unit + component)
pnpm run test:e2e     # Playwright E2E
```

## Docs

- **Web testing layout:** [TESTING.md](./TESTING.md)
- **Monorepo testing / CI:** [docs/engineering/TESTING.md](../../docs/engineering/TESTING.md)
- **Enterprise checklist (DB + auth + tests):** [docs/engineering/ENTERPRISE_READINESS.md](../../docs/engineering/ENTERPRISE_READINESS.md)
- **Auth & security:** [docs/security/AUTHENTICATION.md](../../docs/security/AUTHENTICATION.md)
- **Env templates:** `apps/web/.env.example`, `apps/web/.env.production.example`

Monorepo root: run `pnpm install` from `STUDYOS/`.
