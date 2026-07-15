# APP_MAP.md
# StudyOS — Platform Mind Map
# Complete hierarchical map: every system, module, integration, and data flow

```
LEGEND
══════
[🔴 P0]  MVP — must ship first
[🟡 P1]  v1.0 — ship within 6 weeks of MVP
[🟢 P2]  v2.0 — 3 months post-launch
[⭐]     High-impact / flagship feature
[🤖]     AI Agent
[🔗]     External integration
[🛡️]    Security / Auth
[📊]     Analytics
```

---

## ROOT: StudyOS Platform

```
StudyOS
├── 1. FRONTEND LAYER
│   ├── 1.1 Student App (Next.js 16 Web App)
│   └── 1.2 Design System (shared)
│
├── 2. BACKEND LAYER
│   ├── 2.1 API (FastAPI Python 3.12)
│   ├── 2.2 Auth Service (Custom FastAPI + BFF)
│   ├── 2.3 Core Services
│   └── 2.4 AI Integration Layer
│
├── 3. DATA LAYER
│   ├── 3.1 Primary Database (Supabase PostgreSQL)
│   ├── 3.2 Vector Store (pgvector)
│   ├── 3.3 File Storage (Supabase Storage)
│   └── 3.4 Cache (Redis)
│
├── 4. AI / AGENT LAYER
│   ├── 4.1 LLM Router (Multi-provider)
│   ├── 4.2 RAG Pipeline
│   └── 4.3 Specialist Agents
│
├── 5. INTEGRATION LAYER
│   ├── 5.1 Google NotebookLM
│   ├── 5.2 Google Drive
│   └── 5.3 YouTube (video lectures)
│
└── 6. OBSERVABILITY LAYER
    ├── 6.1 Application Monitoring
    ├── 6.2 Student Analytics
    └── 6.3 Business Metrics
```

---

## 1. FRONTEND LAYER

