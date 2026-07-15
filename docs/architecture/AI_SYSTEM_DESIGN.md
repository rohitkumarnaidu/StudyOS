# StudyOS — AI System Design

**Goals:** AI-first UX, **grounded** tutoring where claimed, **measurable** quality, **controlled** spend, **safe** handling of student content.

---

## 1. Runtime topology

| Workload | Where it runs | Why |
|----------|---------------|-----|
| Tutor chat (platform) | Next **Node** Route Handler + LangGraph | Streaming, longer timeouts, secret access |
| Tutor chat (BYOK) | **Browser → vendor API** | Keys never touch StudyOS servers |
| Roadmap / heavy extraction | **Inngest worker** | Minutes-long CPU / multi-step without blocking HTTP |
| NCERT / corpus indexing | Worker + **batch embed** | Throughput, retries |
| Webhook-sized AI | Edge Function only if < few seconds | Keep Edge thin |

---

## 2. LangGraph design

**Packages:** `packages/ai`

```
packages/ai/
├── graphs/
│   ├── tutor.graph.ts
│   ├── roadmap.graph.ts
│   ├── quiz.graph.ts
│   └── extraction.graph.ts
├── tools/
│   ├── ncert-retrieval.tool.ts
│   ├── syllabus-lookup.tool.ts
│   └── pyq-retrieval.tool.ts
├── prompts/
│   └── ... (versioned templates)
├── models/
│   └── router.ts
├── schemas/
│   └── zod/*.ts
└── tracing/
    └── langsmith.ts
```

**Principles**

- **One graph per product surface** (avoid mega-graph).  
- **Tool allowlists** per graph; tools are thin wrappers over SQL/pgvector queries.  
- **State** serialized to DB at **superstep** boundaries for long runs (roadmap).

---

## 3. Model routing (policy)

| Task class | Primary | Fallback | Notes |
|------------|---------|----------|-------|
| Simple Q&A | Fast OSS/API (e.g. Groq-class) | Haiku-class | Cost-sensitive |
| Tutor with RAG | Sonnet-class or GPT-4.1-class | Second vendor | Quality-sensitive |
| Roadmap / structured JSON | Strong model | Second strong | **JSON mode** + Zod repair pass max 1 |
| Vision / messy OCR assist | Gemini-class or GPT-4.1 vision | other | Only when user uploads image to **platform** path |

**Router inputs:** `task_class`, `user_tier`, `locale`, `latency_slo`, `institute_policy` (B2B may restrict vendors).

---

## 4. RAG pipeline

1. **Ingest:** chunk NCERT / institute PDFs → `ncert_chunks` with `embedding`.  
2. **Retrieve:** hybrid **keyword + vector** optional later; start vector-only with `chapter_id` filter.  
3. **Generate:** system prompt mandates citations `[source: chunk_id]`; post-validator strips uncited claims for “strict mode”.  
4. **Eval:** periodic offline eval set (held-out questions) — **Phase 4+**.

---

## 5. Safety and compliance

- **Prompt injection:** structured user blocks + system instruction to treat user content as untrusted data.  
- **Medical accuracy:** disclaimers; “verify with NCERT” links; escalate uncertain answers to refusal.  
- **PII in prompts:** scrub emails/phones from notes before server-side LLM calls.  
- **Logging:** store **hashes** of prompts optional; never store BYOK keys.

---

## 6. Caching

- **Semantic cache** optional: Redis key = `hash(normalized_question + chapter_id + model)` → TTL 24h for idempotent factual snippets.  
- **Invalidate** on syllabus version bump.

---

## 7. Cost controls

- Pre-flight **token estimator** rough cut; hard cap per request.  
- Per-user **daily budget** table for platform AI; **HTTP 429** with problem+json `insufficient_quota`.  
- Institute **pooled budget** for B2B.

---

## 8. Human-in-the-loop (future)

- Teacher **approved notes** promoted to institute corpus with separate embedding namespace.  
- **Red-team** queue for flagged assistant messages (platform_admin tooling).

---

## 9. Testing AI

- **Golden tests:** fixed prompts + schema snapshot (not exact tokens).  
- **Contract tests:** tools return typed rows; graph exits `success | fail`.  
- **Load tests:** concurrent SSE sessions ≤ target on staging.

---

*See `FINAL_ARCHITECTURE.md` § AI and `SYSTEM_DESIGN.md` § flows.*
