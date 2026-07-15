# StudyOS — Deployment Guide

**Date:** 2026-05-18  
**Version:** 1.0  
**Target:** Enterprise production deployment

---

## Overview

This guide covers deploying StudyOS to production environments. The platform consists of:
- **Web App:** Next.js 16 (React 19) — BFF + frontend
- **API:** FastAPI (Python 3.12) — business logic
- **Database:** PostgreSQL via Supabase
- **Cache:** Redis (optional, recommended for production)

---

## Deployment Options

### Option 1: Vercel + Supabase (Recommended)
- **Web:** Deploy to Vercel (optimized for Next.js)
- **API:** Deploy to Supabase Edge Functions or separate hosting
- **DB:** Supabase managed PostgreSQL
- **Best for:** MVP, rapid iteration, low ops overhead

### Option 2: Docker + Cloud Provider
- **Web + API:** Docker containers on AWS/GCP/Azure
- **DB:** Managed PostgreSQL (RDS, Cloud SQL)
- **Cache:** Managed Redis (ElastiCache, Memorystore)
- **Best for:** Enterprise control, compliance requirements

### Option 3: Self-Hosted
- **All components:** On-premise infrastructure
- **Best for:** Data sovereignty, air-gapped environments

---

## Environment Configuration

### Required Environment Variables

#### Web App (`apps/web/.env.production`)
```env
# Application
NEXT_PUBLIC_APP_URL=https://app.studyos.app
NEXT_PUBLIC_API_URL=https://api.studyos.app/v1

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Auth
STUDYOS_JWT_SECRET=your-jwt-secret-min-32-chars
STUDYOS_JWT_ISSUER=studyos-production

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
NEXT_PUBLIC_POSTHOG_KEY=your-posthog-key
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com

# Feature Flags
STUDYOS_FEATURE_FLAGS_ENABLED=true
```

#### API (`apps/api/.env.production`)
```env
# Application
STUDYOS_APP_ENV=production
STUDYOS_TRUSTED_HOSTS=api.studyos.app,localhost

# Database
STUDYOS_DATABASE_URL=postgresql://user:pass@host:5432/studyos

# Auth
STUDYOS_JWT_SECRET=your-jwt-secret-min-32-chars
STUDYOS_JWT_ISSUER=studyos-production
STUDYOS_ACCESS_TOKEN_TTL_SECONDS=900
STUDYOS_REFRESH_TOKEN_TTL_SECONDS=604800

# AI Providers
STUDYOS_AI_PRIMARY_PROVIDER=openai
STUDYOS_AI_OPENAI_API_KEY=your-openai-key
STUDYOS_AI_OLLAMA_BASE_URL=http://localhost:11434
STUDYOS_AI_MEMORY_MAX_MESSAGES=10

# Cache
STUDYOS_REDIS_URL=redis://localhost:6379/0

# Monitoring
STUDYOS_OTLP_ENDPOINT=http://localhost:4318
STUDYOS_SENTRY_DSN=https://your-sentry-dsn

# Security
STUDYOS_RATE_LIMIT_PER_MINUTE=60
STUDYOS_CORS_ORIGINS=https://app.studyos.app
```

---

## Docker Deployment

### Building Images
```bash
# Build all images
docker compose -f docker/docker-compose.yml build

# Build specific service
docker compose -f docker/docker-compose.yml build api
docker compose -f docker/docker-compose.yml build web
```

### Running in Production
```bash
# Start all services
docker compose -f docker/docker-compose.prod.yml up -d

# Check status
docker compose -f docker/docker-compose.prod.yml ps

# View logs
docker compose -f docker/docker-compose.prod.yml logs -f api
docker compose -f docker/docker-compose.prod.yml logs -f web
```

### Docker Compose Production Config
```yaml
# docker/docker-compose.prod.yml
version: '3.8'

services:
  api:
    build:
      context: ../apps/api
      dockerfile: Dockerfile
    environment:
      - STUDYOS_APP_ENV=production
      - STUDYOS_DATABASE_URL=${DATABASE_URL}
      - STUDYOS_JWT_SECRET=${JWT_SECRET}
      - STUDYOS_REDIS_URL=${REDIS_URL}
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  web:
    build:
      context: ../apps/web
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_APP_URL=${APP_URL}
      - NEXT_PUBLIC_API_URL=${API_URL}
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    depends_on:
      - api
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

---

## Database Migrations

### Running Migrations
```bash
# Apply all pending migrations
pnpm supabase migration up

