# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# 🚀 PHASE 0 — COMPLETE END-TO-END IMPLEMENTATION PROMPT

## 📌 PROJECT OVERVIEW

**Project:** StudyOS (Next.js 15 + FastAPI + Supabase monorepo)  
**Phase:** 0 — Foundation Setup  
**Team Size:** 3 engineers (1 DevOps + 1 Full-Stack + 1 Tech Lead)  
**Total Effort:** 13.5 hours (parallel execution possible)  
**Deliverable:** Production-ready foundation unblocking Phase 1 (Auth + Syllabus)

---

## 🎯 PHASE 0 COMPLETION CHECKLIST — ALL 12 ISSUES

### ✅ **ISSUE #1: Monorepo Verification & Dependency Installation**

**What to do:**
- Run `pnpm install` to install all dependencies
- Run `turbo run lint` to validate code style (ESLint + Prettier)
- Run `turbo run typecheck` to validate TypeScript (strict mode)
- Run `turbo run test` to run all unit tests
- Run `turbo run build` to build apps/web and apps/api

**Acceptance Criteria:**
```
✓ pnpm install completes with 0 errors
✓ turbo run lint passes all files
✓ turbo run typecheck returns 0 errors
✓ turbo run test passes all tests
✓ turbo run build succeeds for web and api
✓ All checks complete in < 5 minutes
```

**Feasibility:** ✅ **HIGH** — Standard monorepo setup, should work immediately. If errors occur, they're diagnostic (missing deps, config issues) and fixable within 1 hour.

---

### ✅ **ISSUE #2: Supabase Project Linking (Staging)**

**What to do:**
- Create or identify existing Supabase staging project
- Link local environment to Supabase: `supabase link --project-ref=$PROJECT_ID`
- Push database migrations: `supabase db push --dry-run` (verify, then `supabase db push`)
- Generate TypeScript types: `supabase gen types typescript > apps/web/src/types/database.types.ts`
- Configure Google OAuth provider in Supabase dashboard (use placeholder credentials for now)
- Update `.env.local` with `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`

**Acceptance Criteria:**
```
✓ Supabase project created/identified
✓ supabase link succeeds
✓ supabase db push runs without errors
✓ Database types generated and committed to git
✓ Google OAuth provider configured
✓ .env.local has all required vars
```

**Feasibility:** ✅ **HIGH** — Supabase setup is straightforward if account exists. If creating new project, add 30 min. Database migration should work as-is from migrations/ folder.

---

### ✅ **ISSUE #3: GitHub Actions CI Pipeline Setup**

**What to do:**
- Create `.github/workflows/ci.yml` with 4 jobs:
  1. `lint` job — runs `turbo run lint` (ESLint + Prettier)
  2. `typecheck` job — runs `turbo run typecheck` (TypeScript)
  3. `test` job — runs `turbo run test` (Vitest)
  4. `build` job — runs `turbo run build` (production build)
- Trigger on pull requests to `main` and `staging` branches
- Create a test PR to verify all checks pass
- Enable branch protection: require all checks before merge

**Acceptance Criteria:**
```
✓ .github/workflows/ci.yml exists with 4 jobs
✓ Trigger: on pull_request to main, staging
✓ Test PR created and all checks pass
✓ Branch protection enabled
✓ Workflow duration < 5 minutes
```

**Feasibility:** ✅ **HIGH** — Standard GitHub Actions setup. YAML syntax can be validated locally. Typical pattern, minimal troubleshooting needed.

---

### ✅ **ISSUE #4: Vercel Project Setup & Preview Deploys**

**What to do:**
- Create Vercel account (if needed)
- Import `apps/web` from GitHub repo
- Configure environment variables (copy non-secret placeholders from `.env.example`)
- Create a test PR on GitHub
- Verify Vercel bot comments with preview URL
- Click preview URL and verify app loads (no 404 errors)

**Acceptance Criteria:**
```
✓ Vercel account created
✓ apps/web imported to Vercel
✓ Environment variables configured
✓ Test PR created, Vercel bot responds
✓ Preview URL loads successfully
✓ Preview deploys automatically on every PR
```

