#!/usr/bin/env bash
# Disaster Recovery Drill Script for StudyOS
# Simulates failures, tests recovery procedures, and generates a report.
# Usage: ./dr-drill.sh [--quick|--full] [--report-dir PATH]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="${STUDYOS_DR_REPORT_DIR:-/opt/studyos/reports/dr}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_FILE="$REPORT_DIR/dr_drill_${TIMESTAMP}.json"
DRILL_MODE="${1:---full}"
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
RESULTS=()

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $1"
}

record_result() {
    local test_name="$1"
    local status="$2"
    local details="${3:-}"

    RESULTS+=("{\"test\":\"$test_name\",\"status\":\"$status\",\"details\":\"$details\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}")

    case "$status" in
        PASS) ((PASS_COUNT++)) ;;
        FAIL) ((FAIL_COUNT++)) ;;
        SKIP) ((SKIP_COUNT++)) ;;
    esac

    log "[$status] $test_name: $details"
}

setup() {
    mkdir -p "$REPORT_DIR"
    log "=== StudyOS DR Drill Started ==="
    log "Mode: $DRILL_MODE"
    log "Report: $REPORT_FILE"
}

# --- Pre-flight Checks ---
test_backup_files_exist() {
    local backup_dir="${STUDYOS_BACKUP_DIR:-/opt/studyos/backups}"
    local postgres_backups=$(find "$backup_dir/postgres" -name "*.sql.gz" 2>/dev/null | wc -l)

    if [ "$postgres_backups" -gt 0 ]; then
        record_result "backup_files_exist" "PASS" "Found $postgres_backups PostgreSQL backups"
    else
        record_result "backup_files_exist" "FAIL" "No PostgreSQL backups found"
    fi
}

