# ?? ARCHIVED � Historical Document

> **Status:** This document is archived for historical reference only. It may contain outdated information. See FINAL_AUDIT_REPORT.md and DOCUMENTATION_INDEX.md for current state.

---

# ROADMAP.md
# StudyOS — Enterprise Platform Roadmap
# End-to-End: Concept → MVP → v1.0 → v2.0 → Scale

> **Mission:** Build the most intelligent, student-centric study OS for India's
> 2.4 million NEET aspirants — combining AI tutoring, personalized roadmaps,
> progress tracking, and seamless NotebookLM/LLM integration in one platform.

---

## 0. QUICK REFERENCE

| Item | Detail |
|------|--------|
| **Product** | StudyOS — AI Study Platform |
| **Primary Exam** | NEET 2026 (expandable to JEE, UPSC, GATE) |
| **Target Users** | Class 11/12 students + Droppers (16–22 yrs), India |
| **Stack** | Next.js 15 + TypeScript + Supabase + LangGraph + Tailwind |
| **Deployment** | Vercel (frontend) + Supabase (backend + DB + storage) |
| **Auth** | Supabase Auth (email + Google + Phone OTP) |
| **AI** | Multi-provider LLM router (Claude, GPT-4o, Gemini, Groq, Ollama) |
| **Database** | PostgreSQL (Supabase) + pgvector + Dexie.js (offline) |
| **Analytics** | PostHog + Tinybird/ClickHouse |
| **Payments** | Razorpay (India) + Stripe (international) |
| **Notifications** | FCM (push) + WhatsApp Business API (Twilio) |
| **Monitoring** | Sentry + LangSmith + Uptime Robot |
| **AI Agents** | LangGraph + structured outputs with Zod |
| **Reference** | [docs/STUDYOS_COMPLETE_SUMMARY.md](../../docs/STUDYOS_COMPLETE_SUMMARY.md) |

---

## 1. GOALS

### Primary Goals

| ID | Goal | Metric of Success |
|----|------|-------------------|
| G1 | **Note Intelligence** | Upload notes → AI maps 90%+ topics to NEET syllabus correctly |
| G2 | **LLM Flexibility** | Connect 5+ providers in < 2 min; switch without losing history |
| G3 | **Personalized Roadmap** | AI generates weekly plan in < 10s; 80% of students follow it |
| G4 | **Progress Tracking** | Every subtopic trackable; syncs offline-first in < 100ms |
| G5 | **NotebookLM Bridge** | One-click export; formatted markdown ready to import |
| G6 | **Multi-tenant** | Institute can onboard 500+ students with teacher dashboards |
| G7 | **Engagement** | D30 retention > 40%; avg daily study session > 45 min |
| G8 | **Performance** | LCP < 2.5s; offline core works on 2G; < 5MB initial bundle |

### North Star Metric
> **Weekly Active Studiers (WAS):** Students who complete ≥ 3 study sessions per week
> Target: 10 WAS at launch → 500 WAS at 3 months → 5000 WAS at 6 months

---

## 2. USER PERSONAS

### Persona 1 — Arjun (Primary)
- 17 years old, Cumbum, Tamil Nadu
- NEET 2026 aspirant, coaching at local institute
- Studies 8–10 hrs/day, Android phone (mid-range)
- Pain: no single place to track what's done; AI tools feel generic
- Needs: checklist + AI tutor + roadmap in Tamil/English

### Persona 2 — Priya (Dropper)
- 19 years old, Hyderabad
- Second NEET attempt, strong Biology, weak Chemistry
- Studies independently, has laptop + phone
- Pain: knows what she doesn't know but can't prioritize efficiently
- Needs: weak area detector + spaced repetition + mock tests

### Persona 3 — Mr. Rajan (Teacher — B2B)
- 35 years old, runs coaching institute, Coimbatore
- 120 students across 4 batches
- Pain: no visibility into which students are actually studying
- Needs: class progress dashboard + note distribution + WhatsApp alerts

### Sample User Journey — Arjun
```
Week 1 (Onboarding)
├── Signs up with Google → sets NEET 2026, exam date May 3, 8 hrs/day
├── Marks 12 chapters as "already studied" in quick assessment
├── AI generates 18-week roadmap → Week 1: Current Electricity + Genetics revision
├── Connects Groq API key (free) for AI tutor
└── Installs as PWA on phone

Day 3 (Normal Study Session)
├── Opens app 8 AM → Dashboard: "Good morning Arjun! 🌅 Today: Electrochemistry"
├── Opens Electrochemistry → sees checklist with 23 subtopics
├── Completes Nernst Equation subtopic → progress ring: 43% → 47%
├── Stuck on Kohlrausch's law → taps "Ask AI"
│   └── AI answers with NCERT citation + example numerical
├── Uploads handwritten notes photo
│   └── OCR extracts text → AI maps to 4 subtopics → saves to chapter
└── 2-hour session: 8 subtopics done → streak: 🔥 Day 3

Week 8 (Mid-Journey)
├── Dashboard: "67% overall complete. 14 Tier 1 chapters done. On track!"
├── Weak Area Detector: "You score 45% on Genetics MCQs — revise this week"
├── Roadmap auto-updated: swaps Week 9 topic with Genetics intensive
├── Takes chapter quiz: 12/20 → error log updated with 8 wrong answers
└── Exports Biology notes to NotebookLM for audio podcast study

3 Weeks Before Exam
├── Sprint Mode activated → app shifts to rapid revision
├── All 79 chapters checked; Tier 1 complete, Tier 2 at 80%
├── Daily: 20-Q rapid fire quiz from weak areas
├── Formula sheet auto-generated → saves PDF to WhatsApp
└── Rank Predictor: "Predicted: 585–615 | AIR estimate: 18,000–25,000"
```

