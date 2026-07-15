# StudyOS — DevOps Plan

**Scope:** environments, CI/CD, secrets, migrations, monitoring, incident response.  
**Hosts:** Vercel + Supabase + Upstash + Cloudflare (+ Inngest).

---

## 1. Environments

| Env | Vercel | Supabase | Purpose |
|-----|--------|----------|---------|
| `development` | local `next dev` | `supabase start` or shared dev project | feature dev |
| `preview` | per-PR preview | **staging** project (preferred) or branch DB | review |
| `staging` | `staging` branch | staging | QA, E2E |
| `production` | `main` | production | users |

**Why separate Supabase projects:** migration mistakes do not destroy production; RLS tests run freely.

---

## 2. Secrets management

| Secret type | Store |
|-------------|-------|
| Supabase service role | Vercel **server** env + Inngest env only |
| Razorpay secret | Edge Function + workers only |
| LLM platform keys | Vercel **server** + workers; rotate quarterly |
| PostHog/Sentry | Client keys public; server keys restricted |
| Upstash | Server only |

**Rotation:** runbook entry; use **versioned** secret names in Vercel when rotating without downtime.

---

## 3. CI/CD pipeline (GitHub Actions)

**On PR**

- `pnpm install --frozen-lockfile`  
- `turbo run lint typecheck test --filter=[HEAD^1]`  
- `supabase db lint` (if available) + **sqlfluff** or similar on `migrations/`  
- **Preview** deploy Vercel; comment URL on PR.

**On merge to `main`**

- Migrations: `supabase db push` to **production** with manual approval gate (GitHub Environment) OR automated after staging soak.  
- **Sentry release** + source maps upload.  
- **Tag** `web@x.y.z` optional.

**Why manual gate early:** prevents irreversible schema mistakes; automate after confidence.

---

## 4. Database migrations

- **Trunk-based** forward migrations only.  
- **Breaking changes:** expand → migrate → contract pattern.  
- **RLS tests** in CI: `pgTAP` or scripted `psql` with role switching.

---

## 5. Observability hooks

- **Sentry:** performance traces sample rate 10% production (tune).  
- **Vercel:** deployment annotations.  
- **PostHog:** feature flags for risky features.  
- **LangSmith:** project per environment.

---

## 6. Incident response (lightweight)

| Severity | Example | Action |
|----------|---------|--------|
| SEV1 | auth broken, data leak suspected | freeze deploys, rollback Vercel, revoke tokens if needed |
| SEV2 | AI down | enable fallback model; banner in app |
| SEV3 | elevated 5xx | scale workers; investigate DB locks |

**Communication:** internal Slack + status page (optional Phase 2).

---

## 7. Backups & DR

- Supabase **PITR** on production Pro.  
- **Quarterly restore drill** to staging.  
- Storage: lifecycle rules for temp exports bucket.

---

## 8. Performance budgets

- Define **LCP, TTFB, API p95** SLOs in `ENTERPRISE_ARCHITECTURE.md`; block release if regression > 10% on critical pages (manual until automated).

---

## 9. Dependency hygiene

- **Renovate** or Dependabot weekly; auto-merge patch after green CI.  
- **`pnpm audit`** in CI; critical vulns block merge.

---

## 10. Local developer experience

- `pnpm dev` starts web; `pnpm dev:supabase` optional script.  
- **Seed** small syllabus slice for fast loads; full seed in CI nightly.

---

*Complements `IMPLEMENTATION_PHASES.md`.*
