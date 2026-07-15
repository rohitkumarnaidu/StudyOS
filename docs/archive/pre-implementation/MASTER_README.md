# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# StudyOS — Complete Master Guide
# NEET 2026 AI-Powered Study Platform
# Built for: Your Sister's NEET Re-attempt | Expandable to 2.4M NEET aspirants

---

## WHAT IS STUDYOS?

StudyOS is an enterprise AI study platform that combines:
- Notion-style progress tracking
- NotebookLM-style AI content search (across your 483 PW files)
- Personalized AI tutor (Claude + Gemini + Groq)
- Automated roadmap generation
- Mock test + analytics system
- WhatsApp notifications + PWA on mobile

Built in React + TypeScript + Supabase + LangGraph.
Deployed on Vercel. Works offline. Mobile-first.

---

## YOUR COMPLETE ASSET INVENTORY

### Knowledge Base (ALL CONNECTED)
| Source | Files | Connected To | Status |
|--------|-------|-------------|--------|
| GitHub: rohitkumarnaidu/NEET-NOTES | 483 PW PDFs | Claude Project | ✅ Live |
| Google Drive | 7 folders, 483 files | Notion (ZIP import), NotebookLM | ✅ Live |
| NotebookLM | All 483 files | Via Drive link | ✅ Live |
| Notion NEET workspace | Study tracker | Claude via MCP | ✅ Connected |
| Claude Project | Formula Charts + Short Notes | GitHub sync | ✅ Active |

### Study Materials by Folder
| Folder | Content | Best Tool | Priority |
|--------|---------|-----------|----------|
| NCERT CHAPTER WISE | Core chapter PDFs | Claude Project + NotebookLM | P0 |
| FORMULA CHARTS | All formulas | Claude Project (upload directly) | P0 |
| SHORT NOTE | Quick revision | Claude Project (upload directly) | P0 |
| CHAPTERWISE PYQ | PYQ by chapter | NotebookLM + PYQ Analyzer | P1 |
| NEET PYQ | Full past papers | NotebookLM + PYQ Analyzer | P1 |
| BOARDS PYQ | Board level papers | NotebookLM | P2 |
| MIND MAPS | Visual summaries | NotebookLM | P2 |

### Claude Skills (5 Built + Packaged)
| Skill | Trigger | Purpose |
|-------|---------|---------|
| neet-concept-explainer | "explain [topic]" | 5-layer explanation from PW notes |
| neet-test-generator | "test me on [topic]" | NEET MCQs with +4/-1 marking |
| neet-result-analyzer | "analyze my result" | Analytics + rank estimator |
| neet-tricks-vault | "tricks for [chapter]" | Mnemonics + cheatcodes + traps |
| neet-revision-scheduler | "study plan" | Spaced repetition scheduler |

### App Skill Files (6 Built for Cursor/Claude/Windsurf)
| File | Purpose |
|------|---------|
| SKILL_NEET_DOMAIN.md | NEET domain knowledge for AI code generation |
| SKILL_DESIGN.md | Design system tokens + component patterns |
| SKILL_FRONTEND.md | React/TS patterns + project structure |
| SKILL_BACKEND.md | Supabase + Edge Functions patterns |
| SKILL_AGENTS.md | LangGraph agents + LLM router patterns |
| SKILL_ANALYTICS.md | Event catalog + PostHog patterns |
| SKILL_SECURITY.md | API key security + RLS + XSS prevention |

---

## STUDYOS APP — COMPLETE FILE STRUCTURE

