# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# StudyOS Product Folder — Complete Inventory & Status

**Last Updated:** May 14, 2026  
**Path:** `docs/product/`

---

## 📁 Folder Structure

```
docs/product/
├── MASTER_README.md                    ✅ Complete | 483 files inventory
├── plan/
│   ├── APP_MAP.md                      ✅ Complete | Hierarchical platform map
│   ├── APP_PROMPT.prompt               ✅ Complete | AI coding assistant prompt
│   ├── NEET_2026_Complete_Syllabus_Guide.md  ✅ Complete | 79 chapters + 450+ subtopics
│   └── ROADMAP.md                      ✅ Complete | 8-week MVP roadmap
├── skills-app/
│   ├── SKILL_AGENTS.md                 ✅ Complete | LangGraph patterns
│   ├── SKILL_ANALYTICS.md              ✅ Complete | PostHog events catalog
│   ├── SKILL_BACKEND.md                ✅ Complete | Supabase + Edge patterns
│   ├── SKILL_DATABASE.md               ✅ NEW | Migrations + RLS patterns
│   ├── SKILL_DESIGN.md                 ✅ Complete | Color tokens + components
│   ├── SKILL_FRONTEND.md               ✅ Complete | React patterns
│   ├── SKILL_NEET_DOMAIN.md            ✅ Complete | Domain knowledge
│   └── SKILL_SECURITY.md               ✅ Complete | API keys + RLS + XSS
└── skills-claude/                      ✅ 5 Binary .skill packages
    ├── neet-concept-explainer.skill
    ├── neet-result-analyzer.skill
    ├── neet-revision-scheduler.skill
    ├── neet-test-generator.skill
    └── neet-tricks-vault.skill
```

---

## 📊 Content Breakdown

### 1. MASTER_README.md (2000+ lines)
**Purpose:** Central hub — all assets, tools, integrations mapped  
**Key Sections:**
- ✅ What is StudyOS (product overview)
- ✅ Complete asset inventory (483 PDFs, 7 Google Drive folders, Notion)
- ✅ Knowledge base connections (GitHub, Drive, NotebookLM, Claude Project)
- ✅ Claude skills (5 built + packaged)
- ✅ App skills (7 for Cursor/Claude/Windsurf)
- ✅ Complete file structure diagram (src/, supabase/, docker/)
- ✅ Implementation status by page (Landing, Auth, Dashboard, Syllabus, etc.)
- ✅ Database schema diagram
- ✅ API endpoints list
- ✅ Tech stack summary
- ✅ Deployment checklist

**Status:** Comprehensive reference document; foundation for architecture  

---

### 2. plan/ folder (4 files)

#### 2.1 APP_MAP.md (3500+ lines)
**Purpose:** Hierarchical system diagram + full platform architecture  
**Sections:**
- **Legend:** P0/P1/P2 priority, agent markers, integration markers
- **Root:** StudyOS Enterprise Platform (6 major layers)
  1. Frontend Layer (student app + teacher + admin + design system)
  2. Backend Layer (API gateway + auth + core services + AI orchestration)
  3. Data Layer (DB + vectors + storage + cache + analytics)
  4. AI Layer (agent framework + router + RAG + specialists)
  5. Integration Layer (NotebookLM + Drive + WhatsApp + YouTube + NTA)
  6. Observability Layer (monitoring + tracing + analytics)
- **Detail:** Every page, component, agent, API endpoint mapped
- **Personas:** 3 detailed user personas (Arjun, Priya, Rajan)
- **User Journey:** Week 1 → 8 → exam day flows

**Status:** Complete; aligned with FINAL_ARCHITECTURE.md  

---

#### 2.2 ROADMAP.md (2000+ lines)
**Purpose:** MVP → v1 → v2 timeline with metrics  
**Sections:**
- **Quick Reference:** Tech stack table
- **Goals:** 8 primary goals + north star metric (Weekly Active Studiers)
- **Personas:** Detailed user archetypes
- **Timelines:**
  - **MVP (Week 0–2):** Foundation + auth + syllabus
  - **v1.0 (Week 2–8):** Progress + AI tutor + notes
  - **v1.1 (Week 8–12):** Roadmap + quiz + analytics
  - **v2.0 (Post-12w):** Teacher dashboard + institutes + payments
- **Feature priority matrix:** P0/P1/P2 assignments
- **Blocking issues & dependencies**

**Status:** Comprehensive; aligns with IMPLEMENTATION_PHASES.md  

---

#### 2.3 APP_PROMPT.prompt (1500+ lines)
**Purpose:** Master AI coding assistant prompt for Cursor/Claude  
**Sections:**
- System instruction for AI to understand StudyOS context
- Database schema summary
- Component patterns
- API patterns
- Agent patterns
- Style guide
- Common anti-patterns to avoid

**Status:** Complete; reference for developers using AI pair programming  

---

