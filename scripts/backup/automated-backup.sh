#!/usr/bin/env bash
# Automated PostgreSQL backup script for StudyOS
# Usage: ./automated-backup.sh [full|incremental|schema-only]
# Runs via cron: 0 2 * * * /opt/studyos/scripts/backup/automated-backup.sh full

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${STUDYOS_BACKUP_DIR:-/opt/studyos/backups}"
DB_URL="${STUDYOS_DATABASE_URL:-}"
RETENTION_DAYS="${STUDYOS_BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_TYPE="${1:-full}"

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1"
}

validate_config() {
    if [ -z "$DB_URL" ]; then
        log "ERROR: STUDYOS_DATABASE_URL not set"
        exit 1
    fi

    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/postgres"
    mkdir -p "$BACKUP_DIR/redis"
    mkdir -p "$BACKUP_DIR/logs"
}

backup_postgres() {
    local backup_file="$BACKUP_DIR/postgres/studyos_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"
    local log_file="$BACKUP_DIR/logs/postgres_backup_${TIMESTAMP}.log"

    log "Starting PostgreSQL ${BACKUP_TYPE} backup..."

    case "$BACKUP_TYPE" in
        full)
            pg_dump "$DB_URL" | gzip > "$backup_file" 2>> "$log_file"
            ;;
        schema-only)
            pg_dump --schema-only "$DB_URL" | gzip > "$backup_file" 2>> "$log_file"
            ;;
        data-only)
            pg_dump --data-only "$DB_URL" | gzip > "$backup_file" 2>> "$log_file"
            ;;
        *)
            log "ERROR: Unknown backup type: $BACKUP_TYPE"
            exit 1
            ;;
    esac

    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log "PostgreSQL backup completed: $backup_file ($size)"
        echo "$backup_file"
    else
        log "ERROR: PostgreSQL backup failed or produced empty file"
        exit 1
    fi
}

backup_redis() {
    local redis_url="${STUDYOS_REDIS_URL:-redis://localhost:6379/0}"
    local backup_file="$BACKUP_DIR/redis/studyos_redis_${TIMESTAMP}.rdb"
    local log_file="$BACKUP_DIR/logs/redis_backup_${TIMESTAMP}.log"

    log "Starting Redis backup..."

    # Trigger BGSAVE and wait for completion
    redis-cli -u "$redis_url" BGSAVE 2>> "$log_file"
    sleep 5

    # Check if save is in progress
    local saving=$(redis-cli -u "$redis_url" LASTSAVE 2>> "$log_file")
    if [ $? -eq 0 ]; then
        log "Redis BGSAVE triggered, last save timestamp: $saving"
    else
        log "WARNING: Redis BGSAVE may have failed, attempting dump anyway"
    fi

    # Copy RDB file if accessible (requires volume mount in Docker)
    if [ -f "/data/dump.rdb" ]; then
        cp "/data/dump.rdb" "$backup_file"
        log "Redis backup completed: $backup_file"
    else
        log "WARNING: Redis dump.rdb not found at /data/dump.rdb"
        log "Redis backup skipped (requires volume access)"
    fi
}

cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR/postgres" -name "*.sql.gz" -mtime +"$RETENTION_DAYS" -delete 2>/dev/null || true
    find "$BACKUP_DIR/redis" -name "*.rdb" -mtime +"$RETENTION_DAYS" -delete 2>/dev/null || true
    find "$BACKUP_DIR/logs" -name "*.log" -mtime +"$RETENTION_DAYS" -delete 2>/dev/null || true
    log "Cleanup completed"
}

verify_backup() {
    local backup_file="$1"
    log "Verifying backup integrity: $backup_file"

    # Test gzip integrity
    if gzip -t "$backup_file" 2>/dev/null; then
        log "Backup integrity check passed"
        return 0
    else
        log "ERROR: Backup integrity check failed"
        return 1
    fi
}

main() {
    validate_config

    log "=== StudyOS Backup Started ==="
    log "Type: $BACKUP_TYPE"
    log "Backup dir: $BACKUP_DIR"

    backup_postgres
    backup_redis
    cleanup_old_backups

    log "=== StudyOS Backup Completed ==="
}

main "$@"