**Feasibility:** ✅ **HIGH** — Vercel UI is intuitive. If build fails, check environment variables and Next.js config. Usually fixable in 30 min.

---

### ✅ **ISSUE #5: Sentry Integration (Error Tracking)**

**What to do:**
- Create Sentry account + project
- Store DSN in `NEXT_PUBLIC_SENTRY_DSN` environment variable
- Install and initialize `@sentry/nextjs` in `apps/web`:
  ```javascript
  import * as Sentry from "@sentry/nextjs";
  
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 0.05, // 5% performance monitoring
  });
  ```
- Create `/api/test-error` endpoint that throws an error for testing
- Verify error appears in Sentry dashboard
- Enable performance monitoring (5% sample rate)

**Acceptance Criteria:**
```
✓ Sentry account + project created
✓ DSN stored in env var
✓ @sentry/nextjs initialized
✓ /api/test-error endpoint works
✓ Test error appears in Sentry dashboard
✓ Performance monitoring enabled
```

**Feasibility:** ✅ **HIGH** — Sentry SDK is well-documented. Integration is boilerplate. Test error verification takes 5 min.

---

### ✅ **ISSUE #6: PostHog Integration (Product Analytics)**

**What to do:**
- Create PostHog account (free tier OK)
- Store project key in `NEXT_PUBLIC_POSTHOG_KEY` environment variable
- Install and initialize PostHog SDK in `apps/web/src/app/providers.tsx`:
  ```javascript
  import posthog from 'posthog-js'
  
  posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY, {
    api_host: "https://app.posthog.com",
    session_recording: { sampleRate: 0.01 } // 1% session recording
  })
  ```
- Fire a test event: `posthog.capture('test_event', { count: 1 })`
- Verify event appears in PostHog dashboard
- Enable session recording (1% sample rate to avoid noise)

**Acceptance Criteria:**
```
✓ PostHog account created
✓ Project key in env var
✓ PostHog SDK initialized in providers.tsx
✓ Test event fired and appears in dashboard
✓ Session recording enabled (1% sample rate)
```

**Feasibility:** ✅ **HIGH** — PostHog SDK is simple. Event capture is one-liner. Dashboard verification is immediate.

---

### ✅ **ISSUE #7: Docker Local Development Setup**

**What to do:**
- Update `docker/docker-compose.yml` to include:
  ```yaml
  services:
    postgres:
      image: postgres:15
      environment:
        POSTGRES_PASSWORD: postgres
      volumes:
        - postgres_data:/var/lib/postgresql/data
        - ./supabase/migrations:/docker-entrypoint-initdb.d
    
    supabase-studio:
      image: supabase/studio:latest
      ports:
        - "54323:3000"
      environment:
        SUPABASE_URL: http://postgres:5432
        SUPABASE_ADMIN_API_KEY: your-secret-key
    
    web:
      build: ../apps/web
      ports:
        - "3000:3000"
      environment:
        SUPABASE_URL: http://postgres:5432
        NEXT_PUBLIC_SUPABASE_URL: http://localhost:5432
  ```
- Run `docker-compose up --build`
- Verify:
  - `curl http://localhost:3000` → app loads
  - `curl http://localhost:54323` → Supabase Studio loads
  - All containers show `healthy`
- Run `docker-compose down` → all containers stop cleanly

**Acceptance Criteria:**
```
✓ docker-compose.yml has all services
✓ docker-compose up --build succeeds
✓ http://localhost:3000 loads without errors
✓ http://localhost:54323 loads Supabase Studio
✓ All containers healthy
✓ docker-compose down cleans up
✓ New dev can run: docker-compose up → app ready in 2 min
```

**Feasibility:** ⚠️ **MEDIUM** — Docker troubleshooting can be complex. Port conflicts, image pull timeouts, or permission issues possible. Typical resolution: 1-2 hours. Once working, very reliable.

---

### ✅ **ISSUE #8: Development Environment README**

