"""Tests for backup and disaster recovery scripts."""

import os
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent.parent / "scripts"
BACKUP_DIR = SCRIPTS_DIR / "backup"
DR_DIR = SCRIPTS_DIR / "dr"


class TestBackupScripts:
    def test_backup_script_exists(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        assert script.exists()

    def test_backup_script_is_executable(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        assert os.access(script, os.X_OK)

    def test_backup_script_has_shebang(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        with open(script) as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!/usr/bin/env bash")

    def test_backup_script_has_validate_config(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        content = script.read_text()
        assert "validate_config" in content
        assert "STUDYOS_DATABASE_URL" in content

    def test_backup_script_has_postgres_backup(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        content = script.read_text()
        assert "backup_postgres" in content
        assert "pg_dump" in content

    def test_backup_script_has_redis_backup(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        content = script.read_text()
        assert "backup_redis" in content
        assert "BGSAVE" in content

    def test_backup_script_has_cleanup(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        content = script.read_text()
        assert "cleanup_old_backups" in content
        assert "RETENTION_DAYS" in content

    def test_backup_script_has_verification(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        content = script.read_text()
        assert "verify_backup" in content
        assert "gzip -t" in content

    def test_backup_script_supports_backup_types(self) -> None:
        script = BACKUP_DIR / "automated-backup.sh"
        content = script.read_text()
        assert "full" in content
        assert "schema-only" in content
        assert "data-only" in content


class TestDRDrillScript:
    def test_dr_drill_script_exists(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        assert script.exists()

    def test_dr_drill_script_is_executable(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        assert os.access(script, os.X_OK)

    def test_dr_drill_script_has_shebang(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        with open(script) as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!/usr/bin/env bash")

    def test_dr_drill_has_backup_tests(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        content = script.read_text()
        assert "test_backup_files_exist" in content
        assert "test_backup_integrity" in content

    def test_dr_drill_has_db_recovery_tests(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        content = script.read_text()
        assert "test_db_restore_dry_run" in content
        assert "test_db_connection_after_failure" in content

    def test_dr_drill_has_redis_tests(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        content = script.read_text()
        assert "test_redis_restore" in content

    def test_dr_drill_has_service_health_tests(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        content = script.read_text()
        assert "test_api_health" in content
        assert "test_web_health" in content

    def test_dr_drill_has_rto_rpo_tests(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        content = script.read_text()
        assert "test_rto_compliance" in content
        assert "test_rpo_compliance" in content

    def test_dr_drill_supports_modes(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        content = script.read_text()
        assert "--quick" in content
        assert "--full" in content
        assert "run_quick_drill" in content
        assert "run_full_drill" in content

    def test_dr_drill_generates_json_report(self) -> None:
        script = DR_DIR / "dr-drill.sh"
        content = script.read_text()
        assert "generate_report" in content
        assert '"pass_rate_percent"' in content
        assert '"results"' in content


class TestRunbooks:
    def test_dr_runbook_exists(self) -> None:
        runbook = (
            Path(__file__).parent.parent.parent.parent.parent
            / "docs"
            / "runbooks"
            / "disaster-recovery.md"
        )
        assert runbook.exists()

    def test_dr_runbook_has_recovery_sections(self) -> None:
        runbook = (
            Path(__file__).parent.parent.parent.parent.parent
            / "docs"
            / "runbooks"
            / "disaster-recovery.md"
        )
        content = runbook.read_text()
        assert "Database Failure Recovery" in content
        assert "Redis Failure Recovery" in content
        assert "API Service Failure Recovery" in content
        assert "Full System Outage Recovery" in content

    def test_dr_runbook_has_escalation_matrix(self) -> None:
        runbook = (
            Path(__file__).parent.parent.parent.parent.parent
            / "docs"
            / "runbooks"
            / "disaster-recovery.md"
        )
        content = runbook.read_text()
        assert "Escalation Matrix" in content
        assert "P1" in content
        assert "P2" in content

    def test_multi_region_checklist_exists(self) -> None:
        checklist = (
            Path(__file__).parent.parent.parent.parent.parent
            / "docs"
            / "runbooks"
            / "multi-region-readiness.md"
        )
        assert checklist.exists()

    def test_multi_region_checklist_has_sections(self) -> None:
        checklist = (
            Path(__file__).parent.parent.parent.parent.parent
            / "docs"
            / "runbooks"
            / "multi-region-readiness.md"
        )
        content = checklist.read_text()
        assert "Infrastructure" in content
        assert "Application" in content
        assert "Security" in content
        assert "Monitoring" in content
        assert "Disaster Recovery" in content
        assert "Testing" in content