---

## 3. MILESTONES

### MVP — Week 1–3 (21 Days)
**Goal:** Working product with core loop: Study → Track → AI Ask → Repeat

```
Authentication & Profile
  [✅] Email + Google OAuth sign-in (Supabase Auth)
  [✅] Onboarding: exam selection + date + chapter assessment
  [✅] User profile stored in Supabase

Syllabus & Checklist
  [✅] Full NEET 2026 syllabus seeded (79 chapters, 400+ topics, 1000+ subtopics)
  [✅] Chapter checklist with checkbox per subtopic
  [✅] Progress % per chapter, subject, and overall
  [✅] Offline-first via Dexie.js (works without internet)
  [✅] Streak tracking (daily study streak counter)

AI Chat
  [✅] LLM provider settings (API key input, provider selector)
  [✅] Chat panel scoped to current chapter
  [✅] Streaming responses
  [✅] Multi-provider support: OpenAI + Anthropic + Gemini + Groq

Dashboard
  [✅] Progress rings per subject
  [✅] Today's study recommendation (from roadmap)
  [✅] Exam countdown

Deploy
  [✅] Vercel deploy + Supabase project live
  [✅] PWA manifest (installable on phone)
  [✅] Share with 10 beta students
```

### v1.0 — Week 4–10 (6 Weeks Post-MVP)
**Goal:** Intelligent platform — notes, roadmap, quiz, analytics, integrations

```
Note Intelligence
  [ ] Image/PDF upload → Tesseract.js OCR (client-side)
  [ ] AI topic extraction agent → maps to NEET syllabus
  [ ] Syllabus gap detection ("Your notes miss: crossing over, chiasma")
  [ ] Note editor (markdown) with chapter tagging
  [ ] Notes library (search, filter, sort)

AI Roadmap Generator
  [ ] Roadmap Agent (LangGraph): inputs progress + exam date → weekly plan JSON
  [ ] Weekly calendar view (horizontal scroll, snap to current week)
  [ ] Auto-regenerate weekly (Monday morning cron)
  [ ] Urgency system (green/amber/red based on weeks remaining)
  [ ] Export roadmap as PDF + WhatsApp image

Quiz + PYQ System
  [ ] PYQ bank seeded (NEET 2015–2025, 1800+ questions)
  [ ] AI Quiz Generator agent (per chapter, NEET-style MCQs)
  [ ] Chapter quiz mode (practice + exam)
  [ ] Mistake tracker (wrong answers → error log → pre-exam review)
  [ ] Spaced repetition scheduling (SM-2 algorithm)

Analytics Dashboard
  [ ] Study heatmap calendar (GitHub-style)
  [ ] Chapter completion velocity chart
  [ ] Subject balance donut
  [ ] Weak area table (by quiz score + recency)
  [ ] Predicted NEET score range
  [ ] Weekly report (PDF export + WhatsApp share)

Integrations
  [ ] Google Drive MCP (OAuth + push notes as Google Docs)
  [ ] NotebookLM export (chapter → optimized markdown → ZIP download)
  [ ] WhatsApp daily reminders (opt-in, Twilio Business API)
  [ ] Razorpay subscription (Free vs Student Pro ₹299/mo)
  [ ] YouTube lecture links per chapter (curated + search)

NEET-Specific Features
  [ ] Formula sheet auto-generator (AI extracts from completed chapters → PDF)
  [ ] NEET rank predictor (completion % + quiz accuracy → score range + AIR)
  [ ] Historical cut-off tracker (2019–2025, state-wise, category-wise)
  [ ] 30-day Sprint Mode (exam < 30 days → compressed revision plan)

Performance & Polish
  [ ] Virtual scrolling (react-virtual) for long chapter lists
  [ ] Full dark mode
  [ ] PWA offline service worker (Workbox)
  [ ] Background sync (Dexie sync queue → Supabase when online)
  [ ] Push notifications (FCM for Android/iOS)
  [ ] Tamil + Hindi language support (i18n framework)
  [ ] Accessibility audit (WCAG 2.1 AA)
```

### v2.0 — Week 11–24 (3 Months Post-v1)
**Goal:** Enterprise platform, B2B, advanced AI, scale

