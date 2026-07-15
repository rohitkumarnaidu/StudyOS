# StudyOS — Developer Onboarding Guide

**Date:** 2026-05-18  
**Version:** 1.0  
**Time to first commit:** ~30 minutes

---

## 1. Welcome to StudyOS! 🎓

StudyOS is an AI-first study operating system built for NEET exam preparation. It's a **pnpm + Turborepo monorepo** with:
- **Web:** Next.js 16 (React 19) — BFF + frontend
- **API:** FastAPI (Python 3.12) — business logic
- **Database:** PostgreSQL via Supabase
- **Cache:** Redis

---

## 2. Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **Node.js** | 20.x | `nvm install 20` |
| **pnpm** | 9.x | `corepack enable` |
| **Python** | 3.12 | `uv python install 3.12` |
| **uv** | Latest | `pip install uv` |
| **Git** | 2.x | System package manager |

### Optional but Recommended
- **Docker** — For local database/Redis
- **Supabase CLI** — For database migrations
- **pre-commit** — For automated checks

---

## 3. Setup (First Time)

### 3.1 Clone and Install
```bash
# Clone the repo
git clone https://github.com/your-org/studyos.git
cd studyos

# Install dependencies
pnpm install

# Install pre-commit hooks (optional)
pre-commit install
```

### 3.2 Environment Setup
```bash
# Copy environment templates
cp apps/web/.env.example apps/web/.env
cp apps/api/.env.example apps/api/.env

# Edit with your values (use provided defaults for local dev)
```

### 3.3 Database Setup
```bash
# Option 1: Use Supabase cloud (recommended)
# Create project at https://supabase.com
# Copy connection string to apps/api/.env

# Option 2: Use local Docker
docker compose -f docker/docker-compose.yml up postgres redis -d

# Run migrations
pnpm supabase migration up
```

### 3.4 Verify Setup
```bash
# Start everything
pnpm dev

# Visit:
# - Web: http://localhost:3000
# - API: http://localhost:8000/docs
# - Demo login: demo@studyos.app / demo
```

---

## 4. Project Structure

```
STUDYOS/
├── apps/
│   ├── web/              # Next.js 16 frontend
│   │   ├── src/
│   │   │   ├── app/      # App Router (pages)
│   │   │   ├── features/ # Feature modules
│   │   │   ├── shared/   # Shared components/utils
│   │   │   └── server/   # Server actions
│   │   └── public/       # Static assets
│   └── api/              # FastAPI backend
│       ├── src/studyos_api/
│       │   ├── api/      # Route handlers
│       │   ├── services/ # Business logic
│       │   ├── core/     # Config, errors, logging
│       │   └── ai/       # AI/LLM integration
│       └── tests/        # Test suite
├── packages/             # Shared packages
│   ├── config/           # Zod-validated config
│   └── tsconfig/         # Shared TS configs
├── supabase/
│   └── migrations/       # SQL migrations
├── docker/               # Docker configs
└── docs/                 # Documentation
```

---

## 5. Development Workflow

### 5.1 Making Changes
```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# Web: apps/web/src/...
# API: apps/api/src/...

# 3. Run tests
pnpm test          # All tests
pnpm --filter @studyos/api test   # API only
pnpm --filter @studyos/web test   # Web only

# 4. Lint and typecheck
pnpm lint          # All lint
pnpm typecheck     # All typecheck

# 5. Commit
git add .
git commit -m "feat: add my feature"

# 6. Push and create PR
git push origin feature/my-feature
```

### 5.2 Code Review Checklist
- [ ] Tests added/updated
- [ ] Lint and typecheck pass
- [ ] No console.log in production code
- [ ] Error handling implemented
- [ ] Documentation updated

---

## 6. Key Commands

### Development
| Command | Description |
|---------|-------------|
| `pnpm dev` | Start all apps in dev mode |
| `pnpm --filter @studyos/web dev` | Start web only |
| `pnpm --filter @studyos/api dev` | Start API only |

### Testing
| Command | Description |
|---------|-------------|
| `pnpm test` | Run all tests |
| `pnpm --filter @studyos/api test` | API tests |
| `pnpm --filter @studyos/web test` | Web tests |
| `pnpm exec playwright test` | E2E tests |

### Quality
| Command | Description |
|---------|-------------|
| `pnpm lint` | Lint all apps |
| `pnpm typecheck` | Typecheck all apps |
| `pnpm format:check` | Check formatting |
| `pnpm format:write` | Fix formatting |

### Database
| Command | Description |
|---------|-------------|
| `pnpm supabase migration up` | Apply migrations |
| `pnpm supabase db reset` | Reset database |
| `pnpm supabase gen types typescript` | Generate TS types |

---

## 7. Architecture Overview

### Request Flow
```
Browser → Next.js (BFF) → FastAPI → PostgreSQL
           ↓                  ↓
        Redis Cache       Redis Cache
```

### Key Patterns
- **BFF Pattern:** Next.js acts as Backend-for-Frontend
- **Feature-based organization:** Code grouped by feature
- **Server Components:** Default in Next.js 16
- **Type Safety:** TypeScript + Pydantic validation
- **Error Handling:** Structured logging + error boundaries

---

## 8. Testing Guide

### API Tests (Python)
```python
# tests/api/test_my_feature.py
class TestMyFeature:
    def test_happy_path(self, client, auth_headers):
        resp = client.get("/v1/my-feature", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["success"] is True
```

### Web Tests (TypeScript)
```typescript
// src/features/my-feature/__tests__/my-component.test.tsx
describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
```

### E2E Tests (Playwright)
```typescript
// e2e/my-feature.spec.ts
test('user can use my feature', async ({ page }) => {
  await page.goto('/my-feature')
  await expect(page.getByText('Hello')).toBeVisible()
})
```

---

## 9. Common Issues

### "Module not found" errors
```bash
# Clear pnpm cache and reinstall
pnpm store prune
pnpm install
```

### Database connection errors
```bash
# Check DATABASE_URL in apps/api/.env
# Verify Supabase project is running
# Check network connectivity
```

### Port conflicts
```bash
# Web: 3000, API: 8000, Redis: 6379, Postgres: 5432
# Kill existing processes or change ports in .env
```

---

## 10. Resources

| Resource | Link |
|----------|------|
| **Architecture Docs** | `docs/architecture/` |
| **API Documentation** | `http://localhost:8000/docs` |
| **Design System** | `apps/web/DESIGN.md` |
| **Testing Guide** | `docs/engineering/TESTING_GUIDELINES.md` |
| **Deployment Guide** | `DEPLOYMENT_GUIDE.md` |
| **AGENTS.md** | `AGENTS.md` (for AI assistants) |

---

## 11. Team Contacts

| Role | Contact |
|------|---------|
| **Engineering Lead** | [TBD] |
| **Frontend Lead** | [TBD] |
| **Backend Lead** | [TBD] |
| **DevOps** | [TBD] |

---

## 12. First Task Suggestions

1. **Good First Issue:** Fix a typo in documentation
2. **Easy:** Add a test for an untested function
3. **Medium:** Add a new UI component
4. **Hard:** Implement a new API endpoint

---

Welcome aboard! 🚀
