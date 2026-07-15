# StudyOS — AI-Powered Learning Platform

**Free platform for NEET 2026 aspirants.** AI tutoring, PDF + Mind Map notes pipeline, offline-first PWA, adaptive quizzes, personalized roadmaps.

**START HERE:** [docs/STUDYOS_COMPLETE_SUMMARY.md](docs/STUDYOS_COMPLETE_SUMMARY.md) — master reference for architecture, product specs, and implementation roadmap.

For detailed layout, see **`ARCHITECTURE.md`** for the enterprise-style structure (route groups, `packages/*`, API layers).

---

## What's Built

### Phase 0 ✅ Complete
- Monorepo (pnpm + Turborepo) with 2 apps + 4 packages
- CI/CD pipeline (JS + Python + E2E)
- Docker compose (api + web + postgres + redis)
- 11 database migrations with RLS policies
- NEET 2026 syllabus seed (91 chapters)
- Auth: login/signup + Google OAuth + JWT + rotating refresh tokens
- Dashboard shell with chapter list
- Progress API + Syllabus API
- AI backend module (multi-provider, streaming, MCP)

### Phase 1 🟡 In Progress
- Topics/subtopics seeding (450+ subtopics)
- Progress UI wiring (checkboxes, optimistic updates)
- Streak system
- Dashboard enhancement (progress rings, study stats)

---

## Layout

```
./
├── apps/
│   ├── web/                 # Next.js 16 (route groups, features/, shared/)
│   └── api/                 # FastAPI (core/, api/v1/, ai/, services/)
├── packages/
│   ├── config/              # Zod public env (@studyos/config)
│   ├── shared/              # Constants / tiny shared TS
│   ├── eslint-config/
│   └── typescript-config/
├── supabase/                # Postgres migrations + seed
├── docker/                  # Dockerfiles + compose
├── docs/
│   ├── architecture/        # 18 docs: FINAL_ARCHITECTURE, SYSTEM_DESIGN, etc.
│   ├── engineering/         # ENGINEERING.md, ADRs, TESTING, PRODUCTION_READINESS
│   ├── product/             # NEET spec: plan/, skills-app/, skills-claude/
│   ├── database/            # ERD, indexing, migrations guide
│   ├── auth/                # Supabase Google OAuth setup
│   └── security/            # Authentication security guide
├── .github/workflows/       # CI pipeline
├── ARCHITECTURE.md          # Monorepo structure + commands
├── EXECUTIVE_SUMMARY.md     # Vision, timeline, costs, risks
└── README.md                # This file
```

---

## Environment

Copy templates and replace placeholders (never commit real secrets):

| Template | Copy to |
|----------|---------|
| `apps/web/.env.example` | `apps/web/.env.local` |
| `apps/api/.env.example` | `apps/api/.env` |
| `apps/web/.env.production.example` | reference for prod |
| `apps/api/.env.production.example` | reference for prod |

---

## Commands

```bash
pnpm install              # Install all dependencies
pnpm dev                  # Start all dev servers
pnpm check                # Lint + typecheck + test
pnpm build                # Production build
pnpm format               # Auto-format code
```

API (Python):
```bash
uv sync --all-groups
uv run pytest -q
```

---

## Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) | Vision, timeline, costs, risks |
| [docs/architecture/FINAL_ARCHITECTURE.md](docs/architecture/FINAL_ARCHITECTURE.md) | Canonical tech choices |
| [docs/architecture/IMPLEMENTATION_ROADMAP.md](docs/architecture/IMPLEMENTATION_ROADMAP.md) | 7-wave roadmap (22 weeks) |
| [docs/architecture/IMPLEMENTATION_PHASES.md](docs/architecture/IMPLEMENTATION_PHASES.md) | Technical milestones per phase |
| [docs/architecture/SYSTEM_DESIGN.md](docs/architecture/SYSTEM_DESIGN.md) | C4 diagrams, request flows, PDF pipeline |
| [docs/architecture/ENTERPRISE_ARCHITECTURE.md](docs/architecture/ENTERPRISE_ARCHITECTURE.md) | Business domains, NFRs, team topology |
| [docs/architecture/DATABASE_PLAN.md](docs/architecture/DATABASE_PLAN.md) | Schema strategy, scaling, backups |
| [docs/architecture/DATABASE_SCHEMA_PLAN.md](docs/architecture/DATABASE_SCHEMA_PLAN.md) | 20 migrations, RLS matrix, indexing |
| [docs/architecture/FEATURE_PRIORITY.md](docs/architecture/FEATURE_PRIORITY.md) | P0/P1/P2 feature ranking |
| [docs/architecture/DEVELOPMENT_PHASES.md](docs/architecture/DEVELOPMENT_PHASES.md) | Engineering workflow, DoR/DoD |
| [docs/architecture/API_ARCHITECTURE.md](docs/architecture/API_ARCHITECTURE.md) | BFF pattern, error model, rate limits |
| [docs/architecture/AI_SYSTEM_DESIGN.md](docs/architecture/AI_SYSTEM_DESIGN.md) | LangGraph, RAG, cost controls |
| [docs/architecture/DEVOPS_PLAN.md](docs/architecture/DEVOPS_PLAN.md) | CI/CD, secrets, monitoring |
| [docs/engineering/PRODUCTION_READINESS.md](docs/engineering/PRODUCTION_READINESS.md) | Honest production audit |
| [docs/engineering/ENTERPRISE_READINESS.md](docs/engineering/ENTERPRISE_READINESS.md) | Enterprise checklist |

**Product specs:** [docs/product/PRODUCT_FOLDER_INVENTORY.md](docs/product/PRODUCT_FOLDER_INVENTORY.md)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript strict |
| **Styling** | Tailwind CSS v4, shadcn/ui (Radix) |
| **State** | TanStack Query v5, Zustand, Dexie (offline) |
| **PWA** | Serwist (service worker) |
| **Backend** | FastAPI (Python 3.12), Supabase (PostgreSQL) |
| **AI** | Multi-provider (Anthropic, OpenAI, Ollama), LangGraph |
| **PDF** | pdfplumber, pdf.js, vision model OCR |
| **Mind Maps** | @xyflow/react (interactive viewer) |
| **Vector DB** | pgvector (PostgreSQL extension) |
| **Deploy** | Vercel (web), Supabase (DB), Railway/Fly (API) |

---

## Implementation Status

| Phase | Status | Duration |
|-------|--------|----------|
| Phase 0: Foundation | ✅ Complete | 1 week |
| Phase 1: Auth + Syllabus + Progress | 🟡 In Progress | 1-2 weeks |
| Phase 2: Offline + PWA + Settings | ⏳ Planned | 1-2 weeks |
| Phase 3: AI Tutor Chat | ⏳ Planned | 2-3 weeks |
| Phase 4: PDF + Mind Map Pipeline | ⏳ Planned | 3-4 weeks |
| Phase 5: Quizzes + Mock Tests | ⏳ Planned | 3-4 weeks |
| Phase 6: Analytics + Roadmap | ⏳ Planned | 2-3 weeks |
| Phase 7: Scale + Launch | ⏳ Planned | 2-3 weeks |

**Total:** ~22 weeks to launch-ready

---

**Last updated:** 2026-05-16