```
studyos/
├── skills/                          ← AI coding assistant skills
│   ├── SKILL_NEET_DOMAIN.md
│   ├── SKILL_DESIGN.md
│   ├── SKILL_FRONTEND.md
│   ├── SKILL_BACKEND.md
│   ├── SKILL_AGENTS.md
│   ├── SKILL_ANALYTICS.md
│   └── SKILL_SECURITY.md
│
├── supabase/
│   ├── migrations/
│   │   ├── 001_auth_and_users.sql
│   │   ├── 002_syllabus.sql
│   │   ├── 003_progress.sql
│   │   ├── 004_notes.sql
│   │   ├── 005_roadmap.sql
│   │   ├── 006_quiz_and_questions.sql
│   │   ├── 007_chat.sql
│   │   ├── 008_analytics.sql
│   │   └── 009_payments.sql
│   └── functions/
│       ├── roadmap-generator/
│       ├── note-extractor/
│       ├── quiz-generator/
│       ├── whatsapp-scheduler/
│       ├── razorpay-webhook/
│       ├── fcm-push-sender/
│       ├── ncert-indexer/
│       └── weekly-analytics-rollup/
│
├── src/
│   ├── app/
│   │   ├── routes.tsx
│   │   ├── providers.tsx
│   │   └── pages/
│   │       ├── Landing.tsx          ← P0: First thing sister sees
│   │       ├── Auth.tsx             ← P0: Google OAuth + Phone OTP
│   │       ├── Onboarding.tsx       ← P0: Quick chapter assessment
│   │       ├── Dashboard.tsx        ← P0: Today's plan + progress rings
│   │       ├── Syllabus.tsx         ← P0: 79 chapters checklist
│   │       ├── Chapter.tsx          ← P0: Subtopic checklist + AI chat
│   │       ├── Quiz.tsx             ← P0: Test generator + grader
│   │       ├── Analytics.tsx        ← P1: Performance dashboard
│   │       ├── Notes.tsx            ← P1: Upload PW notes + OCR
│   │       ├── Roadmap.tsx          ← P1: Weekly study plan
│   │       └── Settings.tsx         ← P1: LLM keys + notifications
│   │
│   ├── components/
│   │   ├── ui/                      ← shadcn/ui (don't modify)
│   │   └── app/
│   │       ├── layout/              ← AppShell, BottomNav, TopBar
│   │       ├── checklist/           ← ChapterChecklist, SubtopicItem
│   │       ├── chat/                ← LLMChatPanel, MessageBubble
│   │       ├── notes/               ← NoteUploadFlow, NoteEditor
│   │       ├── quiz/                ← QuizSession, QuestionCard, Timer
│   │       ├── analytics/           ← ScoreChart, WeakTopicsTable
│   │       └── roadmap/             ← WeekCard, UrgencyBanner
│   │
│   ├── lib/
│   │   ├── supabase.ts              ← Supabase client
│   │   ├── llm-router.ts            ← Multi-provider LLM router
│   │   ├── key-store.ts             ← Encrypted API key storage (Dexie)
│   │   ├── analytics.ts             ← PostHog event tracking
│   │   └── neet-data.ts             ← NEET syllabus JSON + tier data
│   │
│   ├── agents/                      ← LangGraph agents
│   │   ├── tutor-agent.ts           ← NCERT-grounded Q&A
│   │   ├── roadmap-agent.ts         ← Weekly plan generator
│   │   ├── quiz-agent.ts            ← NEET MCQ generator
│   │   ├── weak-area-agent.ts       ← Behavioral analysis
│   │   └── motivation-agent.ts      ← Daily message
│   │
│   ├── hooks/                       ← Custom React hooks
│   │   ├── useProgress.ts
│   │   ├── useChat.ts
│   │   ├── useQuiz.ts
│   │   └── useOfflineSync.ts
│   │
│   └── stores/                      ← Zustand stores
│       ├── auth.store.ts
│       ├── study.store.ts
│       └── ui.store.ts
│
├── .github/
│   └── workflows/
│       └── ci.yml                   ← Lint + Test + Deploy pipeline
│
├── public/
│   ├── manifest.json                ← PWA manifest
│   └── icons/                       ← All PWA icon sizes
│
├── APP_MAP.md                        ← Complete feature map
├── ROADMAP.md                        ← 24-week build roadmap
├── APP_PROMPT.prompt                 ← Build prompts for Cursor/Claude
├── NEET_2026_Complete_Syllabus_Guide.md
└── MASTER_README.md                  ← This file
```

---

## HOW EACH AI TOOL CONNECTS IN THE APP

