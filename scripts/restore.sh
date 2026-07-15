#!/usr/bin/env bash
# StudyOS — Database restore script
# Usage: ./scripts/restore.sh <backup_file>
# Requires: psql, postgresql-client

set -euo pipefail

DB_URL="${STUDYOS_DATABASE_URL:-}"
BACKUP_FILE="${1:-}"

if [ -z "$DB_URL" ]; then
  echo "ERROR: STUDYOS_DATABASE_URL is not set"
  exit 1
fi

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  echo "Available backups:"
  ls -la ./backups/studyos_*.sql.gz 2>/dev/null || echo "  No backups found"
  exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
  echo "ERROR: Backup file not found: ${BACKUP_FILE}"
  exit 1
fi

echo "WARNING: This will overwrite the current database!"
echo "Database: $(echo "$DB_URL" | sed 's|://.*|://***|')"
echo "Backup: ${BACKUP_FILE}"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Restore cancelled"
  exit 0
fi

echo "Restoring from ${BACKUP_FILE}..."

if [[ "$BACKUP_FILE" == *.gz ]]; then
  gunzip -c "$BACKUP_FILE" | psql "$DB_URL"
else
  psql "$DB_URL" < "$BACKUP_FILE"
fi

echo "Restore complete"
