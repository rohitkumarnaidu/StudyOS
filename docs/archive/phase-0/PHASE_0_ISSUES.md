# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# GitHub Issues — Phase 0 (Ready to Create)

Copy and paste these into your GitHub repo to create issues automatically.

---

## TIER 1 — CRITICAL PATH

### Issue #1: Monorepo Verification & Dependency Installation

```
Title: [Phase 0] Monorepo Verification & Dependency Installation

Description:
Get the monorepo booting with all dependencies installed and checks passing.

Acceptance Criteria:
- [ ] pnpm install (0 errors)
- [ ] turbo run lint passes all files
- [ ] turbo run typecheck returns 0 errors
- [ ] turbo run test passes all unit tests
- [ ] turbo run build succeeds for all apps

Commands:
\`\`\`bash
cd STUDYOS
pnpm install
pnpm turbo run lint typecheck test build
\`\`\`

Documentation:
- docs/STUDYOS_COMPLETE_SUMMARY.md § Ready for Development
- docs/ARCHITECTURE.md

Labels: phase-0, setup, critical
Assignee: Full-Stack Engineer
Effort: 2 hours
Depends on: None
```

---

### Issue #2: Supabase Project Linking (Staging)

```
Title: [Phase 0] Supabase Project Linking (Staging)

Description:
Create and link Supabase staging project. Prepare for Phase 1 migrations.

Acceptance Criteria:
- [ ] Supabase account created (or existing project identified)
- [ ] Staging project ref captured as STAGING_PROJECT_ID
- [ ] supabase link --project-ref=STAGING_PROJECT_ID succeeds
- [ ] supabase db push --dry-run shows 0 errors
- [ ] Database types generated and committed
- [ ] Google OAuth provider configured (placeholder credentials)

Commands:
\`\`\`bash
supabase projects list
supabase link --project-ref=$STAGING_PROJECT_ID
supabase db push --dry-run
supabase gen types typescript > apps/web/src/types/database.types.ts
git add . && git commit -m "chore: add supabase types"
\`\`\`

Documentation:
- docs/auth/SUPABASE_GOOGLE.md
- docs/database/README.md

Labels: phase-0, backend, database, critical
Assignee: DevOps Engineer
Effort: 3 hours
Depends on: #1
```

---

### Issue #3: GitHub Actions CI Pipeline Setup

```
Title: [Phase 0] GitHub Actions CI Pipeline Setup

Description:
Set up CI/CD pipeline for lint, typecheck, test, and build checks.

Acceptance Criteria:
- [ ] .github/workflows/ci.yml created with jobs: lint, typecheck, test, build
- [ ] PR trigger: on pull_request to main, staging
- [ ] Test PR created; all checks pass
- [ ] Checks are required before merge (branch protection)
- [ ] Workflow duration < 5 minutes

Jobs:
- lint: ESLint + Prettier check
- typecheck: TypeScript strict mode
- test: Vitest (unit tests)
- build: turbo build

Documentation:
- docs/architecture/DEVOPS_PLAN.md

Labels: phase-0, devops, ci-cd, critical
Assignee: DevOps Engineer
Effort: 4 hours
Depends on: #1
```

---

## TIER 2 — OBSERVABILITY WIRED

### Issue #4: Vercel Project Setup & Preview Deploys

```
Title: [Phase 0] Vercel Project Setup & Preview Deploys

Description:
Link apps/web to Vercel for automatic preview deploys on PR.

Acceptance Criteria:
- [ ] Vercel account created
- [ ] apps/web linked to Vercel project
- [ ] Environment variables configured (non-secret placeholders)
- [ ] Test PR created; Vercel bot comments with preview URL
- [ ] Preview loads successfully (stub app OK)

Labels: phase-0, devops, deployment
Assignee: DevOps Engineer
Effort: 2 hours
Depends on: #1
```

---

### Issue #5: Sentry Integration (Error Tracking)

```
Title: [Phase 0] Sentry Integration (Error Tracking)

Description:
Integrate Sentry for error tracking and performance monitoring.

Acceptance Criteria:
- [ ] Sentry account + project created
- [ ] DSN stored in NEXT_PUBLIC_SENTRY_DSN
- [ ] @sentry/nextjs initialized in apps/web
- [ ] /api/test-error endpoint created for testing
- [ ] Test error sent to Sentry and appears in dashboard
- [ ] Performance monitoring enabled (5% sample rate)

Verification:
\`\`\`bash
npm run dev
curl http://localhost:3000/api/test-error
# Check Sentry dashboard
\`\`\`

Labels: phase-0, observability
Assignee: Full-Stack Engineer
Effort: 2.5 hours
Depends on: #1
```

---

### Issue #6: PostHog Integration (Product Analytics)

```
Title: [Phase 0] PostHog Integration (Product Analytics)

Description:
Integrate PostHog for product analytics and session recording.

Acceptance Criteria:
- [ ] PostHog account created (free tier OK)
- [ ] Project key in NEXT_PUBLIC_POSTHOG_KEY
- [ ] PostHog SDK initialized in apps/web/src/app/providers.tsx
- [ ] Test event fired via posthog.capture('test_event')
- [ ] Event appears in PostHog dashboard
- [ ] Session recording enabled (1% sample rate)

Labels: phase-0, observability, analytics
Assignee: Full-Stack Engineer
Effort: 2 hours
Depends on: #1
```

---

### Issue #7: Docker Local Development Setup