### 1.1 Student App
```
Student App [🔴 P0]
├── Onboarding
│   ├── Welcome Screen [🔴 P0]
│   │   ├── App logo + value proposition
│   │   └── "Which exam?" selector (NEET / JEE Mains / JEE Advanced / Custom)
│   ├── Profile Setup [🔴 P0]
│   │   ├── Name, city
│   │   ├── Exam date picker → weeks-remaining counter
│   │   ├── Class (11 / 12 / Dropper)
│   │   └── Study hours per day selector (4h / 6h / 8h / 10h+)
│   └── Quick Assessment [🔴 P0]
│       ├── Chapter grid → tap to mark "Already studied"
│       ├── Confidence slider per subject (1–5)
│       └── Skip option → defaults to "beginner" roadmap
│
├── Authentication [🔴 P0]
│   ├── Email + Password (primary)
│   ├── Google OAuth (via Supabase)
│   ├── Login / Signup / Forgot Password flows
│   └── Session management (HttpOnly cookies via BFF)
│
├── Dashboard [🔴 P0] ⭐
│   ├── Today's Goal Card
│   │   ├── Personalized greeting
│   │   ├── Chapters to study today (from roadmap)
│   │   └── Streak counter
│   ├── Subject Progress Rings
│   │   ├── Physics ring (% complete)
│   │   ├── Chemistry ring
│   │   ├── Biology ring
│   │   └── Overall readiness score (0–100)
│   ├── Weak Areas Panel
│   │   ├── Top 3 weak chapters
│   │   └── "Quick Revise" shortcut
│   └── Exam Countdown
│       ├── Days remaining
│       └── "X chapters left to cover" stat
│
├── Syllabus Navigator [🔴 P0] ⭐
│   ├── Subject Tabs (Physics / Chemistry / Biology)
│   ├── Chapter List
│   │   ├── Chapter card (name, tier badge, weightage %, progress bar)
│   │   ├── Sort: by tier / by completion / by exam date proximity
│   │   ├── Filter: incomplete / in-progress / complete / deleted topics
│   │   └── Search chapters and topics
│   └── Chapter Detail View [🔴 P0] ⭐
│       ├── Chapter header (name, subject, class, tier, weightage)
│       ├── Overall progress ring
│       ├── Topic Accordion List
│       │   ├── Topic header (checkbox, name, subtopic count, progress)
│       │   └── Subtopic Items
│       │       ├── Checkbox (tap to complete)
│       │       ├── Subtopic name + definition
│       │       ├── "High yield ⭐" badge
│       │       ├── "Deleted ❌" badge with strikethrough
│       │       └── Difficulty tag (Easy / Medium / Hard)
│       ├── Chapter Notes Panel
│       └── "Ask AI about this chapter" button
│
├── AI Chat Interface [🔴 P0] ⭐
│   ├── Chat Panel
│   │   ├── Chapter context injected automatically
│   │   └── Message bubbles (markdown rendered)
│   ├── Smart Suggestions
│   │   ├── "Explain [current subtopic]"
│   │   ├── "Give me 3 NEET MCQs on [topic]"
│   │   └── "What are common mistakes in [topic]?"
│   └── Chat History (per chapter, persistent)
│
├── Note Management [🔴 P0] ⭐
│   ├── Note Upload
│   │   ├── Drag-drop zone (desktop)
│   │   ├── File picker (PDF, JPEG, PNG, WEBP, TXT)
│   │   └── Paste text directly
│   ├── AI Topic Extraction
│   │   ├── Extracted topics list (review before saving)
│   │   ├── Syllabus gap detection
│   │   └── Manual remap
│   ├── Note Editor
│   │   ├── Rich markdown editor
│   │   ├── Chapter/topic tag selector
│   │   └── Auto-save
│   └── Notes Library
│       ├── Filter by subject / chapter / tag
│       └── Search full-text across all notes
│
├── Study Roadmap [🟡 P1] ⭐
│   ├── Roadmap View
│   │   ├── Weekly calendar (horizontal scroll)
│   │   ├── Week cards (collapsible)
│   │   └── Exam readiness score progress
│   └── Roadmap Controls
│       ├── "Regenerate roadmap" button
│       ├── Study hours slider
│       └── Manual chapter reorder
│
├── Mock Test + PYQ Center [🟡 P1] ⭐
│   ├── PYQ Browser
│   │   ├── Filter by year (2015–2025), subject, chapter
│   │   └── Question cards with answer reveal
│   └── Chapter-wise Quiz
│       ├── Select chapter → auto-generate MCQs
│       ├── Timer
│       └── Instant feedback with explanation
│
├── Analytics & Insights [🟡 P1] ⭐
│   ├── Personal Dashboard
│   │   ├── Study time heatmap
│   │   ├── Chapter completion velocity
│   │   └── Predicted NEET score
│   └── Weak Area Analysis
│       ├── Bottom chapters by quiz score
│       └── Spaced repetition due list
│
├── Flashcard System [🟢 P2] ⭐
│   ├── Auto-generated flashcards per subtopic
│   ├── Spaced Repetition (SM-2 algorithm)
│   └── Flip card UI
│
└── Settings
    ├── Profile (name, exam, date, hours)
    ├── Notifications
    ├── Theme (light / dark / sepia / high contrast)
    ├── Language (English / Tamil / Hindi)
    ├── Data & Privacy
    │   ├── Export all my data
    │   └── Delete account + all data
    └── About + Help
```

### 1.2 Design System
```
Design System [🔴 P0]
├── Foundations
│   ├── Color Palette
│   │   ├── Primary: Deep Indigo (#4F46E5)
│   │   ├── Secondary: Emerald (#10B981)
│   │   ├── Warning: Amber (#F59E0B)
│   │   ├── Danger: Rose (#F43F5E)
│   │   └── Subject Colors: Physics #3B82F6, Chemistry #8B5CF6, Biology #10B981
│   ├── Typography
│   │   ├── Font: Inter + Noto Sans Tamil
│   │   └── Scale: 12 / 14 / 16 / 18 / 20 / 24 / 32 / 48px
│   ├── Spacing: 4px grid
│   └── Border Radius: 4 / 8 / 12 / 16 / 24 / full
│
├── Components (@/shared/components/ui/)
│   ├── Button, Input, Checkbox, Badge, Avatar
│   ├── ProgressRing, StatCard, ChapterCard, SubtopicItem
│   ├── Dialog, Tooltip, Popover, Tabs
│   └── AnimatedPage, AnimatedCard (framer-motion)
│
└── Patterns
    ├── Empty States, Error States, Loading States
    ├── Success States (confetti on chapter complete)
    └── Motion: 150ms ease (micro) / 300ms ease-in-out (page)
```

---

## 2. BACKEND LAYER