```
                    ┌─────────────────────┐
                    │     StudyOS App      │
                    │   (Next.js / React)  │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌─────────────┐    ┌─────────────────┐   ┌─────────────┐
   │ Claude API  │    │   Notion MCP    │   │ Gemini API  │
   │             │    │                 │   │             │
   │ • Explain   │    │ • PW notes DB   │   │ • Drive files│
   │ • Test gen  │    │ • Mistake log   │   │ • Image OCR │
   │ • Analyze   │◄───┤ • Progress track│   │ • Vision Q&A│
   │ • Roadmap   │    │ • Flashcards    │   │ • Formula   │
   │ • Tricks    │    │                 │   │   photos    │
   └─────────────┘    └─────────────────┘   └─────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌─────────────┐    ┌─────────────────┐   ┌─────────────┐
   │  NotebookLM │    │    Supabase     │   │   GitHub    │
   │  (separate) │    │                 │   │  NEET-NOTES │
   │             │    │ • Scores DB     │   │             │
   │ • All 483   │    │ • User progress │   │ • 483 PDFs  │
   │   PW files  │    │ • Mistake journal│   │ • 7 folders │
   │ • Podcast   │    │ • Auth          │   │ • Source of │
   │   mode      │    │ • Analytics     │   │   truth     │
   └─────────────┘    └─────────────────┘   └─────────────┘
```

---

## BUILD ORDER — EXACTLY WHAT TO DO WHEN

### TODAY (Before writing any code)
1. Fix Claude Project size issue:
   - Go to Claude Project → Files → GitHub
   - Deselect: BOARDS PYQ, CHAPTERWISE PYQ, NEET PYQ, MIND MAPS
   - Keep only: FORMULA CHARTS + SHORT NOTE (a few files each)
   - Result: Project loads fast, Claude answers accurately

2. Save the 5 Claude Skills:
   - Download all .skill files from this conversation
   - Click "Save skill" for each in Claude Project

3. Start studying RIGHT NOW using Claude skills + NotebookLM
   - Don't wait for the app to be built

### Week 1 — MVP Core (Study while building)
**Morning: Sister studies using Claude + NotebookLM**
**Evening: You build:**

Day 1-2:
- [ ] Create GitHub repo: studyos (separate from NEET-NOTES)
- [ ] Init: npm create vite@latest studyos -- --template react-ts
- [ ] Install: shadcn/ui, Tailwind, Supabase, Dexie, Zustand, React Query
- [ ] Copy all 7 SKILL_*.md files into /skills/ directory
- [ ] Run Supabase migration 001 (auth + users)
- [ ] Run Supabase migration 002 (syllabus with 79 chapters seeded)

Day 3-4:
- [ ] Auth page (Google OAuth + Phone OTP via Supabase)
- [ ] Onboarding flow (exam selection + chapter assessment)
- [ ] Dashboard skeleton (progress rings, today's plan, countdown)

Day 5-7:
- [ ] Chapter checklist (subtopic checkboxes, offline via Dexie)
- [ ] AI Chat panel (Claude API streaming, chapter context)
- [ ] Deploy to Vercel → give sister access to test

### Week 2 — Test Generator + Analytics
- [ ] Quiz page: Subject → Chapter → Type → Generate → Grade
- [ ] Claude API quiz generation using neet-test-generator skill workflow
- [ ] Score saved to Supabase
- [ ] Analytics dashboard: score trend, accuracy, weak topics
- [ ] Notion MCP integration: wrong answers auto-logged to Notion mistake journal

### Week 3 — PYQ Analyzer + Spaced Repetition
- [ ] PYQ analyzer: Claude reads all PYQ folders from GitHub
- [ ] Finds: which topics appear every year across all 3 PYQ folders
- [ ] Spaced repetition scheduler: Day 1, 3, 7, 14, 30 revision reminders
- [ ] PWA setup: installable on sister's phone

### Week 4 — Multi-AI + Polish
- [ ] Add Gemini API for Drive files + photo questions
- [ ] Camera input: sister photographs textbook → Gemini reads → Claude explains
- [ ] WhatsApp daily reminder (what to study today)
- [ ] Full 180-question NEET mock with timer and OMR-style UI

---

## KEY INTEGRATION CODE SNIPPETS

### Claude API with Notion MCP (main pattern)
```javascript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    system: `You are a NEET 2026 expert coach. 
    Student's weak areas from Notion: {weak_areas}
    Current chapter: {chapter_name}
    Always cite which PW material you're drawing from.`,
    messages: [{ role: "user", content: userQuestion }],
    mcp_servers: [{
      type: "url",
      url: "https://mcp.notion.com/mcp",
      name: "notion-mcp"
    }]
  })
});
```

### Gemini API for Drive/Image Questions
```javascript
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });

