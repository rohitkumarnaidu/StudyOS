# StudyOS — monorepo architecture

**Quick reference:** See [docs/STUDYOS_COMPLETE_SUMMARY.md](docs/STUDYOS_COMPLETE_SUMMARY.md) for master architecture overview + 24-week implementation roadmap.

This directory is the **pnpm + Turborepo** workspace root. The layout follows **clean architecture boundaries**: versioned HTTP APIs, shared libraries with explicit contracts, and **feature slices** in the Next.js app.

---

## 1. Directory map (current)

| Path | Role |
|------|------|
| `apps/web` | **Next.js App Router**: route groups `(marketing)`, `(auth)`, `(app)`; `src/features/*` vertical slices; `src/shared/*` cross-cutting UI, config, API client, hooks. |
| `apps/api` | **FastAPI**: `core/` (config, errors, logging, rate limit), `api/v1/` (HTTP routers), `deps/` (auth/RBAC), `middleware/`. |
| `packages/config` | **Zod** schemas for **browser-safe** env (`NEXT_PUBLIC_*`) — `@studyos/config`. |
| `packages/shared` | **Pure** shared TS: constants, helpers, `utils/*` — `@studyos/shared`. |
| `packages/eslint-config`, `packages/typescript-config` | Workspace-wide lint and TS bases. |

---

## 2. Restructuring decisions (why this shape)

1. **Monorepo root = product root** — One `pnpm-workspace.yaml` (`apps/*`, `packages/*`) so CI, Docker, and editors share a single install graph.
2. **`packages/config` vs app `src/shared/config`** — Zod **schemas** and parsing live in `@studyos/config` (reusable, testable without Next). The web app re-exports at `src/shared/config/env.ts` so feature code imports a **stable app-local path** (`@/shared/config/env`) while staying DRY.
3. **Legacy `src/lib/env.ts`** — Thin re-export only. Avoids breaking deep links or old imports; new code should prefer `@/shared/config/env`.
4. **Route groups** — `(marketing)`, `(auth)`, `(app)` separate layouts and concerns without changing URLs.
5. **`@/` + `@/shared/*` + `@/features/*` (tsconfig)** — `@/*` remains the escape hatch; explicit aliases document intent and improve IDE navigation.
6. **`src/shared/lib/index.ts`** — Barrel for **tiny** shared helpers (`cn`, …) so UI imports stay short (`@/shared/lib`).
7. **`@studyos/shared` `utils/invariant.ts`** — Cross-package **runtime assertion** for narrow cases; prefer Zod at boundaries when possible.
8. **`.vscode/settings.json`** — Format-on-save + workspace TypeScript + ESLint auto working dirs for smoother DX (optional for contributors).

---

## 3. Files moved (this restructuring pass)

| From | To |
|------|-----|
| `apps/web/src/lib/env.test.ts` | `apps/web/src/shared/config/env.test.ts` |

**Compatibility stub (not a move):** `apps/web/src/lib/env.ts` now re-exports from `@/shared/config/env` so existing `@/lib/env` imports keep working.

**New files (this pass)**

- `apps/web/src/shared/config/env.ts`
- `apps/web/src/shared/lib/index.ts`
- `packages/shared/src/utils/invariant.ts`
- `.vscode/settings.json` (workspace)

**Updated:** `apps/web/tsconfig.json`, `apps/web/src/shared/api/http.ts`, UI components’ `cn` imports, `packages/shared/src/index.ts`, root `package.json` (`check` script).

---

## 4. Import aliases (web)

| Alias | Resolves to |
|-------|-------------|
| `@/*` | `apps/web/src/*` |
| `@/features/*` | `apps/web/src/features/*` |
| `@/shared/*` | `apps/web/src/shared/*` |
| `@studyos/config` | `packages/config` (workspace) |
| `@studyos/shared` | `packages/shared` (workspace) |

---

## 5. Commands

```bash
pnpm install
pnpm check          # lint + typecheck + test (no build)
pnpm turbo run lint typecheck test build
```

API (`apps/api`):

```bash
uv sync --all-groups
uv run pytest -q
```

---

## 6. Web frontend foundation (enterprise)

| Area | Implementation |
|------|----------------|
| **Layouts** | Root `layout.tsx` (fonts, skip link, `<main id="main">`); route groups `(marketing)`, `(auth)`, `(app)` with `AppShell` for authenticated chrome. |
| **Routing** | App Router file conventions: `loading.tsx` / `error.tsx` per segment; global `app/error.tsx`. |
| **Theme** | `next-themes` (`ThemeProvider` in `providers.tsx`); design tokens in `globals.css` (`:root` / `.dark`); `ThemeToggle` in shell header. |
| **UI system** | `shared/components/ui/*` — `Button`, `Input`, `Label`, `Card` (+ header/title/content), `Skeleton`, `Alert`, `Spinner`; semantic Tailwind tokens (`bg-background`, `text-primary`, …). |
| **API layer** | `shared/api/http.ts` — `apiFetch` + `ApiError`; toasts via `shared/lib/toast.ts` including `notifyFromUnknown`. |
| **Loading / errors** | `(marketing)/loading.tsx`, `(app)/loading.tsx`; `(app)/error.tsx`; root `error.tsx` with reset. |
| **Auth** | `STUDYOS_SESSION_COOKIE` in `features/auth/constants.ts`; `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/session`; `SessionProvider` + `useSession`; `AppSessionGate` under `(app)` (syncs with middleware + focus refresh). |
| **Protected routes** | `middleware.ts` matcher for `/dashboard/*` + client `AppSessionGate`. |
| **Forms** | `react-hook-form` + `FormProvider` + `FormField` (`shared/components/form/form-field.tsx`) + Zod resolver. |
| **Notifications** | `sonner` `<Toaster />` in `AppProviders`; helpers `notifySuccess` / `notifyError` / `notifyFromUnknown` exported from `@/shared/lib`. |
| **Hooks** | `useMounted`, `useMediaQuery`, `useDebouncedValue`; optional `useRequireSession` in `features/auth/hooks/`. |
