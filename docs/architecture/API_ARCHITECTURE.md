# StudyOS — API Architecture

**Principles:** contract-first, **least privilege**, idempotent webhooks, **RFC 7807**-style errors (`application/problem+json` where feasible), **versioned** external integrations.

---

## 1. API surface classes

| Class | Transport | Auth | Examples |
|-------|-----------|------|------------|
| **A — Next BFF** | HTTPS JSON / SSE | User session cookie + CSRF for mutating cookie sessions | `/api/ai/chat`, `/api/sync/push`, `/api/roadmap/request` |
| **B — Supabase Data** | HTTPS PostgREST | User JWT, RLS | Direct from browser for simple CRUD where policies proven |
| **C — Edge Functions** | HTTPS JSON | Service secret **or** verified JWT per route | `/functions/v1/razorpay-webhook` |
| **D — Realtime** | WebSocket | User JWT channel filter | progress updates, job status |
| **E — Third-party** | HTTPS | API keys server-side only | Razorpay server, Twilio, YouTube |

**Decision:** Prefer **B** for CRUD that is **purely user-scoped** and already encoded in RLS. Use **A** when combining **secrets**, **multi-step orchestration**, or **non-Postgres** side effects.

---

## 2. Naming and conventions

- **REST-ish** Route Handlers: plural nouns, verbs in subpaths only when unavoidable (`POST /api/roadmap/regenerate`).  
- **Query params:** `cursor`, `limit` (max 100 default 20).  
- **Ids:** UUID v7 or ULID **generated server-side** for time-ordered rows (optional optimization for hot tables).  
- **Headers:**  
  - `X-Request-Id` (echo from client or generate)  
  - `X-Institute-Slug` optional; middleware may ignore if host-based tenant used

---

## 3. AuthN / AuthZ on BFF

1. `createServerClient` from `@supabase/ssr` reads JWT.  
2. `requireUser()` throws **401** problem if absent.  
3. `requireRole(['teacher'])` throws **403** if profile role insufficient.  
4. **Institute scope:** `assertInstituteAccess(userId, instituteId)` before any batch read.

---

## 4. Error model

```typescript
// Conceptual — shared in packages/api-contracts
type Problem = {
  type: string;      // URI identifying error kind
  title: string;
  status: number;
  detail?: string;
  instance?: string; // request id
  errors?: { field: string; message: string }[];
};
```

**Why:** stable client handling vs ad-hoc `{ error: string }`.

---

## 5. Idempotency

- **Mutations that enqueue work:** client sends `Idempotency-Key` header (UUID); stored in Redis 24h with response replay.  
- **Webhooks:** key = provider `event_id`.

---

## 6. Streaming

- **SSE** for AI token streams (`text/event-stream`).  
- **Backpressure:** close stream on client disconnect; LangGraph cancellation token wired.

---

## 7. Pagination patterns

- **Keyset** pagination on `(created_at, id)` for chat messages and events.  
- **Offset** only for admin tables < 10k rows.

---

## 8. Rate limits (HTTP)

| Route group | Default |
|-------------|---------|
| `/api/ai/*` | 20 req/min/user free; higher paid |
| `/api/sync/*` | 60 req/min/user |
| Webhooks | 1000/min/IP + signature required |

---

## 9. Public vs private

| Endpoint | Visibility |
|----------|--------------|
| `GET /api/public/syllabus/:examProfileId` | Public CDN-cacheable (immutable version in path) |
| `/api/**` other | Authenticated |

**Why version in path:** invalidates CDN when NTA updates syllabus.

---

## 10. OpenAPI strategy

- Generate **OpenAPI 3.1** from Zod routes using a lightweight tool (or maintain hand-written `openapi.yaml` for external partners only).  
- Internal frontends consume **shared Zod** only—OpenAPI mainly for **future public API** (Phase 8+).

---

## 11. Deprecation

- **`Deprecation` header** on sunset routes; minimum 90 days notice for any external partner (none at launch).

---

*Maps to `SYSTEM_DESIGN.md` request flows.*