```
Teacher & Institute Dashboard
  [ ] Class progress heatmap (students × chapters matrix)
  [ ] At-risk student alerts (automated)
  [ ] Assignment system (assign chapters + quizzes with deadlines)
  [ ] Note distribution to batch
  [ ] WhatsApp broadcast to class
  [ ] Multi-batch management (institute admin panel)
  [ ] White-label (custom logo, colors, domain)
  [ ] Bulk student import (CSV)
  [ ] Billing dashboard (per-seat, invoices)

Advanced AI Agents
  [ ] RAG pipeline (NCERT corpus → pgvector → grounded answers)
  [ ] Weak Area Detector agent (behavioral analysis → top 5 weak subtopics)
  [ ] Exam Strategy Agent (2 weeks before exam: order of attempt, time allocation)
  [ ] Parent Report Agent (weekly WhatsApp/PDF report for parents)
  [ ] "AI Study Partner" (Socratic mode — AI asks questions to student)
  [ ] Voice notes (Whisper API transcription → topic extraction)

Collaboration
  [ ] Anonymous study groups (students studying same chapter today)
  [ ] Shared chapter challenges (first 5 to complete wins)
  [ ] Public note library (community notes, quality-rated)
  [ ] Note sharing via link

Mock Tests
  [ ] Full NEET simulation (180 Qs, 3 hrs, OMR UI)
  [ ] Section-wise performance analysis
  [ ] Time management report (time per question histogram)
  [ ] Adaptive difficulty (harder questions as student improves)

Advanced Analytics
  [ ] Cohort retention analysis (D1/D7/D30/D90)
  [ ] Feature adoption tracking
  [ ] AI query pattern analysis (most asked questions per chapter)
  [ ] Conversion funnel (free → paid) with drop-off points
  [ ] Tinybird/ClickHouse for real-time analytics at scale

Multi-Exam Support
  [ ] JEE Mains 2026 syllabus
  [ ] JEE Advanced 2026 syllabus
  [ ] NEET PG (postgraduate) syllabus
  [ ] Custom exam profile (any exam, manual chapter entry)

Scale & Infrastructure
  [ ] CDN for NCERT content (Cloudflare)
  [ ] Database read replicas (for analytics queries)
  [ ] Background job queue (pg_cron + Supabase Edge Functions)
  [ ] LLM response caching (Redis) for common questions
  [ ] Automated NCERT vector re-indexing pipeline
  [ ] Multi-region Supabase (India + Singapore)
```

---

## 4. REQUIRED FEATURES CHECKLIST (Full Enterprise)

### Core Infrastructure
- [ ] Supabase project (PostgreSQL + Auth + Storage + Realtime + Edge Functions)
- [ ] Vercel project (linked to GitHub, preview deploys on PR)
- [ ] Upstash Redis (rate limiting + session cache)
- [ ] PostHog (analytics — self-hosted or cloud)
- [ ] Sentry (error tracking frontend + backend)
- [ ] LangSmith (LLM call tracing + cost tracking)
- [ ] Uptime Robot (endpoint monitoring)
- [ ] GitHub Actions CI/CD pipeline

### Authentication
- [ ] Email + password (Supabase Auth)
- [ ] Google OAuth (one-tap)
- [ ] Phone OTP (India +91, MSG91 or Twilio)
- [ ] Magic link (passwordless)
- [ ] Role system: student / teacher / institute_admin / platform_admin
- [ ] Multi-device session management (list + revoke)
- [ ] Rate limiting on auth (5 fails → 15min lockout)
- [ ] GDPR/DPDP Act compliance (export + delete account)

### Database
- [ ] 9 migration files (auth, syllabus, progress, notes, roadmap, quiz, chat, analytics, payments)
- [ ] RLS policies on every table (tested with Supabase RLS test tool)
- [ ] pgvector extension (for NCERT RAG + note search)
- [ ] Database functions (completion %, streak calc, weak chapter detection)
- [ ] Realtime subscriptions (progress updates, notifications)
- [ ] Automated backups (Supabase Pro: daily backups, 30-day retention)
- [ ] pg_cron for: daily streak calculation, weekly report generation, roadmap refresh

### AI & Agents
- [ ] LLM Router (unified interface: OpenAI + Anthropic + Gemini + Groq + Ollama)
- [ ] Tutor Agent (NCERT-grounded Q&A with citations)
- [ ] Roadmap Agent (LangGraph planning agent)
- [ ] Note Extraction Agent (OCR text → NEET topic mapping)
- [ ] Quiz Generator Agent (NEET-style MCQ generation)
- [ ] Weak Area Detector Agent (behavioral analysis)
- [ ] Daily Motivation Agent (personalized morning message)
- [ ] RAG pipeline (NCERT corpus indexed + retrieval)
- [ ] LangSmith tracing on all agent calls
- [ ] Prompt injection prevention (XML sandboxing)
- [ ] Agent output validation (Zod schemas)

### Frontend
- [ ] Design system (tailwind.config.ts with full token set)
- [ ] shadcn/ui component library initialized
- [ ] All SKILL.md files in docs/product/skills-app/ (8 files total)
- [ ] Mobile-first responsive (tested on 360px, 390px, 414px widths)
- [ ] Dark mode (class-based, persisted to localStorage)
- [ ] WCAG 2.1 AA accessibility
- [ ] Virtual scrolling for all long lists
- [ ] Optimistic UI on all mutations
- [ ] Error boundaries on all major sections
- [ ] Loading skeletons (not spinners) for all async content
- [ ] Empty states for all list views

