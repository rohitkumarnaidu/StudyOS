# StudyOS — Risk Analysis

**Method:** Repository-only review of documentation, structure, and stated external dependencies. No penetration testing or runtime assessment was possible (no application).

---

## 1. Critical: specification vs implementation drift

| Risk | Impact | Evidence |
|------|--------|----------|
| **False sense of completion** | Teams ship or market based on checklists; security and UX gaps go unnoticed | `ROADMAP.md` MVP section uses `[✅]` while workspace has **no** application source |
| **Unverifiable claims** | Audit failures, investor/engineering mistrust | No commits, tests, or migrations to map checklist items to |

**Mitigation:** Track delivery in an issue system with links to PRs; keep roadmap checkboxes strictly tied to merged code.

---

## 2. Security and privacy (design is strong; execution is zero)

| Risk | Impact | Notes |
|------|--------|-------|
| **Secrets in documentation** | Credential leakage, scraping | `ROADMAP.md` / `APP_PROMPT.prompt` show **placeholder** env patterns; real keys must never mirror docs |
| **Student notes + LLM** | DPDP / GDPR exposure if logs retain content | Docs say minimize logging — must be enforced in implementation |
| **BYOK in browser** | XSS or malicious extension could exfiltrate keys | `SKILL_SECURITY.md` mandates Dexie encryption — still high sensitivity |
| **Shared “StudyOS Free AI” key** | Abuse, cost blowups, account sharing | Mentioned in APP_MAP; needs strict rate limits and anomaly detection |
| **File uploads** | Malware, polyglots, SSRF if server fetches URLs | Docs mention magic-byte validation; Edge + Storage policies must enforce |
| **Prompt injection** | Wrong medical/educational advice, jailbreaks | Mitigations documented (XML sandwich, length limits) — must be uniform across all LLM entry points |
| **RLS mistakes** | Cross-tenant data leaks for institutes | High impact when B2B launches; requires automated RLS tests |

---

## 3. Product and compliance

| Risk | Impact |
|------|--------|
| **Medical / exam stress content** | Harm if AI tone is wrong; reputational and legal sensitivity in India | MASTER_README acknowledges mental health — needs content policy + escalation paths |
| **Minors** | Parental consent and data processing obligations | ROADMAP mentions DPDP and under-18 consent — workflow not built |
| **AI accuracy** | Student harm if hallucinations on high-stakes topics | RAG + citations planned; until live, risk is unchecked |
| **Rank predictors / cutoffs** | Misleading predictions → distress or disputes | Disclaimers in prompts; still a product/legal review area |

---

## 4. Technical and operational

| Risk | Impact |
|------|--------|
| **Vendor concentration** | Supabase + Vercel outage blocks entire product | Docs mention fallbacks for LLMs, not for primary BaaS |
| **Cost volatility** | LLM spend scales superlinearly with WAU | No code-level budgets/circuit breakers visible here |
| **NotebookLM / Google API changes** | Broken exports or workflows | NotebookLM API explicitly “not public” in roadmap |
| **WhatsApp template / policy changes** | Notifications silently fail | Meta/Twilio compliance overhead |
| **External corpus dependency** | 483 PDFs on GitHub/Drive — licensing, availability, indexing cost | Described in MASTER_README |

---

## 5. Maintainability

| Risk | Impact |
|------|--------|
| **Documentation sprawl** | Single source of truth erodes (APP_MAP vs ROADMAP vs MASTER vs prompts) | Inconsistencies already noted (Next vs Vite, skill file names) |
| **Binary `.skill` blobs** | Hard to diff in PRs; opaque to standard review | `skills-claude/` contents not text-reviewable here |
| **Huge prompt file** | Copy-paste errors when chunking work | `APP_PROMPT.prompt` is very large — consider modular prompts with version pins |

---

## 6. Scalability (when built)

| Risk | Impact |
|------|--------|
| **Hot rows on progress** | Write amplification on popular tables (`subtopic_completions`, `events`) | Needs partitioning or aggregation strategy at scale |
| **Vector index size + cost** | pgvector maintenance, re-embedding on syllabus change | Planned but operationally heavy |
| **Edge function timeouts** | Long LLM or PDF jobs | May need async job queue beyond simple Edge invocations |
| **Multi-region** | Latency for India users if DB is far | ROADMAP mentions multi-region as future — early single-region choice matters |

---

## 7. Risk summary matrix

| Area | Severity (if built naively) | Readiness in-repo |
|------|----------------------------|-------------------|
| Data isolation (RLS) | Critical | Spec only |
| API key handling | Critical | Spec + patterns in SKILL_SECURITY |
| AI safety / accuracy | High | Spec + agent designs |
| Cost control | High | Mentioned, not implemented |
| Doc/process drift | Medium | Observed now |

---

*This risk register should be re-run after the first production deploy with threat modeling (`SKILL_SECURITY.md` aligns with a formal review).*
