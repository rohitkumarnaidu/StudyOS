# StudyOS — Documentation Index

**Date:** 2026-05-18  
**Version:** 2.0  
**Purpose:** Single entry point for all project documentation

---

## Quick Start

| Document | Purpose | Audience |
|----------|---------|----------|
| [README.md](../README.md) | Project overview | Everyone |
| [ONBOARDING.md](../ONBOARDING.md) | New developer setup | New hires |
| [AGENTS.md](../AGENTS.md) | AI assistant guide | AI tools |
| [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) | Production deployment | DevOps |

---

## Architecture

| Document | Purpose | Status |
|----------|---------|--------|
| [FINAL_ARCHITECTURE.md](architecture/FINAL_ARCHITECTURE.md) | Canonical tech decisions | ✅ Current |
| [SYSTEM_DESIGN.md](architecture/SYSTEM_DESIGN.md) | C4 diagrams, request flows | ✅ Current |
| [ENTERPRISE_ARCHITECTURE.md](architecture/ENTERPRISE_ARCHITECTURE.md) | Business domains, NFRs | ✅ Current |
| [MONOREPO_STRUCTURE.md](architecture/MONOREPO_STRUCTURE.md) | Directory layout | ✅ Current |
| [API_ARCHITECTURE.md](architecture/API_ARCHITECTURE.md) | BFF pattern, error model | ✅ Current |
| [AI_SYSTEM_DESIGN.md](architecture/AI_SYSTEM_DESIGN.md) | LangGraph, model routing | ✅ Current |
| [RESTRUCTURING_DECISIONS.md](architecture/RESTRUCTURING_DECISIONS.md) | Monorepo architecture | ✅ Current |

---

## Database

| Document | Purpose | Status |
|----------|---------|--------|
| [DATABASE_PLAN.md](architecture/DATABASE_PLAN.md) | Scaling, backups, governance | ✅ Current |
| [DATABASE_SCHEMA_PLAN.md](architecture/DATABASE_SCHEMA_PLAN.md) | Schema, RLS, indexing | ✅ Current |
| [ERD.md](database/ERD.md) | Entity relationship diagram | ✅ Current |
| [MIGRATIONS_AND_SEEDS.md](database/MIGRATIONS_AND_SEEDS.md) | Migration workflow | ✅ Current |
| [INDEXING_AND_QUERIES.md](database/INDEXING_AND_QUERIES.md) | Index strategy | ✅ Current |

---

## Engineering

| Document | Purpose | Status |
|----------|---------|--------|
| [ENGINEERING.md](engineering/ENGINEERING.md) | Code standards | ✅ Current |
| [TESTING_GUIDELINES.md](engineering/TESTING_GUIDELINES.md) | Testing architecture | ✅ Current |
| [PERFORMANCE_REPORT.md](engineering/PERFORMANCE_REPORT.md) | Performance analysis | ✅ Current |
| [PRODUCTION_READINESS.md](engineering/PRODUCTION_READINESS.md) | Production audit | ✅ Current |
| [ENTERPRISE_READINESS.md](engineering/ENTERPRISE_READINESS.md) | Readiness checklist | ✅ Current |
| [ADR-001-fastapi-service-layer.md](engineering/ADR-001-fastapi-service-layer.md) | Architecture decision | ✅ Current |

---

## Product

| Document | Purpose | Status |
|----------|---------|--------|
| [APP_MAP.md](product/plan/APP_MAP.md) | Feature mind map | ✅ Current (pruned) |
| [NEET_2026_Complete_Syllabus_Guide.md](product/plan/NEET_2026_Complete_Syllabus_Guide.md) | Curriculum guide | ✅ Current |
| [PHASE_0_COMPLETION_REPORT.md](product/plan/PHASE_0_COMPLETION_REPORT.md) | Phase 0 status | ✅ Current (updated) |
| [PHASE_1_PROGRESS.md](product/plan/PHASE_1_PROGRESS.md) | Phase 1 status | ✅ Current |
| [FEATURE_PRIORITY.md](architecture/FEATURE_PRIORITY.md) | Feature ranking | ✅ Current |

---

## Skills (AI Coding Assistants)

