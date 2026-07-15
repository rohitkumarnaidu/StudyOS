"""Tests for report generation Celery tasks."""

from studyos_api.tasks.report_tasks import (
    cleanup_expired_sessions,
    export_study_data,
    generate_mock_test_analysis,
    generate_performance_report,
    generate_streak_report,
)


class TestGeneratePerformanceReport:
    def test_generate_performance_report_success(self) -> None:
        result = generate_performance_report(
            profile_id="user-123",
            report_type="monthly",
            date_range={"start": "2026-04-01", "end": "2026-04-30"},
        )
        assert result["profile_id"] == "user-123"
        assert result["report_type"] == "monthly"
        assert result["date_range"] == {"start": "2026-04-01", "end": "2026-04-30"}
        assert result["status"] == "completed"
        assert result["sections"] == ["accuracy", "velocity", "retention", "predictions"]

    def test_generate_performance_report_default_values(self) -> None:
        result = generate_performance_report(profile_id="user-456")
        assert result["report_type"] == "weekly"
        assert result["date_range"] is None

    def test_generate_performance_report_retry_config(self) -> None:
        task = generate_performance_report
        assert task.max_retries == 3
        assert task.default_retry_delay == 60
        assert task.queue == "reports"


class TestGenerateMockTestAnalysis:
    def test_generate_mock_test_analysis_success(self) -> None:
        result = generate_mock_test_analysis(
            profile_id="user-123",
            mock_test_id="mock-456",
            include_weaknesses=True,
        )
        assert result["profile_id"] == "user-123"
        assert result["mock_test_id"] == "mock-456"
        assert result["include_weaknesses"] is True
        assert result["status"] == "completed"
        assert result["sections"] == ["score_breakdown", "time_analysis", "weakness_report"]

    def test_generate_mock_test_analysis_default_values(self) -> None:
        result = generate_mock_test_analysis(
            profile_id="user-789",
            mock_test_id="mock-001",
        )
        assert result["include_weaknesses"] is True

    def test_generate_mock_test_analysis_retry_config(self) -> None:
        task = generate_mock_test_analysis
        assert task.max_retries == 2
        assert task.default_retry_delay == 90


class TestExportStudyData:
    def test_export_study_data_csv(self) -> None:
        result = export_study_data(
            profile_id="user-123",
            format="csv",
            include_history=True,
        )
        assert result["profile_id"] == "user-123"
        assert result["format"] == "csv"
        assert result["include_history"] is True
        assert result["status"] == "completed"

    def test_export_study_data_json(self) -> None:
        result = export_study_data(
            profile_id="user-456",
            format="json",
            include_history=False,
        )
        assert result["format"] == "json"
        assert result["include_history"] is False

    def test_export_study_data_default_values(self) -> None:
        result = export_study_data(profile_id="user-789")
        assert result["format"] == "csv"
        assert result["include_history"] is True

    def test_export_study_data_retry_config(self) -> None:
        task = export_study_data
        assert task.max_retries == 3
        assert task.default_retry_delay == 30


class TestCleanupExpiredSessions:
    def test_cleanup_expired_sessions_success(self) -> None:
        result = cleanup_expired_sessions()
        assert result["status"] == "completed"
        assert "sessions_cleaned" in result
        assert "cache_entries_purged" in result


class TestGenerateStreakReport:
    def test_generate_streak_report_success(self) -> None:
        result = generate_streak_report(profile_id="user-123")
        assert result["profile_id"] == "user-123"
        assert result["status"] == "completed"
        assert "current_streak" in result
        assert "longest_streak" in result
        assert "total_study_days" in result

    def test_generate_streak_report_retry_config(self) -> None:
        task = generate_streak_report
        assert task.max_retries == 2
        assert task.default_retry_delay == 120