### Offline & PWA
- [ ] Dexie.js schema (all local tables)
- [ ] Service worker (Serwist / Workbox for Next.js)
- [ ] Background sync (Dexie sync queue)
- [ ] Offline indicator + graceful degradation
- [ ] PWA manifest (all icon sizes)
- [ ] Install prompt (smart timing: after 2nd session)
- [ ] Push notifications (FCM tokens stored per device)

### Integrations
- [ ] Google Drive MCP (OAuth + file sync)
- [ ] NotebookLM export (markdown + ZIP)
- [ ] WhatsApp Business API (daily reminders + weekly reports)
- [ ] YouTube Data API (lecture recommendations)
- [ ] Razorpay (subscriptions + webhooks)
- [ ] FCM (push notifications)

### Security
- [ ] API keys: client-side Dexie only, never sent to server
- [ ] DOMPurify on all user-generated content renders
- [ ] Content Security Policy headers (vercel.json)
- [ ] File upload: MIME validation by magic bytes
- [ ] Prompt injection: XML sandwich on all user inputs to LLM
- [ ] HTTPS only (HSTS header)
- [ ] Secure cookies (httpOnly + SameSite=Strict)
- [ ] RLS audit (every table tested for cross-user data leakage)

### Analytics
- [ ] PostHog event tracking (full event catalog from SKILL_ANALYTICS.md)
- [ ] Funnel: signup → onboarding → first study → streak day 7
- [ ] Student personal analytics dashboard
- [ ] Weekly study report (PDF + WhatsApp)
- [ ] Institute analytics (teacher + admin dashboards)
- [ ] Business metrics (Metabase internal dashboard)

---

## 5. TECH STACK — FULL ENTERPRISE SPEC

### Frontend Stack
```
Core:
  Next.js 15 (App Router) + TypeScript (strict mode)
  React 19

Styling:
  Tailwind CSS v3 + tailwind-merge + clsx
  shadcn/ui (component primitives)
  Framer Motion (animations)

State:
  Zustand v4 (global state: auth, UI, LLM config)
  TanStack Query v5 (server state + caching + background refresh)
  Dexie.js v4 (IndexedDB offline store)

AI/LLM:
  LangChain.js + LangGraph (agent framework)
  Custom LLM router (OpenAI / Anthropic / Gemini / Groq / Ollama)

Content:
  react-markdown + remark-gfm + rehype-highlight (markdown rendering)
  KaTeX (math formula rendering)
  DOMPurify (XSS sanitization)

Files:
  Tesseract.js (client-side OCR)
  pdfjs-dist (client-side PDF parsing)
  JSZip (ZIP creation for exports)

PWA:
  Serwist (Workbox-compatible service worker for Next.js)

Analytics:
  PostHog (event tracking + session recording)
  Sentry (error tracking)

Payments:
  Razorpay (Indian payments)
  Stripe (international)

i18n:
  react-i18next (English + Tamil + Hindi + Telugu)

Testing:
  Vitest (unit tests)
  Testing Library (component tests)
  Playwright (E2E tests)
```

### Backend Stack
```
Primary:
  Supabase (PostgreSQL 15 + Auth + Storage + Realtime + Edge Functions)

Extensions:
  pgvector (1536-dim vectors for NCERT RAG)
  pg_cron (scheduled jobs)
  moddatetime (auto-update updated_at)
  uuid-ossp (UUID generation)

Edge Functions (Deno runtime):
  roadmap-generator       → calls Roadmap Agent
  note-extractor          → calls Note Extraction Agent
  quiz-generator          → calls Quiz Generator Agent
  whatsapp-scheduler      → cron: daily reminders + weekly reports
  razorpay-webhook        → handles payment events
  fcm-push-sender         → sends push notifications
  ncert-indexer           → one-time: index NCERT corpus to pgvector
  weekly-analytics-rollup → cron: Sunday: materializes weekly stats

Cache:
  Upstash Redis
  - Rate limiting (sliding window, per-user)
  - LLM response caching (SHA256 hash of prompt → cached response)
  - Session data (fast lookup)

Monitoring:
  Sentry (errors + performance)
  LangSmith (LLM trace logging)
  Axiom (structured logs from Edge Functions)

Queue/Jobs:
  pg_cron (in-database scheduler)
  Supabase Realtime (event streaming to frontend)
```

### Infrastructure & DevOps
```
Hosting:
  Vercel (frontend)
    - Automatic HTTPS
    - Preview deploys per PR
    - Edge Network (CDN)
    - Environment variables per environment

  Supabase (backend)
    - Free tier → Pro ($25/mo at 500+ users)
    - Auto backups (Pro tier)
    - Connection pooling (PgBouncer)
    - Point-in-time recovery

  Upstash Redis (serverless Redis)
    - Pay-per-request (free tier generous)

  Cloudflare (CDN for NCERT static assets)
    - Cache NCERT PDFs + images globally

Domains:
  studyos.app             → main app
  api.studyos.app         → Supabase project URL alias
  *.studyos.app           → institute white-label subdomains

CI/CD:
  GitHub Actions
    - On PR: lint + typecheck + unit tests + Vercel preview deploy
    - On merge to main: full test suite + Vercel production deploy + Supabase migration
    - Weekly: dependency vulnerability scan

Environments:
| development  → local Supabase (supabase start) + Next.js dev server
  staging      → Supabase staging project + Vercel preview
  production   → Supabase production project + Vercel production
```

