# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# ✅ Create All 12 Phase 0 GitHub Issues

**Use this guide to create all Phase 0 issues in your GitHub repo.**

Choose your method below ↓

---

## 🔧 Method 1: GitHub CLI (Fastest — 5 minutes)

**Prerequisites:**
```bash
# Install GitHub CLI (if not installed)
# macOS:
brew install gh

# Windows:
winget install GitHub.cli

# Then authenticate
gh auth login
```

**Create all 12 issues with this script:**

```bash
#!/bin/bash
# save as: create_phase0_issues.sh

REPO="your-org/studyos"  # Change to your repo

# TIER 1: Critical Path
gh issue create --repo $REPO \
  --title "[Phase 0] Monorepo Verification & Dependency Installation" \
  --body "Get the monorepo booting with all dependencies installed and checks passing.

## Acceptance Criteria
- [ ] pnpm install (0 errors)
- [ ] turbo run lint passes all files
- [ ] turbo run typecheck returns 0 errors
- [ ] turbo run test passes all unit tests
- [ ] turbo run build succeeds for all apps

## Commands
\`\`\`bash
cd STUDYOS
pnpm install
pnpm turbo run lint typecheck test build
\`\`\`

## Documentation
- docs/STUDYOS_COMPLETE_SUMMARY.md
- docs/ARCHITECTURE.md" \
  --label "phase-0,setup,critical" \
  --assignee "your-github-handle" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] Supabase Project Linking (Staging)" \
  --body "Create and link Supabase staging project. Prepare for Phase 1 migrations.

## Acceptance Criteria
- [ ] Supabase account created (or existing project identified)
- [ ] Staging project ref captured as STAGING_PROJECT_ID
- [ ] supabase link --project-ref=STAGING_PROJECT_ID succeeds
- [ ] supabase db push --dry-run shows 0 errors
- [ ] Database types generated and committed
- [ ] Google OAuth provider configured (placeholder credentials)

## Commands
\`\`\`bash
supabase projects list
supabase link --project-ref=\$STAGING_PROJECT_ID
supabase db push --dry-run
supabase gen types typescript > apps/web/src/types/database.types.ts
git add . && git commit -m 'chore: add supabase types'
\`\`\`" \
  --label "phase-0,backend,database,critical" \
  --assignee "devops-engineer" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] GitHub Actions CI Pipeline Setup" \
  --body "Set up CI/CD pipeline for lint, typecheck, test, and build checks.

## Acceptance Criteria
- [ ] .github/workflows/ci.yml created with jobs: lint, typecheck, test, build
- [ ] PR trigger: on pull_request to main, staging
- [ ] Test PR created; all checks pass
- [ ] Checks are required before merge (branch protection)
- [ ] Workflow duration < 5 minutes" \
  --label "phase-0,devops,ci-cd,critical" \
  --assignee "devops-engineer" \
  --milestone "Phase 0"

# TIER 2: Observability
gh issue create --repo $REPO \
  --title "[Phase 0] Vercel Project Setup & Preview Deploys" \
  --body "Link apps/web to Vercel for automatic preview deploys on PR.

## Acceptance Criteria
- [ ] Vercel account created
- [ ] apps/web linked to Vercel project
- [ ] Environment variables configured (non-secret placeholders)
- [ ] Test PR created; Vercel bot comments with preview URL
- [ ] Preview loads successfully (stub app OK)" \
  --label "phase-0,devops,deployment" \
  --assignee "devops-engineer" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] Sentry Integration (Error Tracking)" \
  --body "Integrate Sentry for error tracking and performance monitoring.

## Acceptance Criteria
- [ ] Sentry account + project created
- [ ] DSN stored in NEXT_PUBLIC_SENTRY_DSN
- [ ] @sentry/nextjs initialized in apps/web
- [ ] /api/test-error endpoint created for testing
- [ ] Test error sent to Sentry and appears in dashboard
- [ ] Performance monitoring enabled (5% sample rate)" \
  --label "phase-0,observability" \
  --assignee "fullstack-engineer" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] PostHog Integration (Product Analytics)" \
  --body "Integrate PostHog for product analytics and session recording.

## Acceptance Criteria
- [ ] PostHog account created (free tier OK)
- [ ] Project key in NEXT_PUBLIC_POSTHOG_KEY
- [ ] PostHog SDK initialized in apps/web/src/app/providers.tsx
- [ ] Test event fired via posthog.capture('test_event')
- [ ] Event appears in PostHog dashboard
- [ ] Session recording enabled (1% sample rate)" \
  --label "phase-0,observability,analytics" \
  --assignee "fullstack-engineer" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] Docker Local Development Setup" \
  --body "Set up Docker Compose for local development with all services.

## Acceptance Criteria
- [ ] docker/docker-compose.yml updated with:
  - Supabase (postgres, auth, storage, studio)
  - Redis (Upstash mock for local dev)
  - Next.js web app
- [ ] docker-compose up --build succeeds
- [ ] http://localhost:3000 loads app
- [ ] http://localhost:54323 loads Supabase Studio
- [ ] All containers healthy
- [ ] docker-compose down cleans up" \
  --label "phase-0,devops,docker" \
  --assignee "devops-engineer" \
  --milestone "Phase 0"

# TIER 3: Documentation
gh issue create --repo $REPO \
  --title "[Phase 0] Development Environment README" \
  --body "Create comprehensive README files for dev environment setup.

## Acceptance Criteria
- [ ] apps/web/README.md: quick start, env vars, structure, common tasks
- [ ] apps/api/README.md: Python + FastAPI setup
- [ ] docs/DEVELOPMENT.md: Git workflow, branch naming, PR checklist
- [ ] New team members can go from git clone → running app in <1 hour" \
  --label "phase-0,documentation" \
  --assignee "fullstack-engineer" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] Environment Variables Documentation" \
  --body "Document all environment variables and secrets policy.

## Acceptance Criteria
- [ ] .env.example updated with all Phase 0 vars
- [ ] docs/.env.reference.md created explaining each var:
  - Required/optional
  - Format
  - Example
  - Where to get it
- [ ] Secrets policy documented (never commit real secrets)
- [ ] CI/CD guide for setting secrets in GitHub/Vercel" \
  --label "phase-0,documentation,security" \
  --assignee "devops-engineer" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] GitHub Issues Template for Phase 1" \
  --body "Create 20+ GitHub issues for Phase 1 tasks with templates and board.

## Acceptance Criteria
- [ ] 20+ issues created for Phase 1 (auth, syllabus, database, frontend, backend)
- [ ] All issues have:
  - Clear description + acceptance criteria
  - Assignee placeholder
  - Effort estimate
  - Dependencies listed
  - Labels: phase-1, area (auth/frontend/backend/database)
- [ ] GitHub project board created (kanban: To Do, In Progress, Done)
- [ ] Phase 1 issues added to project board" \
  --label "phase-0,process" \
  --assignee "fullstack-engineer" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] Team Onboarding Checklist" \
  --body "Create onboarding guide for new team members.

## Acceptance Criteria
- [ ] docs/ONBOARDING.md created with:
  - Welcome message
  - 1-hour quick start (clone, install, run)
  - Key documentation links (architecture, skills, roadmap)
  - Communication channels
  - Code style (Prettier, ESLint)
  - Testing expectations
- [ ] New team member can complete in <1 hour
- [ ] GitHub wiki or docs site updated with link to ONBOARDING.md" \
  --label "phase-0,documentation,onboarding" \
  --assignee "tech-lead" \
  --milestone "Phase 0"

gh issue create --repo $REPO \
  --title "[Phase 0] Sign-Off & Phase 1 Kickoff" \
  --body "Verify all Phase 0 items complete and kickoff Phase 1.

## Acceptance Criteria
- [ ] All 11 prior issues closed ✓
- [ ] Demo checklist:
  - [ ] pnpm install && pnpm dev works
  - [ ] Vercel preview shows app shell
  - [ ] Sentry error captured
  - [ ] PostHog event fired
  - [ ] docker-compose up loads all services
- [ ] Phase 1 issues assigned to engineers
- [ ] Phase 1 kickoff meeting: 30 min (architecture review)
- [ ] Phase 1 project board set up in GitHub" \
  --label "phase-0,process,milestone" \
  --assignee "tech-lead" \
  --milestone "Phase 0"

echo "✅ All 12 Phase 0 issues created!"
```

