# StudyOS — Monorepo Structure

**Canonical:** Turborepo + **pnpm** with the **package root at `studyos/`** (this directory in the repository).  
**Why pnpm:** strict `node_modules` isolation, fast CI caches, workspace protocol for internal packages.

---

## 1. Repository layout

```
<git-root>/                       # clone folder (e.g. StudyOS/)
├── README.md                     # points you at studyos/
├── .gitignore                    # ignores accidental root node_modules
└── studyos/                      # ← pnpm workspace root (open this in your IDE)
    ├── package.json
    ├── pnpm-workspace.yaml       # packages: apps/*, packages/*
    ├── turbo.json
    ├── .github/workflows/
    ├── README.md
    ├── .env.example
    ├── apps/
    │   ├── web/                  # Next.js frontend
    │   └── api/                  # FastAPI backend
    ├── packages/                 # @studyos/* shared TS libraries
    │   ├── eslint-config/
    │   ├── typescript-config/
    │   └── shared/
    ├── docker/                   # Dockerfiles + compose
    └── docs/
        ├── architecture/         # system design, FINAL_ARCHITECTURE, DB plans, …
        ├── engineering/          # ENGINEERING.md, ADRs
        └── product/              # NEET spec: plan/, skills-app/, skills-claude/, MASTER_README.md
```

Future packages (`ui`, `database`, `ai`, …) still go under **`packages/`**. Optional **`apps/workers`** when job runners are added.

---

## 2. App boundaries

### `apps/web`

- **Next.js** App Router, Server Components by default.  
- **Route Handlers** under `app/api/**` when a thin BFF must live with the UI.  
- **`public/`** static assets.

### `apps/api`

- **FastAPI** — AI orchestration, webhooks, long-running orchestration.  
- **Never** imported by the web bundle; call over HTTP from server or client as designed.

### `apps/workers` (future)

- Inngest / queue consumers. Communicate via DB or events, not direct imports from `web`.

---

## 3. Package dependency rules (conceptual)

| Package        | May import                                      |
| -------------- | ----------------------------------------------- |
| `domain`       | stdlib only (no `apps/*`)                       |
| `database`     | `@supabase/supabase-js`, generated types        |
| `ui`           | `react`, `tailwind`, radix — no DB client in UI |
| `web` (app)    | `packages/*` except worker-only code            |

Enforce with **ESLint boundaries** (or `@nx/enforce-module-boundaries`) when you add Nx-style rules.

---

## 4. Turborepo

Caching and the task graph live in **`turbo.json`** next to `package.json`. From **`studyos/`**:

`pnpm turbo run lint typecheck test build`

---

## 5. Product specification (`docs/product`)

Original **`STUDYOS/`** tree (plans, skills, syllabus guide) now lives under **`docs/product/`**. Treat it as **product source**, not runtime code.

---

*See `docs/architecture/FINAL_ARCHITECTURE.md` for stack decisions.*