---

## 6. DATABASE SCHEMA OVERVIEW

```
Core Tables (9 migration groups):

001 — Auth & Users
  users              → extends auth.users (name, exam_type, exam_date, role, institute_id)
  institutes         → coaching centers (name, slug, logo, plan, seats)
  institute_members  → users ↔ institutes (role: student/teacher/admin)
  batches            → teacher's class groups
  user_devices       → FCM tokens per device (push notifications)

002 — Syllabus (public read, admin write)
  exam_profiles      → NEET2026, JEE_MAINS_2026, etc. (versioned)
  subjects           → Physics, Chemistry, Biology per exam
  chapters           → tier, weightage_pct, is_deleted, ncert_ref
  topics             → under chapters, is_high_yield
  subtopics          → definition, is_high_yield, is_deleted, difficulty

003 — Progress (student write, teacher read-in-batch)
  user_chapter_progress    → pct_complete, confidence, revision_count
  subtopic_completions     → idempotent (unique user+subtopic)
  study_sessions           → start/end, chapters_studied, total_minutes
  streaks                  → current, longest, last_study_date

004 — Notes
  notes              → content_md, source_type, file_url, extracted_topics
  note_versions      → full history per note
  note_embeddings    → chunk_text + vector(1536) for semantic search

005 — Roadmap
  roadmaps           → ai_reasoning, readiness_score, urgency_level
  week_plans         → focus_theme, week_tip, daily_breakdown jsonb
  week_plan_chapters → action: new_study/revision/practice/mock

006 — Quiz & Questions
  questions          → source: PYQ/AI, year, options jsonb, correct, explanation
  quiz_sessions      → score, total_questions, time_taken
  quiz_responses     → per-question response, is_correct, time_taken
  user_question_flags → saved/skipped/flagged per user

007 — Chat
  chat_sessions      → llm_provider, model, total_tokens, chapter_id (context)
  messages           → role, content, tokens_used

008 — Analytics
  events             → event_type, properties jsonb, session_id, device_type
  daily_stats        → materialized: study_mins, subtopics_done, quiz_avg

009 — Payments
  plans              → name, price_inr_monthly, features jsonb
  subscriptions      → user_id, plan, status, period, razorpay_sub_id
  invoices           → amount, paid_at, receipt_url
```

---

## 7. AI AGENTS OVERVIEW

```
Agent 1 — Tutor Agent           [Most used | LangGraph ReAct]
  Input:  Student question + chapter context
  Tools:  ncert_search, student_notes_search, pyq_search
  Output: Answer + NCERT citations + related subtopics
  Model:  Fast/cheap (Groq llama / Claude Haiku)

Agent 2 — Roadmap Agent         [Weekly trigger | LangGraph Planner]
  Input:  All 79 chapter statuses + exam date + study hours
  Tools:  chapter_progress_reader, tier_prioritizer, schedule_builder
  Output: WeeklyRoadmap JSON (validated by Zod)
  Model:  Powerful (GPT-4o / Claude Sonnet)

Agent 3 — Note Extraction Agent [On upload | LangGraph Pipeline]
  Input:  OCR text from uploaded notes
  Tools:  topic_extractor, syllabus_mapper, gap_detector
  Output: ExtractionResult (topics + gaps + quality_score)
  Model:  Balanced (GPT-4o-mini / Gemini Flash)

Agent 4 — Quiz Generator        [On demand | LangGraph Pipeline]
  Input:  Chapter ID + difficulty level
  Tools:  ncert_search, pyq_fetcher, question_validator
  Output: Question[] (NEET-style MCQs with explanations)
  Model:  Balanced (GPT-4o-mini / Gemini Flash)

Agent 5 — Weak Area Detector    [Weekly trigger | LangGraph Analyzer]
  Input:  30-day quiz + progress + chat query data
  Output: WeakAreaReport (top 5 weak subtopics + action plan)
  Model:  Any (analysis task, not creative)

Agent 6 — Motivation Agent      [Daily cron 6AM | Simple chain]
  Input:  Student name + streak + today's roadmap + exam countdown
  Output: DailyMessage (greeting + tip + today's focus)
  Model:  Fast (Groq / Haiku)

Agent 7 — Exam Strategy Agent   [Triggered at T-14 days | Planner]
  Input:  Predicted score + weak areas + exam in N days
  Output: ExamStrategy (attempt order + time allocation + skip strategy)
  Model:  Powerful (GPT-4o / Claude Sonnet)
```

---

## 8. INTEGRATION ARCHITECTURE