// For image questions (sister photographs textbook)
const result = await model.generateContent([
  { inlineData: { mimeType: "image/jpeg", data: base64Image } },
  "Identify the NEET chapter this belongs to and explain the concept shown."
]);
```

### LLM Router (use cheapest that works)
```typescript
const MODEL_ROUTING = {
  simple_explain: { provider: 'groq', model: 'llama-3.3-70b' },    // fast + free
  complex_reason: { provider: 'anthropic', model: 'claude-sonnet-4-6' }, // accurate
  roadmap_gen:    { provider: 'anthropic', model: 'claude-sonnet-4-6' }, // structured
  image_ocr:      { provider: 'google',    model: 'gemini-1.5-pro' },   // vision
  quiz_gen:       { provider: 'groq',      model: 'llama-3.3-70b' },    // fast
};
```

---

## PYQ PATTERN ANALYSIS — RUN THIS FIRST

Before anything else, run this Claude prompt against your 3 PYQ folders:

```
From the uploaded NEET PYQ, CHAPTERWISE PYQ, and BOARDS PYQ files:

1. List the top 20 topics that appear EVERY year (2019-2025) in NEET
2. For each topic: which chapter, which subject, average questions per year
3. List topics that appeared in 2024 AND 2025 papers (hot for 2026)
4. For Biology: which organisms/processes appear most in MCQs
5. For Chemistry: which reactions appear most (with reagents)
6. For Physics: which formula applications appear most

Output as a priority table: Topic | Chapter | Avg Qs/year | 2026 Prediction
```

This analysis = your sister's personalized syllabus priority list.

---

## WHAT YOUR SISTER NEEDS EVERY DAY

### Morning (6 AM — WhatsApp notification)
```
Good morning! Today's NEET plan:
📚 Study: Electrochemistry (Chemistry)
🔄 Revise: Ray Optics (studied 7 days ago)  
🎯 Quick test: 10 MCQs on Genetics (weak area)
⏰ Exam: 287 days away
🔥 Streak: Day 14 — keep going!
```

### Study Session Flow
1. Open app → See today's chapter
2. Work through subtopic checklist
3. Stuck? → "Ask AI" → Claude explains from PW notes
4. Done → 15 MCQ quick test
5. Results → Logged to Supabase + Notion

### End of Day
- Spaced repetition: "Revise these tomorrow: [chapters]"
- Score update: "+32 marks from today's test"
- Motivation: AI-generated personalized message

---

## IMPORTANT REMINDERS

### For the App
- Mobile-first ALWAYS (sister uses phone, not laptop)
- Keep it SIMPLE — she's stressed about NEET, not impressed by features
- Warm, encouraging UI — not clinical/corporate
- Every wrong answer is a learning opportunity, not a failure
- Telugu/Tamil language support matters — add i18n from day 1

### For NEET Prep Strategy
- Biology = 50% of marks. If sister is weak here, fix this FIRST
- PYQ analysis > anything else for score improvement
- Spaced repetition is scientifically proven — don't skip it
- Full mock tests under exam conditions = most important practice
- NEET 2026 = first Sunday of May 2026 (~287 days away)

### For the Tech Build
- Read SKILL_*.md files BEFORE writing any code (put in /skills/ in repo)
- Supabase free tier works until ~200 users, then $25/mo
- Never store LLM API keys in database — Dexie.js encrypted local only
- pgvector for NCERT RAG = biggest AI quality improvement
- LangSmith tracing from day 1 = save hours of debugging

---

## LINKS REFERENCE

| Resource | URL |
|---------|-----|
| GitHub NEET-NOTES | https://github.com/rohitkumarnaidu/NEET-NOTES |
| Notion NEET workspace | https://www.notion.so/NEET-35f72717d95680f88d80d867cb233da4 |
| Google Drive | https://drive.google.com/drive/folders/1ZnCWsSZsz5urgyigfoJhhcr1ae-UpxDV |
| NotebookLM | https://notebooklm.google.com/notebook/37462bcc-2451-42fb-a2a4-78b8d032547d |
| Claude Project | claude.ai/project/019e1e0f-cbca-7297-b991-635273470e32 |
| 21st.dev agents | https://21st.dev |
| Supabase | https://supabase.com |
| Vercel | https://vercel.com |
| LangSmith | https://smith.langchain.com |
| Razorpay | https://razorpay.com |

---

*StudyOS — Built with love for a sister's NEET dream. Expandable to millions.*
*NEET 2026 — She can do it. 💪*
