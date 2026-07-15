# StudyOS API (FastAPI)

Service API under `apps/api`. See the monorepo [`README.md`](../../README.md).

## Setup

```bash
cd apps/api   # or from repo root: pnpm --filter @studyos/api exec uv sync --all-groups
uv sync --all-groups
```

## Commands

| Command | Description |
|--------|-------------|
| `pnpm dev` | Uvicorn with reload |
| `pnpm lint` | Ruff |
| `pnpm typecheck` | Mypy |
| `pnpm test` | Pytest |

## Environment

Copy `../../.env.example` into `apps/api/.env` for local overrides.