### 2.1 API (FastAPI)
```
API (FastAPI Python 3.12) [🔴 P0]
├── /v1/auth — Auth endpoints (login, register, refresh, logout)
├── /v1/syllabus — Read-only syllabus data (public, cached)
├── /v1/progress — Student progress CRUD
├── /v1/notes — Note storage + retrieval
├── /v1/roadmap — AI roadmap generation
├── /v1/quiz — Quiz generation + submission
├── /v1/ai/chat — AI chat (SSE streaming)
├── /v1/analytics — Events ingestion
├── /v1/privacy — Data export + deletion
└── Middleware
    ├── Request ID + logging (structlog)
    ├── Rate limiting (SlowAPI)
    ├── Security headers (CSP, HSTS, X-Frame-Options)
    ├── CSRF double-submit cookie
    ├── Audit logging (sensitive paths)
    └── CORS (allowlist: app domains only)
```

### 2.2 Auth Service (BFF Pattern)
```
Auth Service [🔴 P0] [🛡️]
├── Providers
│   ├── Email + Password (Argon2id hashing)
│   └── Google OAuth (via Supabase)
├── Session Management
│   ├── JWT access token (15min)
│   ├── Opaque refresh token (30 days)
│   ├── HttpOnly cookies via BFF (Next.js middleware)
│   └── Multi-device sessions (list + revoke)
├── Security
│   ├── Password: Argon2id, min 8 chars + complexity
│   ├── Rate limit: 5 failed logins → 15min lockout
│   ├── CSP + HSTS headers
│   └── GDPR: right to erasure, data export
└── BFF Pattern
    ├── Next.js middleware verifies JWT
    ├── Silent refresh on token expiry
    ├── Internal proxy to FastAPI (/v1/*)
    └── Cookies: studyos_access, studyos_refresh
```

### 2.3 Core Services
```
Core Services [🔴 P0]
├── Syllabus Service
│   ├── Serves NEET/JEE chapter JSON (versioned)
│   └── Cached via Redis (TTL: 24h)
├── Progress Service
│   ├── Subtopic completion events (idempotent)
│   ├── Progress rollup (subtopic → topic → chapter → subject → overall)
│   └── Streak calculation
├── AI Service
│   ├── Multi-provider (OpenAI, Anthropic, Google, Ollama)
│   ├── FallbackOrchestrator (primary → fallback → error)
│   ├── SSE streaming for chat responses
│   └── Token usage tracking
├── Cache Service
│   ├── Redis with in-memory fallback
│   ├── TTL-based invalidation
│   └── Pattern-based invalidation
└── Upload Security
    ├── Magic-byte validation
    ├── Size limits (50MB max)
    └── MIME type checks
```

### 2.4 AI Agent Orchestration
```
AI Integration [🟡 P1]
├── LLM Router
│   ├── Provider abstraction (OpenAI, Anthropic, Google, Groq, Ollama)
│   ├── Routing by task complexity
│   └── Fallback chain (primary → backup → error)
├── Context Manager
│   ├── Student profile injection
│   ├── Chapter content injection
│   └── Conversation history (sliding window)
└── Output Validator
    ├── Zod schema validation
    ├── Hallucination check (NCERT corpus)
    └── Citation injector
```

---

## 3. DATA LAYER

### 3.1 Primary Database
```
PostgreSQL (Supabase) [🔴 P0]
├── Core Tables
│   ├── profiles (id, user_id, name, exam_type, exam_date, class_level, study_hours, created_at)
│   ├── auth_credentials (id, user_id, email, password_hash, created_at, updated_at)
│   └── refresh_sessions (id, user_id, token_hash, expires_at, revoked_at, created_at)
│
├── Syllabus Tables
│   ├── exam_profiles (id, name, version, published_at, is_active)
│   ├── subjects (id, exam_profile_id, name, question_count, marks, display_order)
│   ├── chapters (id, subject_id, number, name, class, tier, weightage_pct, is_deleted)
│   ├── topics (id, chapter_id, name, display_order, is_high_yield)
│   └── subtopics (id, topic_id, name, definition, is_high_yield, is_deleted, difficulty)
│
├── Progress Tables
│   ├── user_chapter_progress (user_id, chapter_id, pct_complete, last_studied_at, confidence)
│   ├── subtopic_completions (id, user_id, subtopic_id, completed_at, source)
│   └── streaks (user_id, current_streak, longest_streak, last_study_date)
│
├── Notes Tables
│   ├── notes (id, user_id, chapter_id, topic_id, title, content_md, source_type, file_url, created_at)
│   └── note_embeddings (id, note_id, chunk_text, embedding vector(1536), chunk_index)
│
├── Roadmap Tables
│   ├── roadmaps (id, user_id, generated_at, exam_date, readiness_score, is_active)
│   └── week_plans (id, roadmap_id, week_number, start_date, end_date, focus_theme)
│
├── Quiz Tables
│   ├── questions (id, subject_id, chapter_id, question_text, options_json, correct_option, explanation, difficulty)
│   ├── quiz_sessions (id, user_id, chapter_id, started_at, score, total_questions)
│   └── quiz_responses (id, session_id, question_id, selected_option, is_correct)
│
├── Chat Tables
│   ├── chat_sessions (id, user_id, chapter_id, title, llm_provider, model, created_at)
│   └── messages (id, session_id, role, content, tokens_used, created_at)
│
├── Analytics Tables
│   ├── events (id, user_id, event_type, properties_json, created_at)
│   └── ai_token_usage (id, user_id, provider, model, tokens_used, cost, created_at)
│
└── RLS Policies (every table)
    └── Users: own rows only
```