**Run it:**
```bash
# Make executable
chmod +x create_phase0_issues.sh

# Run
./create_phase0_issues.sh

# Expected output:
# Created issue #1
# Created issue #2
# ...
# ✅ All 12 Phase 0 issues created!
```

---

## 🌐 Method 2: GitHub Web UI (Manual — 15 minutes)

1. Go to your GitHub repo → **Issues**
2. Click **New Issue**
3. Copy/paste from [.github/PHASE_0_ISSUES.md](.github/PHASE_0_ISSUES.md)

**Quick steps for each issue:**

| Issue | Title | Owner | Time |
|-------|-------|-------|------|
| #1 | Monorepo Verification | Full-Stack | 5 min |
| #2 | Supabase Linking | DevOps | 5 min |
| #3 | GitHub Actions | DevOps | 5 min |
| #4 | Vercel Setup | DevOps | 5 min |
| #5 | Sentry | Full-Stack | 5 min |
| #6 | PostHog | Full-Stack | 5 min |
| #7 | Docker | DevOps | 5 min |
| #8 | READMEs | Full-Stack | 5 min |
| #9 | Env Vars | DevOps | 5 min |
| #10 | Phase 1 Issues | Full-Stack | 5 min |
| #11 | Onboarding | Tech Lead | 5 min |
| #12 | Sign-Off | Tech Lead | 5 min |