```
MCP Integrations:

1. Google Drive MCP
   OAuth 2.0 → drive.file scope → push notes as Google Docs
   StudyOS → creates "StudyOS NEET 2026" Drive folder
   Supabase stores: { user_id, drive_folder_id, last_sync_at }

2. NotebookLM Export
   No public API (as of 2026) → generate optimized .md files
   Export: single chapter .md OR multi-chapter .zip
   Format: NEET-optimized markdown (headers, formulas, high-yield points)
   Future: Direct API push when Google releases NotebookLM API

3. WhatsApp Business API (Twilio)
   Messages: daily_reminder, weekly_report, milestone, parent_report
   Trigger: Supabase Edge Function cron (7AM IST = 1:30 UTC)
   Opt-in: explicit in settings; one-tap opt-out
   Store: user consent + phone + message log in Supabase

4. YouTube Data API v3
   Search: "{chapter_name} NEET lecture" → Physics Wallah, Vedantu
   Curated playlists: hardcoded channel IDs for top NEET educators
   Store: user-saved videos per chapter in Supabase

5. Razorpay
   Plans: Free / Student Pro (₹299/mo, ₹1999/yr) / Institute (custom)
   Flow: Frontend → Razorpay checkout → payment → webhook → Supabase
   Webhook endpoint: Supabase Edge Function /razorpay-webhook
   Store: subscriptions + invoices in Supabase

6. FCM (Push Notifications)
   Register device token on first login → store in user_devices
   Send via: Firebase Admin SDK in Supabase Edge Function
   Triggers: daily reminder, milestone achievement, at-risk alert (teacher)

7. Supabase Realtime (internal)
   Subscribe to: progress updates, new notifications, roadmap changes
   Filter by user_id to minimize data transfer
   Auto-reconnect on network restore (critical for Indian mobile users)
```

---

## 9. ANALYTICS ARCHITECTURE

```
Event Flow:
  User Action → PostHog.track() → PostHog Cloud/Self-hosted
                                 → Supabase events table (backup)
                                 → Tinybird ingestion API (real-time aggregation)

Event Catalog (key events):
  Onboarding: onboarding_started, exam_selected, roadmap_generated_first
  Study:       subtopic_completed, chapter_completed, streak_achieved
  AI:          message_sent, ai_response_received
  Notes:       note_uploaded, note_extraction_completed
  Quiz:        quiz_started, quiz_completed, wrong_answer_logged
  Engagement:  app_opened, session_ended (with duration), feature_used
  Business:    upgrade_clicked, payment_completed, subscription_cancelled

Dashboards:
  Student:    Study heatmap + velocity + subject balance + weak areas + score predictor
  Teacher:    Class heatmap + at-risk students + quiz performance
  Institute:  Funnel + batch comparison + seat usage
  Internal:   DAU/WAU/MAU + conversion + retention + LLM cost per user
```

---

## 10. TIMELINE — FULL 24-WEEK PLAN

```
Phase 1 — Foundation (Weeks 1–3) [MVP]
  Week 1: Repo setup + DB schema (migrations 001–003) + Supabase project
          Auth (email + Google + phone OTP) + Onboarding flow
  Week 2: Syllabus seeding (79 chapters JSON) + Chapter checklist UI
          Progress tracking (Dexie offline + Supabase sync) + Dashboard
  Week 3: LLM router + Chat panel (streaming) + LLM provider settings
          Deploy to Vercel + PWA manifest + 10 beta students onboarded

Phase 2 — Intelligence (Weeks 4–6)
  Week 4: Note upload pipeline (OCR → AI extraction → syllabus mapping)
          Note editor + Notes library + Supabase Storage integration
  Week 5: Roadmap Agent (LangGraph) + Weekly calendar UI
          Urgency system + Roadmap export (PDF + WhatsApp image)
  Week 6: PYQ bank seeding (1800+ questions) + Quiz session UI
          Mistake tracker + Basic spaced repetition

Phase 3 — Analytics & Integrations (Weeks 7–9)
  Week 7: PostHog event tracking + Student analytics dashboard
          Study heatmap + Velocity chart + Weak area table
  Week 8: Google Drive MCP (OAuth + push notes)
          NotebookLM export (markdown + ZIP generator)
          Razorpay subscription integration
  Week 9: WhatsApp Business API integration (Twilio)
          FCM push notifications setup
          YouTube lecture recommendations

Phase 4 — NEET Features & Polish (Weeks 10–11)
  Week 10: Formula sheet generator + Rank predictor
           Cut-off tracker + Sprint Mode (30-day exam prep)
           Dark mode + Tamil/Hindi i18n
  Week 11: PWA offline (Workbox service worker + background sync)
           Accessibility audit (WCAG 2.1 AA)
           Performance optimization (bundle splitting, virtual scroll)
           v1.0 public launch 🚀

Phase 5 — B2B & Scale (Weeks 12–16)
  Week 12: Teacher dashboard (class progress heatmap + at-risk alerts)
           Assignment system + note distribution to batch
  Week 13: Institute admin panel (multi-batch + white-label + billing)
           Bulk student CSV import + batch management
  Week 14: RAG pipeline (NCERT corpus → pgvector indexing)
           Upgraded Tutor Agent (NCERT-grounded with citations)
           Weak Area Detector Agent
  Week 15: Exam Strategy Agent (T-14 days trigger)
           Parent Report Agent (WhatsApp PDF weekly)
           LangSmith tracing on all agents
  Week 16: Full NEET mock test (180 Qs, 3hrs, OMR UI)
           Adaptive quiz difficulty
           Performance + scale optimization

Phase 6 — Advanced Features (Weeks 17–24)
  Week 17: Anonymous study groups + peer benchmarks
  Week 18: Voice notes (Whisper API → topic extraction)
  Week 19: "AI Study Partner" Socratic mode
  Week 20: JEE Mains + JEE Advanced syllabus support
  Week 21: Multi-region infrastructure (India + Singapore)
  Week 22: Tinybird/ClickHouse real-time analytics at scale
  Week 23: Android app (React Native wrapper or TWA)
  Week 24: Public API for third-party integrations
```