# Reset database (development only)
pnpm supabase db reset

# Generate types from schema
pnpm supabase gen types typescript --local > apps/web/src/types/database.ts
```

### Migration Best Practices
1. **Test migrations on staging first**
2. **Always provide rollback scripts**
3. **Use idempotent migrations where possible**
4. **Never drop columns in production without backup**
5. **Run migrations during low-traffic windows**

---

## Health Checks

### API Health Endpoint
```
GET /health
Response: { "status": "ok", "version": "1.0.0", "database": "connected" }
```

### Web Health Check
```
GET /
Response: 200 OK with HTML
```

### Monitoring Endpoints
```
GET /metrics          # Prometheus metrics
GET /ready            # Readiness probe
GET /health/detailed  # Detailed health with dependencies
```

---

## Scaling Strategy

### Horizontal Scaling
| Component | Scaling Method | Trigger |
|-----------|---------------|---------|
| **Web** | Add more instances | CPU > 70%, Response time > 500ms |
| **API** | Add more instances | CPU > 70%, Queue depth > 100 |
| **DB** | Read replicas | Read latency > 100ms |
| **Redis** | Cluster mode | Memory > 80% |

### Vertical Scaling
| Component | Current | Recommended Max |
|-----------|---------|-----------------|
| **Web** | 1GB RAM, 1 CPU | 4GB RAM, 2 CPU |
| **API** | 512MB RAM, 0.5 CPU | 2GB RAM, 2 CPU |
| **DB** | 1GB RAM | 8GB RAM (Supabase Pro) |
| **Redis** | 256MB | 2GB |

---

## Backup Strategy

### Database Backups
- **Supabase:** Automatic daily backups (7-day retention)
- **Manual:** `pg_dump` before major migrations
- **Point-in-time:** Enable PITR for production

### Backup Schedule
| Type | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| **Full DB** | Daily | 30 days | S3/GCS |
| **Incremental** | Hourly | 7 days | S3/GCS |
| **Config files** | On change | 90 days | Git + S3 |
| **Logs** | Continuous | 90 days | CloudWatch/Stackdriver |

### Restore Procedure
```bash
# Restore from backup
pg_restore -h host -U user -d studyos backup.dump

# Verify restore
psql -h host -U user -d studyos -c "SELECT count(*) FROM profiles;"
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (API 90%+, Web 80%+)
- [ ] Lint and typecheck clean
- [ ] Database migrations tested on staging
- [ ] Environment variables configured
- [ ] SSL certificates valid
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented

### Deployment
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Deploy to production
- [ ] Verify health checks passing
- [ ] Monitor error rates for 15 minutes
- [ ] Verify critical user journeys

### Post-Deployment
- [ ] Check Sentry for new errors
- [ ] Verify metrics dashboards
- [ ] Test critical user flows
- [ ] Update changelog
- [ ] Notify team of deployment

---

## Rollback Procedure

### Quick Rollback
```bash
# Docker rollback
docker compose -f docker/docker-compose.yml up -d --force-recreate api:previous-tag

# Database rollback
# 1. Stop application
# 2. Restore from backup
# 3. Run reverse migration if needed
# 4. Restart application
```

### Rollback Decision Tree
```
New deployment → Errors detected?
  ├─ No → Monitor for 1 hour → Done
  └─ Yes → Severity?
      ├─ Critical (data loss, downtime) → Immediate rollback
      ├─ High (broken feature) → Rollback within 15 min
      └─ Low (minor bug) → Fix forward if possible
```

---

## Troubleshooting

### Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **DB connection failed** | 500 errors on API | Check DATABASE_URL, network rules |
| **JWT validation fails** | 401 on all requests | Verify JWT_SECRET matches between web and API |
| **Redis connection timeout** | Slow responses | Check Redis URL, network security groups |
| **CORS errors** | Browser console errors | Add origin to CORS_ORIGINS |
| **Migration failed** | Schema mismatch | Check migration order, rollback and retry |

### Debug Commands
```bash
# Check API logs
docker logs studyos-api --tail 100

# Check database connections
psql -h host -U user -d studyos -c "SELECT count(*) FROM pg_stat_activity;"

# Test Redis connection
redis-cli -h host -p 6379 ping

# Check SSL certificate
openssl s_client -connect api.studyos.app:443 -servername api.studyos.app
```