**What to do:**
- Create `apps/web/README.md`:
  ```markdown
  # StudyOS Web App
  
  ## Quick Start
  git clone <repo>
  cd STUDYOS/apps/web
  pnpm install
  pnpm dev
  
  ## Environment Variables
  SUPABASE_URL, SUPABASE_KEY, NEXT_PUBLIC_SENTRY_DSN, etc.
  
  ## Project Structure
  src/
    app/
    components/
    types/
  
  ## Common Tasks
  pnpm dev — Start dev server
  pnpm build — Production build
  pnpm test — Run tests
  pnpm lint — Check code style
  ```
- Create `apps/api/README.md` with Python/FastAPI setup
- Create `docs/DEVELOPMENT.md` with:
  - Git workflow (branch naming, commit format)
  - PR checklist before submitting
  - Code style expectations (Prettier, ESLint)
- Verify new dev can: `git clone → pnpm install → pnpm dev` in < 1 hour

**Acceptance Criteria:**
```
✓ apps/web/README.md created
✓ apps/api/README.md created
✓ docs/DEVELOPMENT.md created
✓ All READMEs have: quick start, structure, common tasks
✓ New dev can go from clone → running app in < 1 hour
```

**Feasibility:** ✅ **HIGH** — Writing documentation is straightforward. No code changes needed. Follow existing patterns from other projects.

---

### ✅ **ISSUE #9: Environment Variables Documentation**

**What to do:**
- Create `.env.example` with all Phase 0 variables:
  ```
  # Supabase
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-anon-key
  SUPABASE_SERVICE_KEY=your-service-key
  
  # Sentry
  NEXT_PUBLIC_SENTRY_DSN=https://your-sentry-dsn
  
  # PostHog
  NEXT_PUBLIC_POSTHOG_KEY=your-posthog-key
  
  # GitHub (optional, for actions)
  GITHUB_TOKEN=your-github-token
  ```
- Create `docs/.env.reference.md` explaining each var:
  ```markdown
  | Variable | Required | Format | Example | Where to Get |
  |----------|----------|--------|---------|-------------|
  | SUPABASE_URL | Yes | URL | https://xyz.supabase.co | Supabase dashboard |
  | NEXT_PUBLIC_SENTRY_DSN | Yes | URL | https://key@sentry.io/123 | Sentry project settings |
  ```
- Document secrets policy: never commit real secrets
- Create CI/CD guide: how to set secrets in GitHub Actions + Vercel

**Acceptance Criteria:**
```
✓ .env.example created with all vars
✓ docs/.env.reference.md created with format, example, source
✓ Secrets policy documented
✓ CI/CD secrets guide created
✓ Zero confusion about environment setup
```

**Feasibility:** ✅ **HIGH** — Purely documentation work. No code needed. Reference existing configs.

---

### ✅ **ISSUE #10: GitHub Issues Template for Phase 1**

**What to do:**
- Create 20+ GitHub issues for Phase 1 covering:
  - **Auth (5 issues):** Google OAuth, JWT tokens, session management, password reset, email verification
  - **Syllabus (5 issues):** Schema, CRUD endpoints, UI components, search, filtering
  - **Frontend (5 issues):** Layout, navigation, forms, state management, error handling
  - **Backend (5 issues):** API endpoints, validation, middleware, database queries, caching