---

## 11. SUCCESS METRICS

### Student Metrics
| Metric | MVP Target | v1 Target | v2 Target |
|--------|-----------|-----------|-----------|
| DAU | 10 | 300 | 3,000 |
| WAU | 10 | 500 | 5,000 |
| D7 Retention | 50% | 55% | 65% |
| D30 Retention | 20% | 35% | 45% |
| Avg daily session | 15 min | 35 min | 50 min |
| Subtopics/day per user | 3 | 8 | 12 |
| AI messages/day per user | 2 | 8 | 15 |
| Chapters completed | N/A | 60% | 75% |

### Business Metrics
| Metric | v1 Target | v2 Target |
|--------|-----------|-----------|
| Monthly Revenue | ₹15,000 | ₹2,00,000 |
| Paid conversions | 50 | 600 |
| Institute partners | 0 | 5 |
| NPS Score | >35 | >55 |
| Crash-free sessions | >97% | >99.5% |

### AI Quality Metrics
| Metric | v1 Target | v2 Target |
|--------|-----------|-----------|
| Answer accuracy (NEET scope) | >85% | >92% |
| Roadmap follow rate | >50% | >70% |
| Note extraction accuracy | >75% | >88% |
| Avg AI response time | < 3s | < 1.5s |
| LLM cost per DAU | < ₹2 | < ₹1 |

---

## 12. RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| NTA changes NEET 2026 syllabus | Low | High | Modular JSON syllabus; admin CMS to update topics; diff alerts to students |
| LLM provider outage | Medium | High | Multi-provider fallback chain; Ollama local as last resort |
| OCR quality poor for handwriting | Medium | High | Manual text input fallback; image quality feedback to user |
| Indian mobile performance (2G, low-RAM) | High | High | Offline-first; <5MB initial bundle; virtual scroll; skeleton loading |
| Student distrust of AI accuracy | Medium | High | Always cite NCERT page; "Verify in NCERT" deep links |
| Exam stress/mental health concerns | Medium | High | Sensitive AI responses; never shame poor performance; resources for stress |
| Data privacy (student notes) | Low | Critical | Notes stay on device + user's own Drive; no notes in LLM backend logs |
| Supabase free tier limits (500MB) | Medium | Medium | Optimize storage; migrate to Pro at 200+ users (cost: $25/mo) |
| Razorpay payment failures | Low | Medium | Retry logic; email fallback; manual upgrade path |
| WhatsApp API rate limits | Medium | Low | Queue + batch sends; respect Meta's 24hr window rules |
| Coaching institutes resistant to new tools | Medium | High | Teacher-first demo; show class performance dashboard value immediately |
| Students share API keys | Low | Medium | Per-key rate limiting; educate on key security |

---

## 13. DEPLOYMENT PIPELINE

```
Local Development
├── supabase start (local Supabase)
├── npm run dev (Next.js dev server)
├── .env.local (local credentials)
└── Deno for Edge Functions (supabase functions serve)

Pull Request
├── GitHub Actions trigger
├── Lint (ESLint + Prettier check)
├── Type check (tsc --noEmit)
├── Unit tests (Vitest)
├── Component tests (Testing Library)
├── Vercel preview deploy (auto)
└── Supabase migration dry-run

Merge to Staging
├── Staging Supabase migration apply
├── Staging Vercel deploy
├── E2E tests (Playwright on staging)
└── Manual QA (5-point checklist)

Merge to Main → Production
├── Production Supabase migration apply
├── Production Vercel deploy
├── Sentry release tracking
├── Uptime Robot checks resume
└── Slack notification: #deployments

Rollback Plan
├── Vercel: instant rollback to previous deployment (1-click)
├── Supabase: migration rollback scripts in 000_rollbacks/
└── Feature flags: disable broken feature without redeploy (PostHog flags)
```

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  pull_request:
    branches: [main, staging]
  push:
    branches: [main, staging]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test:unit
      - run: npm run test:components

  e2e:
    if: github.ref == 'refs/heads/main'
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
        env:
          PLAYWRIGHT_BASE_URL: ${{ secrets.STAGING_URL }}

  deploy:
    needs: [quality]
    runs-on: ubuntu-latest
    steps:
      - name: Apply Supabase Migrations
        run: supabase db push
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
      # Vercel deploys automatically via GitHub integration
```

---

## 14. ENVIRONMENT VARIABLES REFERENCE

```bash
# ═══════════════════════════════════════════════════
# Frontend (NEXT_PUBLIC_ prefix — exposed to browser)
# ═══════════════════════════════════════════════════
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_POSTHOG_KEY=phc_...
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_live_...
NEXT_PUBLIC_APP_URL=https://studyos.app
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_SENTRY_DSN=https://...@sentry.io/...
NEXT_PUBLIC_ENVIRONMENT=production

