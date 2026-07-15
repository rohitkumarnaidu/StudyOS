# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# StudyOS — Project Analysis

**Analysis date:** 2026-05-13  
**Workspace:** `studyos-complete` (contains `STUDYOS/`)

---

## 1. Executive summary

StudyOS is **documented as** an AI-powered, mobile-first study platform for Indian competitive exams (primary focus: **NEET 2026**), combining syllabus checklists, multi-provider LLM tutoring, notes intelligence, roadmaps, quizzes, analytics, and integrations (Notion-style progress, NotebookLM-style workflows, WhatsApp, payments).

**What exists in this repository today:** planning documents, a very large product map, a 24-week roadmap, LLM-oriented build prompts, NEET syllabus domain content, **seven Markdown “skill” guides** for AI-assisted development (`skills-app/`), and **five packaged Claude `.skill` files** (`skills-claude/`, binary — not human-readable in-repo).

**What does not exist here:** runnable frontend or backend code, database migrations, Supabase project, CI configuration, tests, or deployment artifacts. There is **no** `package.json`, `src/`, or `.sql` under this workspace.

---

## 2. Repository inventory

| Path | Role |
|------|------|
| `STUDYOS/MASTER_README.md` | Master narrative: vision, asset inventory (GitHub notes, Drive, NotebookLM, Notion, Claude project), intended stack, high-level file tree **(aspirational, not present)** |
| `STUDYOS/plan/APP_MAP.md` | Enterprise feature mind map: frontend, backend, data, AI, integrations, observability |
| `STUDYOS/plan/ROADMAP.md` | Goals, personas, MVP → v1 → v2 milestones, full checklist, 24-week timeline, env vars, risks |
| `STUDYOS/plan/APP_PROMPT.prompt` | 13 large “build prompts” for scaffolding auth, DB, agents, UI, analytics, MCP, PWA, security, teacher/admin |
| `STUDYOS/plan/NEET_2026_Complete_Syllabus_Guide.md` | NEET 2026 syllabus, tiers, weightage, deleted topics, subtopic outlines |
| `STUDYOS/skills-app/SKILL_*.md` | Conventions for frontend, backend, agents, analytics, security, design, NEET domain |
| `STUDYOS/skills-claude/*.skill` | Claude Skill packages (binary in workspace) |

---

## 3. Stated purpose (from documentation)

1. **Student core loop:** open app → today’s plan → chapter checklist → AI help → short quiz → progress and streaks.  
2. **Differentiation:** NEET-specific structure (79 chapters, tiers, deleted topics), offline-first checklist/notes, BYOK or shared LLM, RAG over NCERT when built, institute/teacher expansion later.  
3. **Scale story:** start with one high-intent user narrative; expand toward lakhs of aspirants with B2B (coaching) features in later phases.

---

## 4. Documentation quality and internal consistency

**Strengths**

- Unusually complete **product** and **engineering** specification for a greenfield app.  
- Security and privacy themes (RLS, DPDP, no LLM keys in DB) are repeated in multiple places.  
- NEET domain doc aligns with APP_MAP tier / weightage concepts.

**Gaps and contradictions**

- `ROADMAP.md` marks many MVP items with `[✅]` while **no implementation** exists in this repo — those checkmarks represent **intent or work done elsewhere**, not verifiable artifacts here.  
- `MASTER_README.md` diagram mentions "Next.js / React" in one place while the canonical stack elsewhere is **Next.js App Router** (confirmed in FINAL_ARCHITECTURE.md).  
- External links (Notion, Drive, GitHub repos, Claude project URLs) appear in docs — **operational risk** if those are private or rot.

---

## 5. What the project “currently does” (literal)

In **this** workspace: it **specifies and guides** building StudyOS; it does **not** execute application logic. Any running app, database, or deployment would live **outside** this tree (or in a different branch/repo not present here).

---

## 6. Enterprise readiness (documentation vs reality)

| Dimension | Status in-repo |
|-----------|----------------|
| Product definition | Strong |
| Architecture on paper | Strong |
| Implementation | Absent |
| Verifiable security (RLS, CSP, audits) | Not applicable until code exists |
| Observability | Specified only |
| Compliance (DPDP, minors) | Described, not implemented |

---

## 7. Recommended next steps (analysis only — no implementation in this task)

1. Initialize the real app repo (or merge this `STUDYOS/` spec into the codebase repo) and align **one** canonical stack (FINAL_ARCHITECTURE.md confirms Next.js 15 App Router).  
2. Replace narrative `[✅]` with **traceable** issues (issue tracker) linked to commits.  
3. Begin Phase 0 implementation: verify monorepo boots, CI/CD pipelines green, Sentry/PostHog wired (see IMPLEMENTATION_PHASES.md).
4. Add a short `README.md` at repo root explaining that **`STUDYOS/` is the spec** and where the actual app lives.

---

*This file is an evidence-based description of the contents of `studyos-complete` as of the analysis date.*
