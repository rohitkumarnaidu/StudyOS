# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# StudyOS — Tech Stack Summary

**Source:** `STUDYOS/plan/ROADMAP.md` (Section 5), `STUDYOS/MASTER_README.md`, `STUDYOS/plan/APP_PROMPT.prompt`, and `STUDYOS/skills-app/SKILL_FRONTEND.md` / `SKILL_BACKEND.md`.

**Note:** This stack is **specified**, not verified by a running project in this workspace.

---

## 1. Frontend

| Layer | Technology |
|-------|------------|
| Language | TypeScript (**strict** mode requested) |
| UI library | React 18 |
| Build / dev | **Vite 5** (canonical); diagram in MASTER_README also mentions Next.js — treat as documentation inconsistency |
| Routing | React Router v6 |
| Styling | Tailwind CSS v3, tailwind-merge, clsx |
| Components | shadcn/ui |
| Motion | Framer Motion |
| State (client) | Zustand |
| State (server) | TanStack Query v5 |
| Offline | Dexie.js (+ optional encryption patterns in SKILL_SECURITY) |
| Markdown / math | react-markdown, remark-gfm, rehype-highlight, KaTeX |
| Sanitization | DOMPurify |
| Files / OCR | Tesseract.js, pdfjs-dist, JSZip |
| PWA | vite-plugin-pwa, Workbox |
| i18n | react-i18next (English, Tamil, Hindi, Telugu — phased) |
| Analytics (client) | posthog-js |
| Errors (client) | Sentry |
| Payments (client) | Razorpay; Stripe for international (per ROADMAP) |
| Testing | Vitest, Testing Library, Playwright |

---

## 2. Backend and database

| Concern | Technology |
|---------|------------|
| Primary backend | **Supabase** — PostgreSQL 15, Auth, Storage, Realtime |
| Serverless compute | **Supabase Edge Functions** (Deno) |
| DB extensions (planned) | pgvector, pg_cron, moddatetime, uuid-ossp |
| Cache / rate limits | **Upstash Redis** |
| Push | Firebase Cloud Messaging (Firebase Admin from Edge Functions) |

---

## 3. AI / ML

| Concern | Technology |
|---------|------------|
| Agent framework | LangChain.js + **LangGraph** |
| Models (examples in docs) | Anthropic Claude, OpenAI GPT-4o family, Google Gemini, Groq Llama, local Ollama |
| Embeddings (examples) | OpenAI `text-embedding-3-small` or Ollama `nomic-embed-text` |
| Observability | **LangSmith** (named), Helicone mentioned as alternative in APP_MAP |
| Token / cost | tiktoken (OpenAI) mentioned in prompts |

---

## 4. Infrastructure and delivery

| Concern | Technology |
|---------|------------|
| Frontend hosting | **Vercel** (previews, HTTPS, env per environment) |
| DB / auth hosting | Supabase cloud (local `supabase start` for dev) |
| Static / NCERT CDN | Cloudflare (optional layer in roadmap) |
| CI/CD | GitHub Actions (lint, typecheck, tests, migrations — specified in ROADMAP) |
| Uptime | Uptime Robot (named) |
| Logs (optional) | Axiom (named for Edge Functions) |

---

## 5. Third-party integrations (named in docs)

- Google (Drive OAuth, Gemini, YouTube Data API v3)  
- Meta / Twilio for WhatsApp Business API  
- Razorpay + Stripe  
- PostHog; optional Tinybird / ClickHouse for scale analytics  
- Sentry, LangSmith  

---

## 6. Domain and content

- NEET 2026 syllabus and pedagogy: `NEET_2026_Complete_Syllabus_Guide.md` + `SKILL_NEET_DOMAIN.md`  
- External note corpus: GitHub `NEET-NOTES`, Google Drive, NotebookLM (operational, not in-repo)

---

## 7. One-line stack string (for executives)

**“Vite + React + TypeScript on Vercel, Supabase (Postgres/Auth/Storage/Edge) as backend, Dexie for offline, LangGraph + multi-vendor LLMs for AI, pgvector for RAG, Redis for limits/cache, PostHog + Sentry + LangSmith for visibility, Razorpay for India payments.”**

---

*Stack rows above reflect documentation intent; lock versions in `package.json` when the application is initialized.*