# ═══════════════════════════════════════════════════
# Backend (Supabase Edge Functions — server-only)
# ═══════════════════════════════════════════════════
SUPABASE_SERVICE_ROLE_KEY=eyJ...         # Never expose to frontend!
SUPABASE_JWT_SECRET=...

# LLM (for server-side agent calls — RAG indexing only)
OPENAI_API_KEY=sk-...                    # For NCERT indexing pipeline
LANGSMITH_API_KEY=ls__...               # AI observability

# Notifications
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
WHATSAPP_FROM_NUMBER=whatsapp:+14155238886
FCM_SERVER_KEY=...                       # Firebase Cloud Messaging

# Integrations
YOUTUBE_DATA_API_KEY=AIza...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...

# Infrastructure
UPSTASH_REDIS_URL=redis://...
UPSTASH_REDIS_TOKEN=...
AXIOM_API_TOKEN=...                      # Structured logging

# ═══════════════════════════════════════════════════
# STUDENT LLM KEYS — NEVER IN ENV OR DB
# Stored: Dexie.js (encrypted, client-side only)
# ═══════════════════════════════════════════════════
# OPENAI_API_KEY      → student enters in Settings
# ANTHROPIC_API_KEY   → student enters in Settings
# GOOGLE_API_KEY      → student enters in Settings
# GROQ_API_KEY        → student enters in Settings
# OLLAMA_BASE_URL     → student enters in Settings (default: localhost:11434)
```

---

## 15. SKILLS FILE DIRECTORY

All SKILL.md files live in `docs/product/skills-app/` directory. AI coding assistants
(Cursor, Windsurf, Claude, Copilot) read these before generating any code.

```
docs/product/skills-app/
├── SKILL_NEET_DOMAIN.md     ← Read first for any study/content features
│   Contains: Exam structure, deleted topics, tier definitions,
│   weightage data, student context, sensitive topics handling
│
├── SKILL_DESIGN.md          ← Read before any UI component
│   Contains: Color tokens, typography, spacing, component patterns,
│   dark mode, mobile-first rules, accessibility, animations
│
├── SKILL_FRONTEND.md        ← Read before any React/TS code
│   Contains: Project structure, component patterns, state management,
│   performance rules, testing patterns, import conventions
│
├── SKILL_BACKEND.md         ← Read before any Supabase/Edge Function code
│   Contains: RLS patterns, migration conventions, Edge Function patterns,
│   error format, database query patterns, Realtime subscriptions
│
├── SKILL_DATABASE.md        ← Read before any migration/RLS/query code (NEW)
│   Contains: Migration structure, 9 groups, RLS policies, patterns,
│   query examples, indexing strategy, performance rules
│
├── SKILL_AGENTS.md          ← Read before any AI/LLM agent code
│   Contains: LangGraph patterns, prompt templates, Zod schemas,
│   guardrail patterns, LLM router usage, 21st.dev template integration
│
├── SKILL_ANALYTICS.md       ← Read before adding any analytics events
│   Contains: Event naming convention, required properties,
│   event catalog, funnel definitions, privacy rules
│
└── SKILL_SECURITY.md        ← Read before any auth/data/upload code
    Contains: API key policy, XSS prevention, prompt injection,
    file upload safety, RLS audit checklist, DPDP compliance
```

---

## 16. LAUNCH CHECKLIST

### Pre-Launch (24 hours before)
- [ ] All environment variables set in Vercel + Supabase production
- [ ] Database migrations applied and verified on production
- [ ] NCERT vector index built (1-time indexing pipeline run)
- [ ] Razorpay live key configured + webhook endpoint tested
- [ ] WhatsApp Business API approved templates live
- [ ] Sentry release created + source maps uploaded
- [ ] Uptime Robot monitors set up (app + Supabase API)
- [ ] PostHog production project initialized
- [ ] LangSmith production project initialized
- [ ] Full E2E test suite passed on staging
- [ ] Manual test: signup → onboard → study → chat → export (real phone)
- [ ] Performance audit: Lighthouse score > 85 on mobile
- [ ] Security check: no API keys in source, RLS tested

### Launch Day
- [ ] Deploy to production (Vercel merge main)
- [ ] Verify all Edge Functions deployed (supabase functions list)
- [ ] Run smoke tests (automated + manual)
- [ ] Share beta link with first 20 students
- [ ] Monitor Sentry for errors in first 2 hours
- [ ] Monitor Supabase dashboard (DB connections, storage usage)
- [ ] Be on call for first 6 hours

### Post-Launch (Week 1)
- [ ] Daily: check Sentry errors + fix critical bugs
- [ ] Daily: review PostHog funnel (where are students dropping off?)
- [ ] Day 3: first feedback call with 5 beta students
- [ ] Day 7: review D7 retention (target: >50%)
- [ ] Day 7: ship top 3 bug fixes from feedback

---

*ROADMAP.md — StudyOS Enterprise Platform v1.0 | May 2026*
*Sections: Goals, Personas, Milestones (MVP→v1→v2), Features Checklist,*
*Tech Stack, DB Schema, Agents, Integrations, Analytics, Timeline (24 weeks),*
*Success Metrics, Risks, Deployment Pipeline, Env Vars, Skills, Launch Checklist*
