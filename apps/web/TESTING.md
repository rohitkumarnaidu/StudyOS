# Web app — testing layout

This app uses **Vitest** for unit/component tests and **Playwright** for E2E. Guidelines for the whole monorepo live in [docs/engineering/TESTING.md](../../docs/engineering/TESTING.md).

## Layout

| Path | Purpose |
|------|---------|
| `e2e/*.spec.ts` | Playwright browser tests (`pnpm run test:e2e`). |
| `src/**/*.spec.ts` / `*.spec.tsx` | Vitest tests colocated with source (`pnpm run test`). |
| `src/test/setup.ts` | `jest-dom` matchers for Vitest. |
| `vitest.config.ts` | `jsdom`, path alias `@/`, excludes `e2e/`. |
| `playwright.config.ts` | Chromium project, `webServer` for local vs CI (`next start` when `CI=true`). |

## Commands

```bash
pnpm run test          # Vitest (from apps/web)
pnpm run test:watch    # Vitest watch mode
pnpm run test:e2e      # Playwright (build first in CI)
```

## Conventions

- Prefer **Testing Library** queries (`getByRole`, etc.) over implementation details.
- Keep **E2E** to critical journeys; use Vitest for component and unit logic.
- Optional future: **MSW** under `src/testing/mocks/` for fetch-heavy components (not required for current suite).
