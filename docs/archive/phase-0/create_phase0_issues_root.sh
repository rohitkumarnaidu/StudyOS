#!/bin/bash

# Phase 0 GitHub Issues Creation Script
# Usage: ./create_phase0_issues.sh <repo> <devops-handle> <fullstack-handle> <tech-lead-handle>
# Example: ./create_phase0_issues.sh "your-org/studyos" "alice" "bob" "charlie"

if [ $# -ne 4 ]; then
  echo "Usage: $0 <repo> <devops-handle> <fullstack-handle> <tech-lead-handle>"
  echo "Example: $0 'your-org/studyos' 'alice' 'bob' 'charlie'"
  exit 1
fi

REPO=$1
DEVOPS=$2
FULLSTACK=$3
TECH_LEAD=$4

echo "🚀 Creating 12 Phase 0 GitHub Issues..."
echo "📦 Repository: $REPO"
echo "👤 DevOps: @$DEVOPS"
echo "👤 Full-Stack: @$FULLSTACK"
echo "👤 Tech Lead: @$TECH_LEAD"
echo ""

# Verify gh is installed
if ! command -v gh &> /dev/null; then
  echo "❌ GitHub CLI not found. Install with: brew install gh"
  exit 1
fi

# TIER 1: CRITICAL PATH

echo "📍 Creating TIER 1 (Critical Path) issues..."

# Issue #1: Monorepo Verification
gh issue create --repo "$REPO" \
  --title "[Phase 0] #1 — Monorepo Verification & Dependency Installation" \
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
- docs/ARCHITECTURE.md

## Details
- **Effort:** 2 hours
- **Status:** Not Started
- **Depends on:** None
" \
  --label "phase-0,setup,critical" \
  --assignee "$FULLSTACK" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #1 created"

# Issue #2: Supabase Linking
gh issue create --repo "$REPO" \
  --title "[Phase 0] #2 — Supabase Project Linking (Staging)" \
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
\`\`\`

## Documentation
- docs/auth/SUPABASE_GOOGLE.md
- docs/database/README.md

## Details
- **Effort:** 3 hours
- **Status:** Not Started
- **Depends on:** #1
" \
  --label "phase-0,backend,database,critical" \
  --assignee "$DEVOPS" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #2 created"

# Issue #3: GitHub Actions
gh issue create --repo "$REPO" \
  --title "[Phase 0] #3 — GitHub Actions CI Pipeline Setup" \
  --body "Set up CI/CD pipeline for lint, typecheck, test, and build checks.

## Acceptance Criteria
- [ ] .github/workflows/ci.yml created with jobs: lint, typecheck, test, build
- [ ] PR trigger: on pull_request to main, staging
- [ ] Test PR created; all checks pass
- [ ] Checks are required before merge (branch protection)
- [ ] Workflow duration < 5 minutes

## Jobs
- lint: ESLint + Prettier check
- typecheck: TypeScript strict mode
- test: Vitest (unit tests)
- build: turbo build

## Documentation
- docs/architecture/DEVOPS_PLAN.md

## Details
- **Effort:** 4 hours
- **Status:** Not Started
- **Depends on:** #1
" \
  --label "phase-0,devops,ci-cd,critical" \
  --assignee "$DEVOPS" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #3 created"

# TIER 2: OBSERVABILITY

echo ""
echo "📍 Creating TIER 2 (Observability) issues..."

# Issue #4: Vercel Setup
gh issue create --repo "$REPO" \
  --title "[Phase 0] #4 — Vercel Project Setup & Preview Deploys" \
  --body "Link apps/web to Vercel for automatic preview deploys on PR.

## Acceptance Criteria
- [ ] Vercel account created
- [ ] apps/web linked to Vercel project
- [ ] Environment variables configured (non-secret placeholders)
- [ ] Test PR created; Vercel bot comments with preview URL
- [ ] Preview loads successfully (stub app OK)

## Details
- **Effort:** 2 hours
- **Status:** Not Started
- **Depends on:** #1
" \
  --label "phase-0,devops,deployment" \
  --assignee "$DEVOPS" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #4 created"

# Issue #5: Sentry Integration
gh issue create --repo "$REPO" \
  --title "[Phase 0] #5 — Sentry Integration (Error Tracking)" \
  --body "Integrate Sentry for error tracking and performance monitoring.

## Acceptance Criteria
- [ ] Sentry account + project created
- [ ] DSN stored in NEXT_PUBLIC_SENTRY_DSN
- [ ] @sentry/nextjs initialized in apps/web
- [ ] /api/test-error endpoint created for testing
- [ ] Test error sent to Sentry and appears in dashboard
- [ ] Performance monitoring enabled (5% sample rate)

## Verification
\`\`\`bash
npm run dev
curl http://localhost:3000/api/test-error
# Check Sentry dashboard
\`\`\`

## Details
- **Effort:** 2.5 hours
- **Status:** Not Started
- **Depends on:** #1
" \
  --label "phase-0,observability" \
  --assignee "$FULLSTACK" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #5 created"

# Issue #6: PostHog Integration
gh issue create --repo "$REPO" \
  --title "[Phase 0] #6 — PostHog Integration (Product Analytics)" \
  --body "Integrate PostHog for product analytics and session recording.

## Acceptance Criteria
- [ ] PostHog account created (free tier OK)
- [ ] Project key in NEXT_PUBLIC_POSTHOG_KEY
- [ ] PostHog SDK initialized in apps/web/src/app/providers.tsx
- [ ] Test event fired via posthog.capture('test_event')
- [ ] Event appears in PostHog dashboard
- [ ] Session recording enabled (1% sample rate)

## Details
- **Effort:** 2 hours
- **Status:** Not Started
- **Depends on:** #1
" \
  --label "phase-0,observability,analytics" \
  --assignee "$FULLSTACK" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #6 created"

# Issue #7: Docker Compose
gh issue create --repo "$REPO" \
  --title "[Phase 0] #7 — Docker Local Development Setup" \
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
- [ ] docker-compose down cleans up

## Verification
\`\`\`bash
docker-compose -f docker/docker-compose.yml up --build
# Wait 30s
curl http://localhost:3000
curl http://localhost:54323
\`\`\`

## Details
- **Effort:** 3 hours
- **Status:** Not Started
- **Depends on:** #2
" \
  --label "phase-0,devops,docker" \
  --assignee "$DEVOPS" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #7 created"

# TIER 3: DOCUMENTATION

echo ""
echo "📍 Creating TIER 3 (Documentation) issues..."

# Issue #8: Development READMEs
gh issue create --repo "$REPO" \
  --title "[Phase 0] #8 — Development Environment README" \
  --body "Create comprehensive README files for dev environment setup.

## Acceptance Criteria
- [ ] apps/web/README.md: quick start, env vars, structure, common tasks
- [ ] apps/api/README.md: Python + FastAPI setup
- [ ] docs/DEVELOPMENT.md: Git workflow, branch naming, PR checklist
- [ ] New team members can go from git clone → running app in <1 hour

## Details
- **Effort:** 2 hours
- **Status:** Not Started
- **Depends on:** #1
" \
  --label "phase-0,documentation" \
  --assignee "$FULLSTACK" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #8 created"

# Issue #9: Environment Variables
gh issue create --repo "$REPO" \
  --title "[Phase 0] #9 — Environment Variables Documentation" \
  --body "Document all environment variables and secrets policy.

## Acceptance Criteria
- [ ] .env.example updated with all Phase 0 vars
- [ ] docs/.env.reference.md created explaining each var:
  - Required/optional
  - Format
  - Example
  - Where to get it
- [ ] Secrets policy documented (never commit real secrets)
- [ ] CI/CD guide for setting secrets in GitHub/Vercel

## Details
- **Effort:** 1.5 hours
- **Status:** Not Started
- **Depends on:** #1-7
" \
  --label "phase-0,documentation,security" \
  --assignee "$DEVOPS" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #9 created"

# Issue #10: Phase 1 Issues
gh issue create --repo "$REPO" \
  --title "[Phase 0] #10 — GitHub Issues Template for Phase 1" \
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
- [ ] Phase 1 issues added to project board

## Reference
- docs/architecture/IMPLEMENTATION_PHASES.md § Phase 1

## Details
- **Effort:** 2 hours
- **Status:** Not Started
- **Depends on:** #1
" \
  --label "phase-0,process" \
  --assignee "$FULLSTACK" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #10 created"

# Issue #11: Team Onboarding
gh issue create --repo "$REPO" \
  --title "[Phase 0] #11 — Team Onboarding Checklist" \
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
- [ ] GitHub wiki or docs site updated with link to ONBOARDING.md

## Details
- **Effort:** 1 hour
- **Status:** Not Started
- **Depends on:** #1, #8
" \
  --label "phase-0,documentation,onboarding" \
  --assignee "$TECH_LEAD" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #11 created"

# Issue #12: Sign-Off
gh issue create --repo "$REPO" \
  --title "[Phase 0] #12 — Sign-Off & Phase 1 Kickoff" \
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
- [ ] Phase 1 project board set up in GitHub

## Next Steps
- Proceed to docs/architecture/IMPLEMENTATION_PHASES.md § Phase 1
- Auth system development begins

## Details
- **Effort:** 1 hour
- **Status:** Not Started
- **Depends on:** #1-11
" \
  --label "phase-0,process,milestone" \
  --assignee "$TECH_LEAD" \
  --milestone "Phase 0" 2>/dev/null && echo "✅ Issue #12 created"

echo ""
echo "✅ SUCCESS! All 12 Phase 0 issues created!"
echo ""
echo "📊 Next steps:"
echo "1. Go to: https://github.com/$REPO/issues?labels=phase-0"
echo "2. Create a GitHub Project board: https://github.com/$REPO/projects"
echo "3. Add all 12 issues to the board"
echo "4. Start with PHASE_0_DAY1_COMMANDS.md"
echo ""
echo "🚀 Ready to execute Phase 0!"
