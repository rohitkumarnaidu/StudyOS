#!/usr/bin/env bash
# StudyOS — Database backup script
# Usage: ./scripts/backup.sh [output_dir]
# Requires: pg_dump, gzip, postgresql-client

set -euo pipefail

DB_URL="${STUDYOS_DATABASE_URL:-}"
BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/studyos_${TIMESTAMP}.sql.gz"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

if [ -z "$DB_URL" ]; then
  echo "ERROR: STUDYOS_DATABASE_URL is not set"
  exit 1
fi

mkdir -p "$BACKUP_DIR"

echo "Starting backup to ${BACKUP_FILE}..."

pg_dump "$DB_URL" | gzip > "$BACKUP_FILE"

FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup complete: ${BACKUP_FILE} (${FILE_SIZE})"

# Verify backup is valid
if gzip -t "$BACKUP_FILE" 2>/dev/null; then
  echo "Backup verified: OK"
else
  echo "ERROR: Backup verification failed"
  exit 1
fi

# Clean up old backups
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "studyos_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

echo "Backup finished successfully"