| Document | Purpose | Status |
|----------|---------|--------|
| [SKILL_FRONTEND.md](product/skills-app/SKILL_FRONTEND.md) | Next.js 16 patterns | ✅ Current (rewritten) |
| [SKILL_BACKEND.md](product/skills-app/SKILL_BACKEND.md) | FastAPI patterns | ✅ Current (rewritten) |
| [SKILL_DATABASE.md](product/skills-app/SKILL_DATABASE.md) | DB/RLS patterns | ✅ Current |
| [SKILL_SECURITY.md](product/skills-app/SKILL_SECURITY.md) | Security patterns | ✅ Current |
| [SKILL_ANALYTICS.md](product/skills-app/SKILL_ANALYTICS.md) | Analytics patterns | ✅ Current |
| [SKILL_DESIGN.md](product/skills-app/SKILL_DESIGN.md) | Design system | ✅ Current (updated) |
| [SKILL_NEET_DOMAIN.md](product/skills-app/SKILL_NEET_DOMAIN.md) | NEET domain knowledge | ✅ Current |
| [skills-claude/*.skill](product/skills-claude/) | Claude Code skills (6) | ✅ Verified |

---

## DevOps

| Document | Purpose | Status |
|----------|---------|--------|
| [DEVOPS_PLAN.md](architecture/DEVOPS_PLAN.md) | DevOps strategy | ✅ Current |
| [MONITORING_SETUP.md](../docker/MONITORING_SETUP.md) | Grafana/Prometheus | ✅ Current |
| [BACKUP_RUNBOOK.md](../BACKUP_RUNBOOK.md) | Backup/restore | ✅ Current |
| [load-test.js](../docker/load-test.js) | k6 load test script | ✅ Current |

---

## Security

| Document | Purpose | Status |
|----------|---------|--------|
| [AUTHENTICATION.md](security/AUTHENTICATION.md) | Auth strategy | ✅ Current |
| [SUPABASE_GOOGLE.md](auth/SUPABASE_GOOGLE.md) | Google OAuth setup | ✅ Current |

---

## Audit Reports

| Document | Purpose | Date |
|----------|---------|------|
| [FINAL_AUDIT_REPORT.md](../FINAL_AUDIT_REPORT.md) | Complete audit | 2026-05-18 |
| [SECURITY_AUDIT.md](../SECURITY_AUDIT.md) | Security findings | 2026-05-18 |
| [SCALABILITY_REPORT.md](../SCALABILITY_REPORT.md) | Scaling analysis | 2026-05-18 |
| [TECH_DEBT_REPORT.md](../TECH_DEBT_REPORT.md) | Technical debt | 2026-05-18 |
| [FINAL_RECOMMENDATIONS.md](../FINAL_RECOMMENDATIONS.md) | Action plan | 2026-05-18 |

---

## Design

| Document | Purpose | Status |
|----------|---------|--------|
| [DESIGN.md](../apps/web/DESIGN.md) | Frontend design system | ✅ Current |

---

## Archive (Historical)

| Document | Purpose | Archived |
|----------|---------|----------|
| [archive/architecture/](architecture/) | Pre-implementation analysis | Yes |
| [archive/phase-0/](archive/phase-0/) | Phase 0 execution docs | Yes |
| [archive/pre-implementation/](archive/pre-implementation/) | Outdated roadmaps/plans | Yes |

---

## Documentation Guidelines

### Adding New Docs
1. Place in appropriate category folder
2. Add to this index
3. Update cross-references

### Updating Docs
1. Check if document is still relevant
2. Update content and date
3. Remove outdated sections

### Archiving Docs
1. Move to `archive/` folder
2. Add "ARCHIVED" header with date
3. Link to current replacement

---

## Role-Based Reading Paths

### New Developer
1. README.md
2. ONBOARDING.md
3. AGENTS.md
4. ENGINEERING.md

### Frontend Developer
1. DESIGN.md
2. TESTING_GUIDELINES.md
3. API_ARCHITECTURE.md

### Backend Developer
1. DATABASE_PLAN.md
2. API_ARCHITECTURE.md
3. AI_SYSTEM_DESIGN.md

### DevOps Engineer
1. DEPLOYMENT_GUIDE.md
2. MONITORING_SETUP.md
3. BACKUP_RUNBOOK.md

### Product Manager
1. APP_MAP.md
2. FEATURE_PRIORITY.md
3. FINAL_RECOMMENDATIONS.md
