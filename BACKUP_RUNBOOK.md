# StudyOS — Backup & Restore Runbook

**Date:** 2026-05-18  
**Version:** 1.0  
**Purpose:** Step-by-step procedures for database backup and restore

---

## 1. Backup Strategy

### Automated Backups (Supabase)
- **Frequency:** Daily at 2:00 AM UTC
- **Retention:** 7 days (Free), 30 days (Pro)
- **Type:** Full database dump
- **Storage:** Supabase managed storage

### Manual Backups
Run before:
- Major migrations
- Schema changes
- Production deployments
- Data cleanup operations

---

## 2. Backup Procedures

### 2.1 Full Database Backup

```bash
# Connect to Supabase database
export DB_URL="postgresql://user:password@host:5432/postgres"

# Create backup
pg_dump -h $(echo $DB_URL | cut -d@ -f2 | cut -d: -f1) \
  -U $(echo $DB_URL | cut -d/ -f3 | cut -d: -f1) \
  -d studyos \
  -F c \
  -f "backup-$(date +%Y%m%d-%H%M%S).dump"

# Verify backup
pg_restore --list "backup-$(date +%Y%m%d-%H%M%S).dump" | head -20
```

### 2.2 Schema-Only Backup

```bash
pg_dump -h host -U user -d studyos --schema-only -f "schema-$(date +%Y%m%d).sql"
```

### 2.3 Data-Only Backup (Specific Tables)

```bash
pg_dump -h host -U user -d studyos \
  --data-only \
  --table=profiles \
  --table=subtopic_completions \
  --table=streaks \
  -f "data-$(date +%Y%m%d).sql"
```

### 2.4 Backup Verification

```bash
# Check backup file size
ls -lh backup-*.dump

# List backup contents
pg_restore --list backup-*.dump

# Test restore to temporary database
createdb test_restore
pg_restore -d test_restore backup-*.dump
psql -d test_restore -c "SELECT count(*) FROM profiles;"
dropdb test_restore
```

---

## 3. Restore Procedures

### 3.1 Full Database Restore

⚠️ **WARNING:** This will overwrite all existing data!

```bash
# 1. Stop application to prevent writes
docker compose -f docker/docker-compose.prod.yml stop api web

# 2. Drop and recreate database (if needed)
psql -h host -U user -d postgres -c "DROP DATABASE studyos;"
psql -h host -U user -d postgres -c "CREATE DATABASE studyos;"

# 3. Restore from backup
pg_restore -h host -U user -d studyos --clean --if-exists backup-YYYYMMDD-HHMMSS.dump

# 4. Run migrations to ensure schema is current
pnpm supabase migration up

# 5. Restart application
docker compose -f docker/docker-compose.prod.yml start api web

# 6. Verify restore
psql -h host -U user -d studyos -c "SELECT count(*) FROM profiles;"
curl https://api.studyos.app/health
```

### 3.2 Single Table Restore

```bash
# Restore specific table from backup
pg_restore -h host -U user -d studyos \
  --table=profiles \
  --data-only \
  backup-YYYYMMDD-HHMMSS.dump
```

### 3.3 Point-in-Time Recovery (Supabase Pro)

1. Go to Supabase Dashboard → Database → Backups
2. Select "Point-in-time recovery"
3. Choose target timestamp
4. Click "Restore to this point"
5. Wait for restoration to complete (5-15 minutes)
6. Verify data integrity

---

## 4. Backup Schedule

| Type | Frequency | Retention | Storage | Automation |
|------|-----------|-----------|---------|------------|
| **Full DB** | Daily (2 AM UTC) | 30 days | Supabase | ✅ Automated |
| **Manual** | Before migrations | 90 days | S3/GCS | ❌ Manual |
| **Schema** | Weekly | 90 days | Git + S3 | ❌ Manual |
| **Config** | On change | 90 days | Git | ✅ Versioned |

---

## 5. Disaster Recovery

### 5.1 RTO/RPO Targets

| Metric | Target | Current |
|--------|--------|---------|
| **RTO (Recovery Time Objective)** | <1 hour | ~30 minutes |
| **RPO (Recovery Point Objective)** | <24 hours | 24 hours (daily backups) |

### 5.2 Disaster Recovery Steps

1. **Assess the situation**
   - What failed? (DB, API, Web, Network)
   - When did it fail?
   - What data is affected?

2. **Stop all writes**
   ```bash
   docker compose -f docker/docker-compose.prod.yml stop api
   ```

3. **Restore from latest backup**
   - Follow Section 3.1

4. **Verify data integrity**
   ```bash
   psql -h host -U user -d studyos -c "SELECT count(*) FROM profiles;"
   psql -h host -U user -d studyos -c "SELECT count(*) FROM subtopic_completions;"
   ```

5. **Restart services**
   ```bash
   docker compose -f docker/docker-compose.prod.yml start api web
   ```

6. **Monitor for 1 hour**
   - Check health endpoints
   - Monitor error rates
   - Verify user access

---

## 6. Backup Testing

### Monthly Backup Test

```bash
# 1. Create test database
createdb backup_test

# 2. Restore latest backup
pg_restore -d backup_test latest-backup.dump

# 3. Verify data
psql -d backup_test -c "SELECT count(*) FROM profiles;"
psql -d backup_test -c "SELECT count(*) FROM subtopic_completions;"
psql -d backup_test -c "SELECT count(*) FROM streaks;"

# 4. Run test queries
psql -d backup_test -c "SELECT * FROM profiles LIMIT 5;"

# 5. Cleanup
dropdb backup_test
```

### Test Checklist
- [ ] Backup file exists and is not corrupted
- [ ] Restore completes without errors
- [ ] All tables are present
- [ ] Row counts match expected values
- [ ] Sample data is accessible
- [ ] Application connects successfully

---

## 7. Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| **DBA** | [TBD] | Database issues |
| **DevOps** | [TBD] | Infrastructure |
| **Engineering Lead** | [TBD] | All technical decisions |

---

## 8. Backup Monitoring

### Alerts
- **Backup failed:** Immediate notification
- **Backup size anomaly:** >20% change from baseline
- **Restore test failed:** Investigate within 1 hour
- **Storage >80%:** Plan cleanup or expansion

### Monitoring Commands
```bash
# Check backup status (Supabase API)
curl -s https://api.supabase.com/v1/projects/$PROJECT_ID/backups \
  -H "Authorization: Bearer $API_KEY"

# Check backup file age
find /backups -name "*.dump" -mtime +1 -ls
```