#### 2.4 NEET_2026_Complete_Syllabus_Guide.md (2500+ lines)
**Purpose:** Structured NEET 2026 curriculum reference  
**Sections:**
- **Physics:** 11 chapters × unit breakdown (kinematics, thermodynamics, optics, etc.)
- **Chemistry:** 15 chapters × unit breakdown (periodic table, bonding, equilibrium, etc.)
- **Biology:** 38 chapters × unit breakdown (cell biology, genetics, ecology, etc.)
- **English:** 15 chapters × unit breakdown (grammar, comprehension, essay, etc.)
- **Exam pattern:** 180 MCQs, 720 minutes, 4/−1 marking
- **Tier breakdown:** Which chapters are Tier 1 (high marks), Tier 2, Tier 3

**Status:** Complete curriculum map; linked to database seed data  

---

### 3. skills-app/ folder (8 files)

**Purpose:** Markdown skill guides for AI coding assistants (Cursor, Claude, Windsurf)  
**Usage:** `@SKILL_AGENTS` mentions in Cursor prompts trigger these files

#### 3.1 SKILL_AGENTS.md
**Topics:**
- LangGraph architecture overview (supervisor pattern)
- 6 agents defined (tutor, roadmap, extraction, quiz, weak-area, motivation)
- LLM router rules (provider per task type)
- Model configuration (Claude, Groq, OpenAI, Ollama)
- Unified interface constraints
- Safety measures (prompt injection, hallucination guards)

**Lines:** ~400 | **Completeness:** ✅ Complete  

---

#### 3.2 SKILL_ANALYTICS.md
**Topics:**
- PostHog SDK setup
- Event catalog (type-safe TypeScript)
- Events for every major flow (signup, login, complete-subtopic, ask-ai, quiz, etc.)
- Funnels (onboarding → first study → engagement)
- Cohorts (tier, locale, device, days-since-signup)
- Feature flags for A/B testing

**Lines:** ~300 | **Completeness:** ✅ Complete  

---

#### 3.3 SKILL_BACKEND.md
**Topics:**
- Supabase client setup (anon + admin clients)
- Query patterns (error handling, nested queries, RLS)
- Realtime subscription patterns
- Storage patterns (signed URLs)
- Edge Function patterns (webhooks, cron)
- TypeScript generation from DB

**Lines:** ~350 | **Completeness:** ✅ Complete  

---

#### 3.4 SKILL_DATABASE.md (NEW — JUST CREATED)
**Topics:**
- Supabase setup & environment variables
- 9 migration groups (extensions, core, syllabus, progress, roadmap, quiz, chat, analytics, billing)
- Complete SQL for each group
- RLS policy patterns & testing
- Query patterns (TypeScript + Python)
- Performance & indexing rules
- Backup & disaster recovery
- Common mistakes & how to avoid them

**Lines:** ~600 | **Completeness:** ✅ Complete (NEW)  

---

#### 3.5 SKILL_DESIGN.md
**Topics:**
- Color tokens (brand, subjects, tiers, semantic)
- Typography (headings, body, mono)
- Spacing scale
- Component patterns (Button, Card, Input, etc.)
- Dark mode variables
- Responsive breakpoints (mobile-first)
- Shadow + radius tokens
- Animation speeds

**Lines:** ~280 | **Completeness:** ✅ Complete  

---

#### 3.6 SKILL_FRONTEND.md
**Topics:**
- Project structure (app router, route groups, features, shared)
- Component patterns (compound components, hooks, render props)
- State management (Zustand, TanStack Query)
- Form patterns (React Hook Form + Zod)
- Styling patterns (Tailwind utility combinations)
- Testing patterns (Vitest, Testing Library)
- Common pitfalls & solutions

**Lines:** ~400 | **Completeness:** ✅ Complete  

---

#### 3.7 SKILL_NEET_DOMAIN.md
**Topics:**
- NEET 2026 curriculum overview
- Subject-specific patterns (physics formulas, chemistry reactions, biology concepts)
- Common misconceptions per topic
- Tier recommendations (focus high-weight topics first)
- Study time allocation (Physics 25%, Chemistry 30%, Biology 45%)
- Key integration points with AI (where explanations matter most)

**Lines:** ~350 | **Completeness:** ✅ Complete  

---

#### 3.8 SKILL_SECURITY.md
**Topics:**
- API key security (storage, rotation, BYOK)
- RLS enforcement (policy patterns, test matrix)
- XSS prevention (sanitization, CSP headers)
- CSRF token management
- Rate limiting implementation
- PII handling (scrubbing, encryption)
- Webhook signature verification
- Data classification (public vs PII vs UGC)

**Lines:** ~320 | **Completeness:** ✅ Complete  

---

### 4. skills-claude/ folder (5 binary files)

**Purpose:** Packaged Claude skills (binary `.skill` format)  
**Status:** Present but not text-auditable in this environment