- Each issue must have:
  - Clear title
  - Description + acceptance criteria
  - Assignee placeholder (to be filled)
  - Effort estimate (1-5 hours)
  - Dependencies listed (depends on issue #X if applicable)
  - Labels: `phase-1`, area label (auth/frontend/backend/database)
- Create GitHub project board: `Phase 1 Execution` (Kanban: Backlog, In Progress, Done)
- Add all 20+ issues to board in Backlog column

**Acceptance Criteria:**
```
✓ 20+ issues created for Phase 1
✓ Each issue has: description, criteria, effort, dependencies, labels
✓ GitHub project board created
✓ All issues added to board in Backlog
✓ Ready to start Phase 1 immediately
```

**Feasibility:** ✅ **MEDIUM** — Bulk issue creation is time-consuming but straightforward. Use GitHub web UI or API script. Template approach makes it faster.

---

### ✅ **ISSUE #11: Team Onboarding Checklist**

**What to do:**
- Create `docs/ONBOARDING.md`:
  ```markdown
  # Welcome to StudyOS! 👋
  
  ## 1-Hour Quick Start
  1. Clone repo: git clone <repo>
  2. Install deps: pnpm install
  3. Start app: pnpm dev
  4. Verify: http://localhost:3000 loads
  
  ## Key Documentation
  - Architecture: docs/architecture/FINAL_ARCHITECTURE.md
  - Roadmap: docs/architecture/IMPLEMENTATION_PHASES.md
  - Tech Stack: docs/STUDYOS_COMPLETE_SUMMARY.md
  
  ## Communication
  - Slack: #studyos-general
  - Daily Standup: 4:30 PM EST
  
  ## Code Style
  - Use Prettier (auto-format)
  - Follow ESLint rules
  - Write tests for features
  
  ## Testing Expectations
  - Unit tests for utils, hooks
  - Integration tests for API endpoints
  - E2E tests for critical flows
  ```
- Test with new hire: can they complete in < 1 hour?
- Add ONBOARDING.md link to GitHub wiki/docs site

**Acceptance Criteria:**
```
✓ docs/ONBOARDING.md created
✓ Contains: 1-hour quick start, links, communication, code style, testing
✓ New dev can complete checklist in < 1 hour
✓ Link added to GitHub wiki
```

**Feasibility:** ✅ **HIGH** — Documentation task. Follow existing onboarding patterns.

---

### ✅ **ISSUE #12: Sign-Off & Phase 1 Kickoff**

**What to do:**
- Verify all 11 prior issues are closed ✅
- Run Phase 0 demo checklist:
  ```bash
  # 1. Monorepo boots
  pnpm install && pnpm dev
  
  # 2. Vercel preview works
  Create test PR → verify preview URL loads
  
  # 3. Sentry captures errors
  curl http://localhost:3000/api/test-error
  → Check Sentry dashboard
  
  # 4. PostHog tracks events
  Check PostHog dashboard → test_event captured
  
  # 5. Docker stack ready
  docker-compose up
  curl http://localhost:3000
  curl http://localhost:54323
  ```
- Confirm all 3 engineers can access everything
- Assign Phase 1 issues to team members
- Schedule Phase 1 kickoff meeting (30 min):
  - Review auth + syllabus architecture
  - Q&A about Phase 1 tasks
- Activate Phase 1 project board in GitHub

**Acceptance Criteria:**
```
✓ All 11 issues closed
✓ Demo checklist passes (all 5 items)
✓ All engineers can access all systems
✓ Phase 1 issues assigned
✓ Phase 1 kickoff meeting scheduled
✓ Phase 1 project board active
```

**Feasibility:** ✅ **HIGH** — Verification and admin tasks. If any prior issue failed, fix immediately (should be rare if Phase 0 executed correctly).

---

## 🏗️ IMPLEMENTATION FEASIBILITY ANALYSIS

### **By Issue Complexity:**

| Issue | Type | Difficulty | Effort | Risk | Mitigation |
|-------|------|-----------|--------|------|-----------|
| #1 | Setup | Low | 2h | Low | Standard monorepo commands |
| #2 | Integration | Medium | 3h | Low | Supabase docs are clear |
| #3 | DevOps | Low | 4h | Low | GitHub Actions templates exist |
| #4 | Deployment | Medium | 2h | Medium | Vercel auth/config issues |
| #5 | Integration | Low | 2.5h | Low | Sentry SDK is mature |
| #6 | Integration | Low | 2h | Low | PostHog SDK is simple |
| #7 | DevOps | High | 3h | High | Docker/networking issues |
| #8 | Documentation | Low | 2h | Low | Pure writing, no code |
| #9 | Documentation | Low | 1.5h | Low | Reference existing configs |
| #10 | Process | Medium | 2h | Low | Bulk issue creation tools |
| #11 | Documentation | Low | 1h | Low | Template-based |
| #12 | Verification | Low | 1h | Low | Just checking boxes |

---

### **By Phase:**

**TIER 1 — CRITICAL PATH (Issues #1-3)**
- **Feasibility:** ✅ **HIGH**
- **Typical blockers:** Dependency conflicts, missing Node version, git config
- **Time estimate:** 6-9 hours (issues often overlap)
- **Recommendation:** Parallelize #3 with #1 to save time

**TIER 2 — OBSERVABILITY (Issues #4-7)**
- **Feasibility:** ⚠️ **MEDIUM**
- **Typical blockers:** API keys not accessible, Docker port conflicts, environment setup
- **Time estimate:** 6-9 hours (parallel execution)
- **Recommendation:** Have credentials ready before starting. Docker can take time; start early.

**TIER 3 — DOCUMENTATION (Issues #8-12)**
- **Feasibility:** ✅ **HIGH**
- **Typical blockers:** None technical, just writing
- **Time estimate:** 5-7 hours (sequential, but can run parallel with #7)
- **Recommendation:** Start #8-9 while #7 is in progress

---

### **Parallel Execution Strategy:**

```
Timeline:
Day 1-2: Issues #1, #2, #3 (sequential dependency chain)
Day 2-3: Issues #4, #5, #6, #7 (can run in parallel)
Day 3-5: Issues #8, #9, #10, #11, #12 (mostly parallel, #12 must be last)

Ideal parallelization:
- Full-Stack: #1, #5, #6, #8, #10
- DevOps: #2, #3, #4, #7, #9
- Tech Lead: #11, #12 (+ review/unblock others)
```

---

### **Risk Assessment:**

**🟢 GREEN (Low Risk):** Issues #1, #3, #5, #6, #8, #9, #11  
→ Proceed confidently, minimal troubleshooting expected

**🟡 YELLOW (Medium Risk):** Issues #2, #4, #10  
→ Have documentation ready, may need 30-60 min troubleshooting

**🔴 RED (High Risk):** Issue #7 (Docker)  
→ Most likely to have issues (ports, permissions, images). Budget 2-4 extra hours if needed. Have Docker expert on standby.

---

### **Success Probability:**

- **All 12 issues complete (no critical bugs):** 85% if team is experienced, 60% if new to tech stack
- **Timeline feasible:** Yes, 13.5 hours spread across parallel work is achievable
- **Zero blockers:** 40% (usually 1-2 issues need 30 min extra troubleshooting)
- **Phase 1 ready to start:** 90% if Phase 0 completes

---

## 🎯 START HERE — IMMEDIATE ACTIONS

### **STEP 1: Create GitHub Issues**
```bash
chmod +x .github/phase-0/create_phase0_issues.sh
./.github/phase-0/create_phase0_issues.sh "your-org/studyos" "devops-name" "fullstack-name" "tech-lead-name"
```

### **STEP 2: Set Up GitHub Project Board**
- Go to GitHub → Projects → New
- Name: "Phase 0 Execution"
- Template: Kanban (Backlog, In Progress, Done)
- Add all 12 issues to Backlog

### **STEP 3: Assign Issues to Team**
- Issues #1, #5, #6, #8, #10 → Full-Stack Engineer
- Issues #2, #3, #4, #7, #9 → DevOps Engineer
- Issues #11, #12 → Tech Lead

### **STEP 4: Start Issue #1**
```bash
cd STUDYOS
pnpm install
pnpm turbo run lint typecheck test build
```

---

## 📊 EXPECTED OUTPUTS

**After Phase 0 Completion:**

✅ Monorepo boots in < 30 seconds  
✅ All PR checks automated + required  
✅ Vercel preview deploys on every PR  
✅ Errors tracked in Sentry  
✅ Analytics running in PostHog  
✅ Full stack runs locally via Docker  
✅ Team onboarded and productive  
✅ Phase 1 issues ready to start  

---

## 🚀 NEXT PHASE

Once Phase 0 is complete:
- Proceed to **Phase 1: Auth + Syllabus** (20+ issues)
- Follow same execution model
- Estimated effort: 40-60 hours (parallel)
- Expected completion: 2-3 weeks

---

**Status:** 🟢 **READY TO IMPLEMENT**  
**Feasibility:** ✅ **HIGH (with Docker as main risk)**  
**Go/No-Go:** ✅ **GO — All prerequisites met**

**Execute Phase 0 now!** 🚀