---

## 📊 Method 3: GitHub Project Board Setup

After creating issues, set up a **GitHub Project** for Phase 0:

**Steps:**

1. Go to repo → **Projects** → **New Project**
2. Name: `Phase 0 Execution`
3. Template: `Kanban` (automated columns)
4. Columns:
   - 📋 Backlog
   - 🔄 In Progress
   - ✅ Done

**Add issues:**
1. Click **Add items** → Add all 12 issues
2. Drag issues to **Backlog**

**Daily workflow:**
- Morning: Assign today's tasks from Backlog → In Progress
- EOD: Move completed tasks → Done
- 4:30 PM standup: Report In Progress → Done items

---

## ✅ Verification Checklist

After creating all 12 issues, verify:

```bash
# Check issue count
gh issue list --label "phase-0" --state all | wc -l
# Expected: 12

# Check critical issues
gh issue list --label "critical" --label "phase-0"
# Expected: Issues #1, #2, #3

# Check by assignee
gh issue list --assignee "devops-engineer" --label "phase-0"
gh issue list --assignee "fullstack-engineer" --label "phase-0"
gh issue list --assignee "tech-lead" --label "phase-0"
```

---

## 🎯 Next Steps (After Creating Issues)

1. ✅ **All 12 issues created**
2. 👥 **Assign to team** (use assignee fields above)
3. 📊 **Create GitHub Project board** (instructions above)
4. 📅 **Schedule daily 4:30 PM standups** (see PHASE_0_CHECKLIST.md)
5. 🚀 **Begin Day 1 execution** (see PHASE_0_DAY1_COMMANDS.md)

---

## 📞 If You Get Stuck

**GitHub CLI won't authenticate?**
```bash
gh auth login --web
```

**gh command not found?**
```bash
# Install it again
brew install gh  # or your package manager
```

**Issues not appearing?**
```bash
gh issue list --repo your-org/studyos
```

**Need help?** Post in #studyos-general with the error message.

---

**Status:** 🟢 READY TO CREATE  
**Time Required:** 5-15 minutes (depends on method)  
**Next:** PHASE_0_CHECKLIST.md for daily standup template

Go! 🚀
