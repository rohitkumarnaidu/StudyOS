# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# ⏰ Phase 0 Day 1 — Commands & Timeline

**Date:** May 14, 2026 (Monday)  
**Timeline:** 9 AM – 5 PM  
**Tasks:** Issues #1–3, #5–6 (critical path + observability)

---

## 🌅 MORNING (9 AM–12 PM) — Get Code Running

### Task: Issue #1 — Monorepo Verification (Full-Stack)

```bash
# 1. Go to project root
cd STUDYOS

# 2. Install all dependencies (5 min)
pnpm install

# Expected output:
# ✓ Resolved 2345 dependencies
# ✓ Linked 5 workspaces
# ✓ 2,345 packages in 45s

# 3. Run all checks (15 min)
pnpm turbo run lint typecheck test build

# Expected output:
# ✓ lint: 0 errors
# ✓ typecheck: 0 errors
# ✓ test: passed
# ✓ build: all apps built successfully
```

**✅ If all pass:** Issue #1 is DONE

**Expected:** 2 hours total (includes waiting for installs/builds)

---

## 🌤️ AFTERNOON (2 PM–5 PM) — Parallel Tasks

**DevOps Engineer:** Issues #2 & #3  
**Full-Stack Engineer:** Issues #5 & #6

### PARALLEL TASK A: Issue #2 — Supabase Linking (DevOps)

```bash
# 1. Create Supabase account (if not done)
# https://supabase.com → Create project

# 2. Get your project ref
# Dashboard → Settings → General → Project Ref (copy the ID)

# 3. Store it
export SUPABASE_PROJECT_REF="your_ref_here"

# 4. Link project
supabase link --project-ref=$SUPABASE_PROJECT_REF

# Expected output:
# ✓ Linked to project [your_ref]
# ✓ Auth configured
# ✓ Database configured

# 5. Dry run migrations (verify 0 errors)
supabase db push --dry-run

# Expected output:
# Prepared migration: ...sql (0 errors)
# Ready to push

# 6. Generate types
supabase gen types typescript > apps/web/src/types/database.types.ts

# 7. Commit
git add . && git commit -m "chore: add supabase types"
```

**✅ If all pass:** Issue #2 is DONE  
**Expected:** 3 hours

---

### PARALLEL TASK B: Issue #3 — GitHub Actions CI (DevOps)

```bash
# 1. Create GitHub Actions workflow
# File: .github/workflows/ci.yml

name: CI/CD

on:
  pull_request:
    branches: [main, staging]
  push:
    branches: [main, staging]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"
      - run: pnpm install
      - run: pnpm turbo run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"
      - run: pnpm install
      - run: pnpm turbo run typecheck

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"
      - run: pnpm install
      - run: pnpm turbo run test

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"
      - run: pnpm install
      - run: pnpm turbo run build

# 2. Commit and push
git add .github/workflows/ci.yml
git commit -m "ci: add github actions workflow"
git push origin main

# 3. Create test PR to verify workflow runs
git checkout -b test/ci-pipeline
echo "# Test PR" >> README.md
git add . && git commit -m "test: ci pipeline"
git push origin test/ci-pipeline

# 4. Go to GitHub and check PR
# GitHub → Pull Requests → Your test PR
# Should see GitHub Actions running (4 jobs: lint, typecheck, test, build)
```

**✅ If all jobs pass:** Issue #3 is DONE  
**Expected:** 4 hours (includes waiting for first workflow run)

---

### PARALLEL TASK C: Issue #5 — Sentry Integration (Full-Stack)

```bash
# 1. Create Sentry account
# https://sentry.io → Create organization + project (select Next.js)

# 2. Get your DSN
# Sentry Dashboard → Settings → Projects → Your Project → Client Keys (DSN)
# Format: https://xxx@yyy.ingest.sentry.io/zzz

# 3. Store in .env.local
echo "NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn_here" >> .env.local

# 4. Install Sentry package
cd apps/web
pnpm add @sentry/nextjs

# 5. Initialize in next.config.ts
# (The SDK auto-initializes if DSN is in env — it's magic!)

# 6. Start dev server
npm run dev

# 7. Trigger test error (open new terminal)
curl http://localhost:3000/api/test-error
# This should cause an error

# 8. Check Sentry dashboard
# Go to: https://sentry.io/organizations/[your-org]/issues/
# Should see test error appear within 10 seconds
```

**✅ If error appears in Sentry:** Issue #5 is DONE  
**Expected:** 2.5 hours

---

### PARALLEL TASK D: Issue #6 — PostHog Integration (Full-Stack)

```bash
# 1. Create PostHog account
# https://posthog.com → Sign up (free tier)

# 2. Get API key
# PostHog → Settings → Project settings → Project API key (phc_xxx)

# 3. Store in .env.local
echo "NEXT_PUBLIC_POSTHOG_KEY=your_posthog_key_here" >> .env.local

# 4. Install PostHog package
cd apps/web
pnpm add posthog-js

# 5. Initialize in apps/web/src/app/providers.tsx
import { PostHogProvider } from 'posthog-js/react'

export function Providers() {
  return (
    <PostHogProvider
      apiKey={process.env.NEXT_PUBLIC_POSTHOG_KEY}
      options={{
        api_host: 'https://app.posthog.com',
      }}
    >
      {/* your app */}
    </PostHogProvider>
  )
}

# 6. Fire test event in any component
import { usePostHog } from 'posthog-js/react'

export function TestComponent() {
  const posthog = usePostHog()
  
  useEffect(() => {
    posthog?.capture('phase_0_test_event')
  }, [])
}

# 7. Check PostHog dashboard
# PostHog → Events → Should see 'phase_0_test_event' within 10 seconds
```

**✅ If event appears in PostHog:** Issue #6 is DONE  
**Expected:** 2 hours

---

## ✅ END OF DAY 1 CHECKLIST

```bash
# Verify all critical path complete:
pnpm install                              # ✅ Issue #1
supabase db push --dry-run                # ✅ Issue #2
gh workflow run ci.yml && sleep 30s       # ✅ Issue #3 (or check GitHub Actions UI)

# Verify both observability tasks:
curl http://localhost:3000/api/test-error # ✅ Issue #5 (check Sentry)
# Fire PostHog event manually              # ✅ Issue #6 (check PostHog)
```

---

## 📋 Day 1 Summary

| Task | Status | Owner | Time | Issue |
|------|--------|-------|------|-------|
| Monorepo boots | ✅ | Full-Stack | 2h | #1 |
| Supabase linked | ✅ | DevOps | 3h | #2 |
| GitHub Actions | ✅ | DevOps | 4h | #3 |
| Sentry integrated | ✅ | Full-Stack | 2.5h | #5 |
| PostHog integrated | ✅ | Full-Stack | 2h | #6 |

**Total Time: ~13.5 hours across 2 engineers**  
**All critical path items ✅ unblock Days 2–5**

---

## 🚀 Day 2–5 Tasks

After Day 1, proceed with:

- **Day 2:** Vercel setup + Docker setup (Issues #4, #7)
- **Day 3:** Documentation (Issues #8, #9)
- **Day 4:** Phase 1 planning (Issues #10, #11)
- **Day 5:** Sign-off (Issue #12)

See [02_EXECUTION_PLAN.md](02_EXECUTION_PLAN.md) for full timeline.

---

**Status:** 🟢 Ready to execute Day 1  
**Start Time:** Tomorrow 9 AM  
**Next Sync:** EOD Day 1 standup at 4:30 PM
