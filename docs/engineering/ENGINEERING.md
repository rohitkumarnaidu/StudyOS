# Engineering standards — StudyOS

## Documentation

1. **ADRs** (`docs/adr/` or `docs/ADR-*.md`) for irreversible architecture choices.  
2. **Runbooks** for on-call: link from `DEVOPS_PLAN.md` when created.  
3. **README per app/package** when setup or env vars are non-obvious.

## Code review checklist (short)

- Correctness, types, and error paths.  
- **Security:** secrets, authz, user input, file uploads.  
- **Observability:** structured logs, trace IDs, metrics hooks where relevant.  
- **Performance:** N+1 queries, unbounded lists, bundle impact.

## Commits

- Conventional Commits encouraged (`feat:`, `fix:`, `chore:`).  
- PRs should be small and reversible; use feature flags for risky behavior.

## Testing pyramid

- **Unit:** domain + pure helpers (Vitest / Pytest).  
- **Integration:** API contracts (httpx ASGI / MSW in TS as you grow).  
- **E2E:** Playwright for critical user journeys (`pnpm --filter @studyos/web test:e2e`).

Full layout, markers, CI, and commands: **[TESTING.md](./TESTING.md)**.  
Production gate and honest stack audit: **[PRODUCTION_READINESS.md](./PRODUCTION_READINESS.md)**.  
**Enterprise checklist** (database + auth + testing vs requirements): **[ENTERPRISE_READINESS.md](./ENTERPRISE_READINESS.md)**.

## Formatting

- **TypeScript:** Prettier + Tailwind class sorting (`prettier-plugin-tailwindcss`).  
- **Python:** Ruff format + Ruff lint (`apps/api`).

## Dependency hygiene

- Prefer `pnpm` / `uv` lockfiles committed.  
- Patch/minor updates via automation where CI is green.
