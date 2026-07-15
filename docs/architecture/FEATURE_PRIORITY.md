# StudyOS — Feature Priority

**Method:** maps `APP_MAP.md` priorities (P0/P1/P2) to **delivery waves** in `IMPLEMENTATION_ROADMAP.md`, adjusted for **enterprise risk** (security/data before scale).

**Scope change:** NO payments, NO subscriptions. Platform is free. PDF + Mind Map pipeline is the core differentiator.

---

## Tier S — Must never slip (safety + trust)

| Item | Rationale |
|------|-----------|
| RLS + policy tests | Prevents catastrophic cross-user leaks |
| Secure session handling (Supabase SSR) | Account takeover breaks everything |
| CSP + XSS sanitization | UGC + AI markdown = high XSS surface |
| File upload validation (magic bytes, size limits) | Malware/polyglot prevention |
| Rate limits on AI + auth | Abuse/cost control |
| Data export/delete (DPDP) | Legal + trust |

**Maps to:** Wave A cross-cutting + ongoing hardening.

---

## Tier P0 — MVP product (student value)

| Feature | Notes | Wave |
|---------|-------|------|
| Auth + profile (email + Google) | Exam date, exam selection | A |
| Syllabus navigator + chapter detail | 91 chapters, 450+ subtopics, mobile-first | A |
| Subtopic checklist + progress rings | Optimistic UI, RLS enforced | A |
| Streak system + dashboard badge | Daily motivation | A |
| Platform AI chat (scoped, streaming) | Chapter context, markdown + KaTeX | C |
| Settings: profile, notifications, appearance | Basics first | B |
| PWA installable + offline checklist | Works without internet | B |

**Maps to:** Waves A + B + C.

---

## Tier P1 — Core competitiveness (the moat)

| Feature | Notes | Wave |
|---------|-------|------|
| **PDF upload + processing pipeline** | Text extraction, vision OCR, mind map parsing | D |
| **Bulk import (400+ files)** | ZIP/multi-file, progress tracking, error recovery | D |
| **PDF viewer (PW-quality)** | Zoom, page nav, thumbnails, search, smooth transitions | D |
| **Mind map viewer (interactive)** | Canvas-based, zoomable, color-coded, expand/collapse | D |
| **Study mode** | Full-screen, highlights, personal notes, bookmarks | D |
| **Global search (Cmd+K)** | Across all 400+ PDFs, hybrid keyword+vector, snippets | D |
| **Download system** | Original PDF, summary PDF, mind map image, highlights, bulk ZIP, chapter compilation | D |
| Structured notes view | AI-extracted hierarchy, formula cards, definition cards | D |
| Quiz generation + sessions | AI-powered, difficulty levels, explanations | E |
| Mistake log + review | Track improvement, mark reviewed | E |
| Mock test (180Q / 3hr) | OMR navigation, timer | E |
| Weak area detection | Visual chart on dashboard | E |

**Maps to:** Waves D + E.

---

## Tier P2 — Retention + polish

| Feature | Notes | Wave |
|---------|-------|------|
| Analytics dashboard | Progress chart, subject breakdown, heatmap, quiz trends | F |
| AI study roadmap | Personalized plan based on progress + weak areas | F |
| Achievement badges | Milestones, streak rewards | F |
| Streak calendar | Visual fire animation, history | F |
| Mobile responsiveness | All screens tested on mobile | G |
| Accessibility (WCAG 2.1 AA) | Keyboard nav, screen reader support | G |
| Animations + polish | Framer Motion, loading states, dark mode | G |
| i18n infrastructure | English first, Hindi/Tamil/Telugu ready | G |

**Maps to:** Waves F + G.

---

## Tier P3 — Future (post-launch)

| Feature | Notes | When |
|---------|-------|------|
| Institute multi-tenancy | Teacher dashboards, batch management | After 10k WAU |
| WhatsApp / FCM notifications | Consent-gated reminders | After launch |
| Public API | Partner integrations | Demand-driven |
| Advanced RAG | Reranker, hybrid search tuning | When search quality dips |
| Read replica | Analytics offload | When DB CPU > 70% sustained |

---

## Explicit deferrals (avoid thrash)

| Idea | Defer until |
|------|-------------|
| React Native app | TWA + PWA insufficient OR partner store requirement |
| Multi-region active-active DB | Clear revenue + latency evidence |
| Real-time collaborative notes | Conflict resolution cost high |
| Payments / subscriptions | **REMOVED** — platform is free |

---

## Priority vs original ROADMAP checkboxes

- Treat legacy `[✅]` as **non-binding**; reprioritize using this file + issue tracker.
- ALL payment/billing items removed from priority list.

---

*Roadmap timing: `IMPLEMENTATION_ROADMAP.md`.*
