# StudyOS Disaster Recovery Runbook

**Last Updated:** 2026-05-19
**RTO Target:** 15 minutes
**RPO Target:** 60 minutes

---

## Quick Reference

| Scenario | First Action | Escalation |
|---|---|---|
| Database down | Check `docker compose ps postgres` | Restore from backup |
| Redis down | Check `docker compose ps redis` | Restart with `docker compose up -d redis` |
| API down | Check `docker compose ps api` | Restart API container |
| Full outage | Run DR drill script | Contact on-call engineer |

---

## 1. Database Failure Recovery

### 1.1 Symptom: PostgreSQL Unreachable
```
ERROR: connection refused to database "studyos"
```

### 1.2 Diagnosis Steps
```bash
# Check container status
docker compose -f docker/docker-compose.yml ps postgres

# Check logs
docker compose -f docker/docker-compose.yml logs postgres --tail=100

# Test connection
psql "$STUDYOS_DATABASE_URL" -c "SELECT 1"
```

### 1.3 Recovery Steps

#### Option A: Container Restart (if data intact)
```bash
docker compose -f docker/docker-compose.yml restart postgres
# Wait for recovery
sleep 30
psql "$STUDYOS_DATABASE_URL" -c "SELECT 1"
```

#### Option B: Restore from Backup (if data corrupted)
```bash
# 1. Stop API to prevent writes
docker compose -f docker/docker-compose.yml stop api

# 2. Find latest backup
LATEST=$(ls -t /opt/studyos/backups/postgres/*.sql.gz | head -1)
echo "Restoring from: $LATEST"

# 3. Drop and recreate database
psql "$STUDYOS_DATABASE_URL" -c "DROP DATABASE studyos;"
psql "$STUDYOS_DATABASE_URL" -c "CREATE DATABASE studyos;"

# 4. Restore
zcat "$LATEST" | psql "$STUDYOS_DATABASE_URL"

# 5. Verify
psql "$STUDYOS_DATABASE_URL" -c "SELECT count(*) FROM profiles;"

# 6. Restart API
docker compose -f docker/docker-compose.yml start api
```

---

## 2. Redis Failure Recovery

### 2.1 Symptom: Redis Connection Refused
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

### 2.2 Recovery Steps
```bash
# 1. Check Redis status
docker compose -f docker/docker-compose.yml ps redis

# 2. Restart Redis
docker compose -f docker/docker-compose.yml restart redis

# 3. Verify
redis-cli -u "$STUDYOS_REDIS_URL" PING

# 4. Clear stale caches (optional)
redis-cli -u "$STUDYOS_REDIS_URL" FLUSHDB
```

---

## 3. API Service Failure Recovery

### 3.1 Symptom: API Returns 502/503
```
curl: (7) Failed to connect to localhost port 8000
```

### 3.2 Recovery Steps
```bash
# 1. Check API status
docker compose -f docker/docker-compose.yml ps api

# 2. Check logs
docker compose -f docker/docker-compose.yml logs api --tail=200

# 3. Restart API
docker compose -f docker/docker-compose.yml restart api

# 4. Verify health
curl -sf http://localhost:8000/v1/healthz
```

### 3.3 If Restart Fails
```bash
# 1. Stop current API
docker compose -f docker/docker-compose.yml stop api

# 2. Rebuild
docker compose -f docker/docker-compose.yml build api

# 3. Start fresh
docker compose -f docker/docker-compose.yml up -d api

# 4. Verify
curl -sf http://localhost:8000/v1/healthz
```

---

## 4. Full System Outage Recovery

### 4.1 Scenario: All services down
```bash
# 1. Run DR drill to assess damage
./scripts/dr/dr-drill.sh --quick

# 2. Check infrastructure
docker compose -f docker/docker-compose.yml ps

# 3. Start services in order
docker compose -f docker/docker-compose.yml up -d postgres redis
sleep 10  # Wait for DB to initialize

# 4. Verify database
psql "$STUDYOS_DATABASE_URL" -c "SELECT 1"

# 5. Start API
docker compose -f docker/docker-compose.yml up -d api
sleep 5

# 6. Verify API
curl -sf http://localhost:8000/v1/healthz

# 7. Start web
docker compose -f docker/docker-compose.yml up -d web

# 8. Run full DR drill
./scripts/dr/dr-drill.sh --full
```

---

## 5. Data Corruption Recovery

### 5.1 Symptom: Inconsistent data, constraint violations
```
ERROR: duplicate key value violates unique constraint
```

### 5.2 Recovery Steps
```bash
# 1. Identify corruption scope
psql "$STUDYOS_DATABASE_URL" -c "SELECT count(*) FROM profiles;"
psql "$STUDYOS_DATABASE_URL" -c "SELECT count(*) FROM subtopic_completions;"

# 2. Stop writes
docker compose -f docker/docker-compose.yml stop api

# 3. Restore from last known good backup
LATEST=$(ls -t /opt/studyos/backups/postgres/*.sql.gz | head -1)
zcat "$LATEST" | psql "$STUDYOS_DATABASE_URL"

# 4. Verify data integrity
psql "$STUDYOS_DATABASE_URL" -c "SELECT count(*) FROM profiles;"

# 5. Restart services
docker compose -f docker/docker-compose.yml start api
```

---

## 6. Backup Verification

### 6.1 Manual Verification
```bash
# List backups
ls -lh /opt/studyos/backups/postgres/

# Verify integrity
gzip -t /opt/studyos/backups/postgres/latest.sql.gz

# Check backup size (should be > 0)
du -h /opt/studyos/backups/postgres/latest.sql.gz
```

### 6.2 Automated Verification
```bash
# Run DR drill (includes backup verification)
./scripts/dr/dr-drill.sh --quick
```

---

## 7. Escalation Matrix

| Severity | Response Time | Action | Contact |
|---|---|---|---|
| P1 - Full outage | 5 min | DR drill + restore | On-call engineer |
| P2 - Partial outage | 15 min | Restart affected service | Dev team lead |
| P3 - Degraded | 1 hour | Investigate + fix | Dev team |
| P4 - Minor | 24 hours | Schedule fix | Backlog |

---

## 8. Post-Incident Checklist

- [ ] Document incident timeline
- [ ] Identify root cause
- [ ] Verify data integrity
- [ ] Update runbook if needed
- [ ] Schedule post-mortem
- [ ] Update monitoring/alerts
- [ ] Test DR procedures again