| Skill | Purpose |
|-------|---------|
| **neet-concept-explainer** | "Explain [topic]" → 5-layer explanation from PW notes |
| **neet-test-generator** | "Test me on [topic]" → NEET MCQs with +4/−1 marking |
| **neet-result-analyzer** | "Analyze my result" → Analytics + rank estimator |
| **neet-tricks-vault** | "Tricks for [chapter]" → Mnemonics + shortcuts |
| **neet-revision-scheduler** | "Study plan" → Spaced repetition schedule |

---

## 🔄 Cross-References & Dependencies

```
MASTER_README
├─→ links to NEET_2026_Complete_Syllabus_Guide.md (curriculum)
├─→ links to APP_MAP.md (feature map)
├─→ links to ROADMAP.md (timeline)
└─→ references all skill files

APP_MAP.md
├─→ references SKILL_AGENTS.md (agent architecture)
├─→ references SKILL_DATABASE.md (data schema)
├─→ references SKILL_BACKEND.md (Supabase patterns)
├─→ references SKILL_FRONTEND.md (UI components)
└─→ references SKILL_NEET_DOMAIN.md (curriculum)

ROADMAP.md
├─→ Timeline aligned with IMPLEMENTATION_PHASES.md
├─→ Feature priority maps to GitHub Issues
└─→ Blocking issues documented

Skills
├─→ All skills are **stateless references** (no code yet)
├─→ Used in Cursor/Claude prompts via `@SKILL_*` mentions
└─→ Updated whenever architecture changes
```

---

## ✅ Completeness Audit

| Document | Sections | Completeness | Ready for Dev |
|-----------|----------|-------------|--------------|
| **MASTER_README** | 12 | ✅ 100% | ✅ Yes |
| **APP_MAP** | 10+ | ✅ 100% | ✅ Yes |
| **ROADMAP** | 15+ | ✅ 100% | ✅ Yes |
| **APP_PROMPT** | 8+ | ✅ 100% | ✅ Yes |
| **NEET Syllabus** | 80+ | ✅ 100% | ✅ Yes |
| **SKILL_AGENTS** | 8 | ✅ 100% | ✅ Yes |
| **SKILL_ANALYTICS** | 6 | ✅ 100% | ✅ Yes |
| **SKILL_BACKEND** | 7 | ✅ 100% | ✅ Yes |
| **SKILL_DATABASE** | 7 | ✅ 100% | ✅ Yes (NEW) |
| **SKILL_DESIGN** | 8 | ✅ 100% | ✅ Yes |
| **SKILL_FRONTEND** | 7 | ✅ 100% | ✅ Yes |
| **SKILL_NEET_DOMAIN** | 6 | ✅ 100% | ✅ Yes |
| **SKILL_SECURITY** | 8 | ✅ 100% | ✅ Yes |

---

## 🚀 How to Use This Folder

### For Developers (Phase 0–1)
1. Start with **MASTER_README.md** for context
2. Read **ROADMAP.md** to understand timeline
3. Open **APP_MAP.md** for detailed feature breakdown
4. Use **SKILL_*** files in Cursor/Claude:
   ```
   In Cursor Composer:
   "I'm building the auth page. @SKILL_FRONTEND @SKILL_BACKEND @SKILL_SECURITY"
   ```

### For AI Coding Assistants
- Reference **APP_PROMPT.prompt** as system instruction
- Tag specific skills: `@SKILL_AGENTS` for agent code, `@SKILL_DATABASE` for migrations, etc.
- All skills are meant to be **stateless references** (context, not code templates)

### For Product Managers
- **ROADMAP.md** = timeline + metrics
- **APP_MAP.md** = feature tree + priorities
- **NEET_2026_Complete_Syllabus_Guide.md** = curriculum reference

### For QA / Testing
- **MASTER_README.md** § Implementation status shows what's testable
- **ROADMAP.md** § User journeys define test scenarios
- **SKILL_SECURITY.md** § Security checklist

---

## 📋 Current Status (May 2026)

| Category | Status |
|----------|--------|
| **Product specs** | ✅ Complete |
| **Architecture docs** | ✅ Complete |
| **Skill files** | ✅ Complete (8/8 + all skills created) |
| **Curriculum reference** | ✅ Complete (all 79 chapters) |
| **Implementation code** | ⏳ 0% (ready to start Phase 0) |
| **Database migrations** | ⏳ 8/9 begun (ready for Phase 1) |
| **Frontend framework** | ✅ Scaffolded (Next.js 15 ready) |
| **Backend framework** | ✅ Scaffolded (FastAPI ready) |

---

## 🎯 Next Steps

1. ✅ **Review** all product docs with team
2. ✅ **Create GitHub Issues** for each Phase 0–1 task
3. ⏳ **Begin Phase 0** (Week 1): DevOps + CI/CD
4. ⏳ **Begin Phase 1** (Week 1–3): Auth + Syllabus
5. ⏳ Use **SKILL_*** files in daily development

---

**Summary:** Product folder is **100% complete** with comprehensive specifications, skill guides, and curriculum reference. Ready for development team to execute IMPLEMENTATION_ROADMAP.md.