### 3.2 Vector Store
```
Vector Store (pgvector extension) [🟡 P1]
├── NCERT Content Embeddings
│   ├── NCERT chapters chunked (300 tokens each)
│   ├── Embedded with text-embedding-3-small (1536 dims)
│   └── Used by RAG pipeline for AI answers
├── Note Embeddings
│   └── Student notes chunked + embedded for semantic search
└── Question Embeddings
    └── PYQ questions embedded for similarity search
```

### 3.3 File Storage
```
File Storage (Supabase Storage) [🔴 P0]
├── Buckets
│   ├── user-notes (private; RLS: owner only)
│   └── exports (temporary; 24h TTL)
├── Size Limits
│   ├── Image: 10MB max
│   ├── PDF: 20MB max
│   └── Per-user quota: 500MB
└── Security
    ├── Magic-byte validation
    ├── MIME type checks
    └── Signed URLs (15-min expiry)
```

### 3.4 Cache Layer
```
Cache (Redis) [🟡 P1]
├── Cached Data
│   ├── Syllabus JSON (TTL: 24h)
│   ├── User progress summary (TTL: 5min)
│   ├── AI roadmap (TTL: 24h)
│   └── Quiz questions batch (TTL: 1h)
└── Rate Limiting
    └── API rate limits per user (sliding window)
```

---

## 4. AI / AGENT LAYER

### 4.1 LLM Router
```
LLM Router [🔴 P0]
├── Provider Abstraction
│   ├── OpenAI: gpt-4o, gpt-4o-mini
│   ├── Anthropic: claude-sonnet-4, claude-haiku
│   ├── Google: gemini-2.0-flash, gemini-2.5-pro
│   ├── Groq: llama-3.3-70b, mixtral-8x7b
│   └── Ollama: llama3.2, mistral (local)
├── Routing Strategy
│   ├── Simple Q&A → fast/cheap model
│   ├── Roadmap generation → powerful model
│   └── Note extraction → vision model
└── Fallback Chain
    ├── Primary fails → retry → switch to fallback
    └── All fail → show error
```

### 4.2 RAG Pipeline
```
RAG Pipeline [🟡 P1] ⭐
├── Indexing
│   ├── Source: NCERT Class 11+12 PDFs
│   ├── Chunking: 300 tokens with 50-token overlap
│   └── Storage: pgvector in Supabase
├── Retrieval
│   ├── Query embedding generated
│   ├── Cosine similarity search (top 5 chunks)
│   └── Filter by chapter_id
└── Generation
    ├── Context injection: [NCERT chunks] + [student notes]
    ├── System prompt: "Answer only from provided NCERT context"
    └── Citation formatting
```

