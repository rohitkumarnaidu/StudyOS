# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# StudyOS — Missing Features & Systems

**Context:** The repository contains specifications and AI-development skills only. Unless noted, every item below is **missing from this workspace** as implementable software.

---

## 1. Entire application surface (P0 per docs)

Per `ROADMAP.md` MVP and `APP_MAP.md` section 1.1, the following **do not exist as code** here:

- Authentication UI and flows (email, Google, phone OTP, magic link).  
- Onboarding (exam profile, date, chapter self-assessment).  
- Dashboard (rings, today’s focus, countdown, streak).  
- Syllabus navigator and **chapter checklist** with optimistic updates and virtualization.  
- AI chat panel with streaming, history sync, and chapter context.  
- Settings (LLM providers, notifications, i18n, privacy actions).  
- Routing, app shell, bottom navigation, error boundaries, loading skeletons.

---

## 2. Backend and database

Missing entirely in-repo:

- Supabase project configuration, `config.toml`, seed scripts.  
- **All** SQL migrations (`001`–`009` groups described in docs).  
- Row Level Security policies and automated RLS tests.  
- Database functions (`get_chapter_completion_pct`, streak helpers, weak chapters, etc.).  
- Edge Functions source and deployment wiring.  
- Webhook handlers (Razorpay) and cron schedulers (WhatsApp, rollups).

---

## 3. Offline, sync, and PWA

Specified in `ROADMAP.md` / prompts but absent:

- Dexie schema, sync queue, conflict rules, background sync.  
- `vite-plugin-pwa` / Workbox configuration, install prompt UX.  
- Service worker strategies (cache-first vs network-first per asset class).

---

## 4. AI and agents

Missing:

- `llm-router.ts`, provider adapters, retry/fallback implementation.  
- LangGraph graphs, tool registry, Zod-validated outputs.  
- RAG pipeline: chunking NCERT, embedding jobs, pgvector queries, reranking.  
- LangSmith (or equivalent) instrumentation in code.

---

## 5. Content and assessment systems

Missing:

- Seeded **syllabus JSON** in a machine-ingestible repo artifact (the human-readable `NEET_2026_Complete_Syllabus_Guide.md` exists; **structured seed data** for DB does not).  
- PYQ question bank and import pipeline.  
- Quiz session engine, timers, mistake log, spaced repetition (SM-2).  
- Full mock test (180Q / 3h) and OMR-style UI.

---

## 6. Integrations

Missing (no integration code, secrets, or OAuth clients in tree):

- Google Drive MCP / OAuth flows.  
- NotebookLM export generators (markdown/ZIP) as implemented modules.  
- WhatsApp / Twilio schedulers and template management.  
- YouTube API client and curated channel configuration in code.  
- Razorpay / Stripe checkout and subscription lifecycle.  
- FCM device token registration and push sending.  
- Notion MCP usage **inside** a web app (docs show patterns; no app to host them).

---

## 7. B2B and multi-tenant (P1–P2)

Missing:

- Teacher dashboard, class heatmaps, assignments, messaging.  
- Institute admin, white-label, per-seat billing UI and APIs.  
- CSV bulk import, batch management.

---

## 8. Observability and quality

Missing:

- PostHog wiring, event catalog enforcement in TypeScript, funnels.  
- Sentry DSN integration, release health.  
- CI/CD (`ci.yml` referenced in MASTER tree only).  
- Unit, component, and E2E tests (Vitest, Testing Library, Playwright).

---

## 9. Broken or incomplete “flows” (process / doc level)

- **Roadmap checkboxes vs repo:** MVP items marked `[✅]` in `ROADMAP.md` cannot be validated against this tree — creates a **broken governance flow** (status unclear for contributors).  
- **Stack ambiguity:** Next vs Vite — **broken consistency** for anyone scaffolding from different docs.

---

## 10. Claude skills packaging

- `skills-claude/*.skill` files are present but **binary** in this environment; without extraction tooling, their exact instructions are not auditable from the repo alone.

---

*Missing-items list is prioritized from `STUDYOS/plan/ROADMAP.md` MVP/v1/v2 sections and `STUDYOS/plan/APP_MAP.md`. **UPDATE (May 2026):** Naming drift resolved with SKILL_DATABASE.md creation + PRODUCT_FOLDER_INVENTORY.md completion.*
