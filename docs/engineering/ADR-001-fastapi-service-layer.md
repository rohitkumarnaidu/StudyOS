# ADR 001 — FastAPI service layer alongside Next.js and Supabase

## Status

Accepted (2026-05-13)

## Context

Original StudyOS specs emphasized **Next.js Route Handlers** and **Supabase Edge Functions** for AI and webhooks. The team asked whether **FastAPI** should be introduced for MVP vs future enterprise scale.

## Decision

Introduce **`apps/api` (FastAPI)** as the **primary service-layer** for:

- **AI orchestration** (LangGraph / tool calls / streaming SSE) without Edge CPU/time limits.  
- **Webhooks** and **signature verification** with predictable raw-body handling.  
- **Background-friendly** endpoints that pair with a queue (Inngest/Celery) later.  

**Retain:**

- **Next.js (`apps/web`)** for UI, SSR, marketing routes, and thin BFF endpoints when appropriate.  
- **Supabase** (planned) for **Auth**, **Postgres + RLS**, **Storage**, **Realtime**, and **short** Edge Functions where Deno is ideal (e.g. Razorpay webhook fan-out if desired).

## Rationale

1. **Python ecosystem** leads for ML/AI agent iteration velocity and hiring pool at scale.  
2. **FastAPI** provides OpenAPI-first design, async stack, and excellent typing discipline with **mypy + ruff**.  
3. Clear **separation of concerns**: browser and Next focus on UX; API service focuses on orchestration and trust boundaries.  
4. Avoids overloading Next.js server with long CPU-bound or multi-step agent graphs.

## Consequences

- **Two runtimes** in production (Node + Python): requires container orchestration discipline (see `docker/`).  
- **Shared contracts** should evolve via **OpenAPI + Zod** generation in a later milestone (not blocking MVP shell).  
- CI must run **both** JS and Python pipelines (see `.github/workflows/ci.yml`).

## Alternatives considered

- **Node-only BFF**: simpler operationally; weaker story for heavy AI batch + some teams’ preference for Python in research/ML.  
- **Supabase Edge only**: great for short requests; poor fit for long agent runs and complex native deps.