### 4.3 Specialist Agents
```
Specialist Agents [🟡 P1] ⭐
├── 🤖 Tutor Agent
│   ├── Answer concept questions, explain subtopics
│   ├── Context: chapter data + student notes + NCERT RAG
│   └── Output: markdown with NCERT citations
│
├── 🤖 Roadmap Agent ⭐
│   ├── Generate personalized weekly study plans
│   ├── Context: student profile + progress + exam date
│   └── Output: structured WeekPlan JSON (Zod validated)
│
├── 🤖 Note Extraction Agent
│   ├── Parse uploaded notes → extract topics → map to syllabus
│   └── Output: ExtractionResult JSON (topics + gaps + quality score)
│
├── 🤖 Quiz Generator Agent
│   ├── Generate NEET-style MCQs for any chapter
│   └── Output: array of Question objects (validated format)
│
├── 🤖 Weak Area Detector Agent [🟡 P1]
│   ├── Identify weak chapters based on quiz scores + behavior
│   └── Output: WeakAreaReport (top 5 weak subtopics + action plan)
│
└── 🤖 Daily Motivation Agent [🟡 P1]
    ├── Generate personalized daily message + study tip
    └── Output: DailyMessage (greeting + tip + today's focus)
```

---

## 5. INTEGRATION LAYER

```
Integrations
├── 🔗 Google Drive [🟡 P1]
│   ├── OAuth 2.0 connection
│   ├── Push chapter notes as Google Docs
│   └── Pull Google Docs/PDFs as note sources
│
├── 🔗 NotebookLM Bridge [🟡 P1]
│   ├── Export chapters as NotebookLM-optimized markdown
│   └── Bundle multiple chapters as ZIP
│
└── 🔗 YouTube [🟡 P1]
    ├── Search YouTube for lectures matching current chapter
    ├── Curated playlists
    └── Video timestamps linked to subtopics
```

---

## 6. OBSERVABILITY LAYER

```
Observability [🟡 P1] [📊]
├── Application Monitoring
│   ├── Sentry (error tracking + performance)
│   │   ├── Frontend: JS errors, React component crashes
│   │   ├── Backend: FastAPI errors, DB query failures
│   │   └── Alerts: Slack channel #studyos-alerts
│   └── Vercel Analytics (web vitals: LCP, FID, CLS)
│
├── Student Analytics [🟡 P1] [📊] ⭐
│   ├── Event Tracking (PostHog)
│   │   ├── chapter_opened, subtopic_completed, note_uploaded
│   │   ├── ai_message_sent, roadmap_generated, quiz_attempted
│   │   └── streak_achieved, chapter_completed
│   ├── Funnel Analysis
│   │   └── Signup → Onboarding → First chapter → First subtopic
│   └── Retention Cohorts
│       └── Day 1, Day 7, Day 14, Day 30 retention
│
└── Business Metrics [🟡 P1]
    ├── DAU / WAU / MAU
    ├── New signups per day (by exam type)
    ├── AI token cost per DAU
    └── Feature adoption rates
```

---

## 7. SKILLS & DESIGN DOCUMENTS

```
Skills + Docs (for LLM-assisted development)
├── SKILL_FRONTEND.md — Next.js 16 App Router patterns, Tailwind v4, shadcn/ui
├── SKILL_BACKEND.md — FastAPI patterns, Pydantic models, asyncpg
├── SKILL_DATABASE.md — PostgreSQL, RLS, migration patterns
├── SKILL_SECURITY.md — Auth, CSP, CSRF, rate limiting
├── SKILL_ANALYTICS.md — Event naming, PostHog, funnels
├── SKILL_DESIGN.md — Design system, colors, typography, components
└── SKILL_NEET_DOMAIN.md — NEET exam domain knowledge
```

---

## 8. RECOMMENDED FEATURES

```
Recommended Additions
├── "Exam Simulation Mode" ⭐ [🟢 P2]
│   ├── Full 3-hour NEET simulation (180 Qs)
│   └── Post-exam detailed analysis
│
├── "Explain Like I'm 16" Toggle [🟡 P1]
│   └── Simplified AI explanations by default
│
├── "Formula Sheet Auto-Generator" ⭐ [🟡 P1]
│   ├── AI extracts formulas from completed chapters
│   └── One-page PDF export per subject
│
├── "Error Log / Mistake Tracker" [🟡 P1]
│   ├── Wrong quiz questions → error log
│   └── AI analyzes error patterns
│
├── "NEET Cut-off Tracker" [🟡 P1]
│   ├── Historical NEET cut-offs
│   └── Category-wise predictions
│
└── "Peer Benchmark" (Anonymous) [🟢 P2]
    └── "You are in top X% of aspirants"
```

---

*APP_MAP.md — StudyOS Platform v1.0 | May 2026*
*Color coding: 🔴 MVP | 🟡 v1.0 | 🟢 v2.0 | ⭐ High Impact | 🤖 AI Agent | 🔗 Integration | 🛡️ Security | 📊 Analytics*