```
Title: [Phase 0] Docker Local Development Setup

Description:
Set up Docker Compose for local development with all services.

Acceptance Criteria:
- [ ] docker/docker-compose.yml updated with:
  - Supabase (postgres, auth, storage, studio)
  - Redis (Upstash mock for local dev)
  - Next.js web app
- [ ] docker-compose up --build succeeds
- [ ] http://localhost:3000 loads app
- [ ] http://localhost:54323 loads Supabase Studio
- [ ] All containers healthy
- [ ] docker-compose down cleans up

Verification:
\`\`\`bash
docker-compose -f docker/docker-compose.yml up --build
# Wait 30s
curl http://localhost:3000
curl http://localhost:54323
\`\`\`

Labels: phase-0, devops, docker
Assignee: DevOps Engineer
Effort: 3 hours
Depends on: #2
```

---

## TIER 3 — DOCUMENTATION & HANDOFF

### Issue #8: Development Environment README

```
Title: [Phase 0] Development Environment README

Description:
Create comprehensive README files for dev environment setup.

Acceptance Criteria:
- [ ] apps/web/README.md: quick start, env vars, structure, common tasks
- [ ] apps/api/README.md: Python + FastAPI setup
- [ ] docs/DEVELOPMENT.md: Git workflow, branch naming, PR checklist
- [ ] New team members can go from git clone → running app in <1 hour

Labels: phase-0, documentation
Assignee: Full-Stack Engineer
Effort: 2 hours
Depends on: #1
```

---

### Issue #9: Environment Variables Documentation

```
Title: [Phase 0] Environment Variables Documentation

Description:
Document all environment variables and secrets policy.

Acceptance Criteria:
- [ ] .env.example updated with all Phase 0 vars
- [ ] docs/.env.reference.md created explaining each var:
  - Required/optional
  - Format
  - Example
  - Where to get it
- [ ] Secrets policy documented (never commit real secrets)
- [ ] CI/CD guide for setting secrets in GitHub/Vercel

Labels: phase-0, documentation, security
Assignee: DevOps Engineer
Effort: 1.5 hours
Depends on: #1–7
```

---

### Issue #10: GitHub Issues Template for Phase 1

```
Title: [Phase 0] GitHub Issues Template for Phase 1

Description:
Create 20+ GitHub issues for Phase 1 tasks with templates and board.

Acceptance Criteria:
- [ ] 20+ issues created for Phase 1 (auth, syllabus, database, frontend, backend)
- [ ] All issues have:
  - Clear description + acceptance criteria
  - Assignee placeholder
  - Effort estimate
  - Dependencies listed
  - Labels: phase-1, area (auth/frontend/backend/database)
- [ ] GitHub project board created (kanban: To Do, In Progress, Done)
- [ ] Phase 1 issues added to project board

Reference:
- docs/architecture/IMPLEMENTATION_PHASES.md § Phase 1

Labels: phase-0, process
Assignee: Full-Stack Engineer
Effort: 2 hours
Depends on: #1
```

---

### Issue #11: Team Onboarding Checklist

```
Title: [Phase 0] Team Onboarding Checklist

Description:
Create onboarding guide for new team members.

Acceptance Criteria:
- [ ] docs/ONBOARDING.md created with:
  - Welcome message
  - 1-hour quick start (clone, install, run)
  - Key documentation links (architecture, skills, roadmap)
  - Communication channels
  - Code style (Prettier, ESLint)
  - Testing expectations
- [ ] New team member can complete in <1 hour
- [ ] GitHub wiki or docs site updated with link to ONBOARDING.md

Labels: phase-0, documentation, onboarding
Assignee: Tech Lead
Effort: 1 hour
Depends on: #1, #8
```

---

### Issue #12: Phase 0 Sign-Off & Phase 1 Kickoff

```
Title: [Phase 0] Sign-Off & Phase 1 Kickoff

Description:
Verify all Phase 0 items complete and kickoff Phase 1.

Acceptance Criteria:
- [ ] All 11 prior issues closed ✓
- [ ] Demo checklist:
  - [ ] pnpm install && pnpm dev works
  - [ ] Vercel preview shows app shell
  - [ ] Sentry error captured
  - [ ] PostHog event fired
  - [ ] docker-compose up loads all services
- [ ] Phase 1 issues assigned to engineers
- [ ] Phase 1 kickoff meeting: 30 min (architecture review)
- [ ] Phase 1 project board set up in GitHub

Next:
- Proceed to IMPLEMENTATION_PHASES.md § Phase 1
- Auth system development begins

Labels: phase-0, process, milestone
Assignee: Tech Lead
Effort: 1 hour
Depends on: #1–11
```

---

## 🔄 How to Create These Issues

### Option A: GitHub UI (Manual)
1. Go to your GitHub repo → Issues → New Issue
2. Copy title and description from above
3. Add labels and assignee
4. Click "Create"

### Option B: GitHub API (Bash)
See `CREATE_PHASE_0_ISSUES.md` for detailed instructions

### Option C: Use Automated Script
```bash
chmod +x create_phase0_issues.sh
./create_phase0_issues.sh "your-org/studyos" "alice" "bob" "charlie"
```

---

## 📊 Phase 0 Project Board

Create a GitHub Project with these columns:

```
📋 Backlog (all 12 issues)
   ↓
🔄 In Progress (current work)
   ↓
✅ Done (completed issues)
```

**Start with:** Issue #1, #2, #3 in parallel  
**Then:** Issue #4, #5, #6, #7  
**Finally:** Issue #8–12

---

**Use this as reference while executing Phase 0 over the next 5 days.**
