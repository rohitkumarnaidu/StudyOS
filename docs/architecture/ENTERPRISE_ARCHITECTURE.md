# StudyOS — Enterprise Architecture

**Purpose:** business-capable, **AI-first**, **modular** platform definition on top of `FINAL_ARCHITECTURE.md`.
**Audience:** CTO, principal engineers, security/compliance stakeholders.

---

## 1. Business domains (bounded contexts)

| Domain | Responsibilities | Primary data |
|--------|------------------|--------------|
| **Identity & Access** | Users, sessions, roles, MFA roadmap | `auth.*`, `profiles`, `institute_members` |
| **Catalog** | Syllabus versions, tiers, deleted topics | `exam_profiles` tree |
| **Learning** | Progress, streaks, study sessions | `subtopic_completions`, `streaks` |
| **Content** | Notes, PDFs, mind maps, embeddings, highlights, bookmarks | `notes`, `note_versions`, `note_embeddings`, `note_mindmaps`, `highlights`, `personal_notes`, `bookmarks` |
| **AI Conversations** | Chat sessions, messages, traces | `chat_sessions`, `chat_messages` |
| **Assessment** | Question bank, quiz sessions, mistake log | `questions`, `quiz_sessions`, `quiz_responses`, `mistake_log` |
| **Planning** | Roadmaps, study plans | `roadmaps`, `roadmap_items` |
| **Engagement** | Achievements, notifications | `achievements`, `user_achievements` |
| **Analytics** | Aggregated study metrics | materialized views, PostHog |

**Modularity rule:** each domain exposes **use-cases** in `packages/domain`; **UI** composes; **infra** implements.

---

## 2. Non-functional requirements (NFRs)

| NFR | Target (initial) | Scale path |
|-----|-------------------|------------|
| Availability | 99.9% app / 99.95% API monthly | multi-AZ via vendors; reduce blast radius with workers |
| p95 API (reads) | < 200ms uncached hot | Redis + RSC caching |
| p95 AI first token | < 800ms when cached routing | regional inference selection |
| PDF processing | < 60s per file (text), < 120s (scanned/mindmap) | async queue + parallel processing |
| Search latency | < 200ms across 400+ notes | pgvector HNSW + tsvector indexes |
| Data residency | India-first users | DB region + DPA with vendors |
| Privacy | DPDP-aligned consent + export/delete | legal review before marketing claims |
| Accessibility | WCAG 2.1 AA core flows | quarterly audit |
| Security | SOC2-ready practices (even if not certified year 1) | access logs, least privilege |

---

## 3. AI-first product architecture

**Principle:** AI is not a sidebar—it drives **what to study next**, **why**, and **how to verify understanding**.

- **Deterministic layer:** syllabus + progress + rules (tiers, exam countdown).
- **Probabilistic layer:** LLM explanations, roadmap narratives, quiz distractors, note structuring.
- **Guardrail layer:** Zod outputs, retrieval grounding, refusal policies.

**UX implication:** every primary screen has a **context chip** (chapter/subtopic) feeding AI safely.

### AI surfaces

| Surface | Model class | Latency SLO | Cost tier |
|---------|-------------|-------------|-----------|
| Tutor chat | Sonnet-class / GPT-4.1-class | < 5s first response | medium |
| Note structuring | Sonnet-class | < 30s per PDF | medium |
| Mind map parsing | Vision model (Gemini/GPT-4o) | < 60s per PDF | high |
| Quiz generation | Fast model (Groq/GPT-4o-mini) | < 10s per quiz | low |
| Roadmap generation | Sonnet-class | < 15s async | medium |
| Search reranking | Embedding model | < 200ms | low |

---

## 4. PDF + Mind Map Architecture

### Processing pipeline

```
Upload PDF → Storage (private bucket)
    ↓
Detect type: text-based / scanned / mind map
    ↓
┌─ Text PDF ────→ pdfplumber extract text ──────────────────┐
├─ Scanned PDF ─→ Upload → Vision model OCR ────────────────┤
└─ Mind Map PDF → Vision model parse structure → JSON tree ─┘
    ↓
AI structurer: tag chapter/topic, extract concepts, create summary
    ↓
Chunk text → generate embeddings → store in pgvector
    ↓
Mind map nodes/edges → store in note_mindmaps table
    ↓
User can: study, search, download, highlight, annotate
```

### Storage strategy

| Asset | Location | Access |
|-------|----------|--------|
| Original PDFs | Supabase Storage `notes/{user_id}/{note_id}/original.pdf` | Signed URL, 1h expiry |
| Processed text | `notes/{user_id}/{note_id}/extracted.json` | Server-only |
| Mind map JSON | `notes/{user_id}/{note_id}/mindmap.json` | Server-only |
| Thumbnails | `notes/{user_id}/{note_id}/thumb.jpg` | Public signed URL |
| Embeddings | pgvector `note_embeddings` table | Server-only RAG |

### Bulk import

- Accept ZIP or multi-file upload
- Process sequentially with progress tracking
- `bulk_import_jobs` table tracks status
- Realtime progress via Supabase Realtime subscription
- Resume on failure (idempotent per file)

---

## 5. Multi-tenant enterprise (institutes) — FUTURE

- **Isolation:** Postgres RLS + optional **Storage bucket prefix** per institute.
- **Branding:** CSS variables + logo URL stored institute row.
- **Support:** impersonation **only** with break-glass audit (future).

---

## 6. Extensibility

- **Feature flags** per user cohort.
- **Integration adapters** behind interfaces (swap LLM providers, OCR engines).
- **Exam profiles** data-driven to add JEE without forked codepaths.
- **Note processors** pluggable — add new PDF types without changing core pipeline.

---

## 7. Governance

- **ADR log** (`docs/adr/`) for irreversible choices.
- **Threat model** refresh on any new external integration.
- **Data classification:**
  - **Public:** syllabus snapshots (versioned).
  - **PII:** name, phone, email.
  - **UGC:** notes, chats, highlights — highest sensitivity, encrypt at rest.

---

## 8. Team topology (recommended)

- **Platform pod:** auth, DB, CI, observability
- **Learner pod:** checklist, dashboard, offline, PWA
- **AI pod:** tutor chat, note structuring, quiz generation, RAG
- **Content pod:** PDF pipeline, bulk import, viewer, search, download
- **Growth pod:** analytics, roadmap, motivation, quizzes

**Why:** reduces context switching; ownership maps to domains above.

---

## 9. Success measures (engineering)

- **MTTR** < 1h for SEV2 AI incidents (runbook + LangSmith).
- **Migration success rate** 100% on staging before prod.
- **RLS violation attempts** in CI = 0.
- **PDF processing success rate** > 95%.
- **Search relevance** > 80% top-3 results relevant.

---

*Canonical tech choices: `FINAL_ARCHITECTURE.md`. System flows: `SYSTEM_DESIGN.md`.*
