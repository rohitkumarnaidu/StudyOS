# StudyOS — Development Phases (Engineering Workflow)

**Companion to:** `IMPLEMENTATION_PHASES.md` (what to build) and `IMPLEMENTATION_ROADMAP.md` (product waves).
**Focus:** **how** teams work—cadence, quality gates, branching, and definitions of done.

---

## 1. Cadence model

| Horizon | Artifact |
|---------|----------|
| Quarterly | OKRs aligned to Waves A–G |
| Monthly | Architecture review + AI cost review |
| Bi-weekly | Sprint goals mapped to roadmap steps |
| Daily | Stand-down (async) + incident sync if active SEV |

---

## 2. Branching strategy (trunk-based)

- **`main`:** always deployable to **staging**; protected.
- **Short-lived branches:** `feat/*`, `fix/*` ≤ 3 days ideal.
- **PR requirements:** 1 approval + green CI + **RLS impact checklist** if DB touched.
- **Release:** tag or Vercel promote staging → production.

**Why trunk-based:** reduces merge pain in monorepo with shared packages.

---

## 3. Definition of Ready (DoR)

- User story + acceptance criteria.
- **Data model** sketched (ERD snippet in PR).
- **Security notes:** PII? new webhook? new vendor? new Storage bucket?
- **Feature flag** name chosen if risky.
- **AI prompt** versioned if new agent/tool.

---

## 4. Definition of Done (DoD)

- Unit tests for domain logic; component tests for complex UI; Playwright for **one** happy path per feature slice.
- **Telemetry:** PostHog events added/updated.
- **Docs:** README or ADR if behavior is non-obvious.
- **Accessibility:** keyboard path exists for primary flow.
- **Rollback:** flag or migration strategy documented in PR.
- **PDF pipeline:** processing tested with at least 3 sample files (text, scanned, mindmap).

---

## 5. Quality gates in CI

1. Lint + typecheck + unit tests.
2. **SQL migration** dry-run on ephemeral DB.
3. **Bundle analysis** optional weekly (not every PR).
4. **Secret scan** (gitleaks).
5. Preview URL smoke: login + home (Playwright against preview).
6. **Python:** ruff + mypy + pytest (excluding integration markers).

---

## 6. Local environment standards

- Node **20 LTS** or **22** (pick one org-wide).
- Python **3.12+** for FastAPI.
- `corepack enable` + `pnpm`.
- **Format:** Prettier (TS) + Ruff format (Python).
- **Lint:** ESLint + typescript-eslint strict; Ruff lint.
- **Git hooks:** lefthook or husky for lint-staged.

---

## 7. Code review rubric (short)

- **Correctness:** types, nullability, error paths.
- **Security:** RLS, headers, user input handling, file upload validation.
- **Performance:** N+1 queries, unbounded lists, bundle impact.
- **Maintainability:** package boundaries respected.
- **AI quality:** prompt versioned, output validated with Zod, LangSmith trace link.

---

## 8. On-call (lightweight early stage)

- Not 24/7 until launch traffic; still define **owner rotation** weekly post-launch.
- Runbooks in `DEVOPS_PLAN.md` linked from wiki.

---

## 9. AI development workflow

- **Prompt changes** require before/after eval notes in PR.
- **Graph changes** include LangSmith trace link from staging test.
- **Cost estimate** rough tokens appended for new tools.
- **PDF processor changes** tested against sample corpus (text + scanned + mindmap).
- **Embedding changes** require re-index run on staging; verify search quality.

---

## 10. Documentation discipline

- **Product source of truth:** `docs/product/` folder.
- **Engineering source of truth:** `FINAL_ARCHITECTURE.md` + this file + ADRs.
- **API contracts:** shared Zod schemas in `packages/` (future).
- **Database:** `DATABASE_SCHEMA_PLAN.md` + `DATABASE_PLAN.md`.

---

## 11. PDF + Mind Map development workflow

- **Sample corpus:** maintain 10 representative PDFs (3 text, 3 scanned, 4 mind maps) in `test/fixtures/pdfs/`.
- **Processing tests:** mock vision model responses; verify structure output schema.
- **Bulk import tests:** simulate 50-file upload; verify progress tracking + error recovery.
- **Search tests:** seed known notes; verify hybrid search returns relevant results.
- **Viewer tests:** Playwright E2E for PDF viewer zoom, page nav, mind map interaction.

---

## 12. Component architecture rules

- **Feature slices:** `src/features/{feature}/` contains components, hooks, API, schema.
- **Shared UI:** `src/shared/components/ui/` — dumb, reusable primitives (Button, Card, Input).
- **Shared logic:** `src/shared/lib/` — pure utilities (cn, toast, apiFetch).
- **No cross-feature imports:** features communicate via API or shared packages only.
- **Server vs client:** Server Components by default; `'use client'` only when interactivity needed.

---

*Feature sequencing: `FEATURE_PRIORITY.md`.*