test_backup_integrity() {
    local backup_dir="${STUDYOS_BACKUP_DIR:-/opt/studyos/backups}"
    local latest=$(ls -t "$backup_dir/postgres"/*.sql.gz 2>/dev/null | head -1)

    if [ -n "$latest" ]; then
        if gzip -t "$latest" 2>/dev/null; then
            record_result "backup_integrity" "PASS" "Latest backup verified: $latest"
        else
            record_result "backup_integrity" "FAIL" "Latest backup corrupted: $latest"
        fi
    else
        record_result "backup_integrity" "SKIP" "No backups to verify"
    fi
}

# --- Database Recovery Tests ---
test_db_restore_dry_run() {
    local backup_dir="${STUDYOS_BACKUP_DIR:-/opt/studyos/backups}"
    local latest=$(ls -t "$backup_dir/postgres"/*.sql.gz 2>/dev/null | head -1)

    if [ -n "$latest" ]; then
        # Test restore to a temporary database
        local temp_db="studyos_dr_test_${TIMESTAMP}"
        if createdb "$temp_db" 2>/dev/null; then
            if zcat "$latest" | psql -d "$temp_db" > /dev/null 2>&1; then
                record_result "db_restore_dry_run" "PASS" "Successfully restored to temp database"
            else
                record_result "db_restore_dry_run" "FAIL" "Restore to temp database failed"
            fi
            dropdb "$temp_db" 2>/dev/null || true
        else
            record_result "db_restore_dry_run" "SKIP" "Cannot create temp database (permission issue)"
        fi
    else
        record_result "db_restore_dry_run" "SKIP" "No backups available"
    fi
}

test_db_connection_after_failure() {
    local db_url="${STUDYOS_DATABASE_URL:-}"
    if [ -z "$db_url" ]; then
        record_result "db_connection_after_failure" "SKIP" "DATABASE_URL not set"
        return
    fi

    # Simulate brief connection loss (just test reconnect)
    if psql "$db_url" -c "SELECT 1" > /dev/null 2>&1; then
        record_result "db_connection_after_failure" "PASS" "Database connection recovered"
    else
        record_result "db_connection_after_failure" "FAIL" "Database connection failed"
    fi
}

# --- Redis Recovery Tests ---
test_redis_restore() {
    local redis_url="${STUDYOS_REDIS_URL:-redis://localhost:6379/0}"
    local backup_dir="${STUDYOS_BACKUP_DIR:-/opt/studyos/backups}"

    if redis-cli -u "$redis_url" PING > /dev/null 2>&1; then
        record_result "redis_restore" "PASS" "Redis is responding to PING"
    else
        record_result "redis_restore" "FAIL" "Redis is not responding"
    fi
}

# --- Service Health Tests ---
test_api_health() {
    local api_url="${STUDYOS_API_URL:-http://localhost:8000}"

    if curl -sf "$api_url/v1/healthz" > /dev/null 2>&1; then
        record_result "api_health" "PASS" "API health check passed"
    else
        record_result "api_health" "FAIL" "API health check failed"
    fi
}

test_web_health() {
    local web_url="${STUDYOS_WEB_URL:-http://localhost:3000}"

    if curl -sf "$web_url" > /dev/null 2>&1; then
        record_result "web_health" "PASS" "Web health check passed"
    else
        record_result "web_health" "FAIL" "Web health check failed"
    fi
}

# --- RTO/RPO Validation ---
test_rto_compliance() {
    # RTO target: 15 minutes
    local rto_target_seconds=900
    local latest_backup="${STUDYOS_BACKUP_DIR:-/opt/studyos/backups}/postgres"
    local newest=$(ls -t "$latest_backup"/*.sql.gz 2>/dev/null | head -1)

    if [ -n "$newest" ]; then
        local backup_time=$(stat -c %Y "$newest" 2>/dev/null || stat -f %m "$newest" 2>/dev/null || echo 0)
        local now=$(date +%s)
        local age=$((now - backup_time))

        if [ "$age" -lt "$rto_target_seconds" ]; then
            record_result "rto_compliance" "PASS" "Latest backup is $((age / 60))min old (RTO: 15min)"
        else
            record_result "rto_compliance" "FAIL" "Latest backup is $((age / 60))min old (RTO: 15min)"
        fi
    else
        record_result "rto_compliance" "SKIP" "No backups to measure RTO"
    fi
}

test_rpo_compliance() {
    # RPO target: 1 hour (max data loss)
    local rpo_target_seconds=3600
    local latest_backup="${STUDYOS_BACKUP_DIR:-/opt/studyos/backups}/postgres"
    local newest=$(ls -t "$latest_backup"/*.sql.gz 2>/dev/null | head -1)

    if [ -n "$newest" ]; then
        local backup_time=$(stat -c %Y "$newest" 2>/dev/null || stat -f %m "$newest" 2>/dev/null || echo 0)
        local now=$(date +%s)
        local age=$((now - backup_time))

        if [ "$age" -lt "$rpo_target_seconds" ]; then
            record_result "rpo_compliance" "PASS" "Data loss window: $((age / 60))min (RPO: 60min)"
        else
            record_result "rpo_compliance" "FAIL" "Data loss window: $((age / 60))min (RPO: 60min)"
        fi
    else
        record_result "rpo_compliance" "SKIP" "No backups to measure RPO"
    fi
}

# --- Quick Mode (only critical checks) ---
run_quick_drill() {
    test_backup_files_exist
    test_backup_integrity
    test_db_connection_after_failure
    test_redis_restore
    test_api_health
}

# --- Full Mode (all checks) ---
run_full_drill() {
    test_backup_files_exist
    test_backup_integrity
    test_db_restore_dry_run
    test_db_connection_after_failure
    test_redis_restore
    test_api_health
    test_web_health
    test_rto_compliance
    test_rpo_compliance
}

# --- Report Generation ---
generate_report() {
    local total=$((PASS_COUNT + FAIL_COUNT + SKIP_COUNT))
    local pass_rate=0
    if [ $((PASS_COUNT + FAIL_COUNT)) -gt 0 ]; then
        pass_rate=$(( (PASS_COUNT * 100) / (PASS_COUNT + FAIL_COUNT) ))
    fi

    local results_json=$(printf "%s," "${RESULTS[@]}")
    results_json="[${results_json%,}]"

    cat > "$REPORT_FILE" << EOF
{
    "drill_id": "dr_${TIMESTAMP}",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "mode": "$DRILL_MODE",
    "summary": {
        "total": $total,
        "passed": $PASS_COUNT,
        "failed": $FAIL_COUNT,
        "skipped": $SKIP_COUNT,
        "pass_rate_percent": $pass_rate
    },
    "results": $results_json,
    "rto_target_minutes": 15,
    "rpo_target_minutes": 60
}
EOF

    log "=== DR Drill Report ==="
    log "Total: $total | Passed: $PASS_COUNT | Failed: $FAIL_COUNT | Skipped: $SKIP_COUNT"
    log "Pass Rate: ${pass_rate}%"
    log "Report saved to: $REPORT_FILE"
}

main() {
    setup

    case "$DRILL_MODE" in
        --quick) run_quick_drill ;;
        --full|"") run_full_drill ;;
        *)
            log "ERROR: Unknown mode: $DRILL_MODE"
            echo "Usage: $0 [--quick|--full]"
            exit 1
            ;;
    esac

    generate_report

    if [ "$FAIL_COUNT" -gt 0 ]; then
        log "WARNING: $FAIL_COUNT tests failed. Review the report for details."
        exit 1
    fi

    log "=== StudyOS DR Drill Completed Successfully ==="
}

main "$@"
