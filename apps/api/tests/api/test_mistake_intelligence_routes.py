"""Tests for mistake intelligence routes."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture
def client():
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""
    os.environ["STUDYOS_DATABASE_URL"] = ""
    os.environ["STUDYOS_EXPOSE_ERROR_DETAIL"] = "true"
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app, base_url="http://testserver", raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def auth_headers():
    from studyos_api.core.config import get_settings
    from studyos_api.security.tokens import mint_access_token

    settings = get_settings()
    token = mint_access_token(settings, sub=str(uuid.uuid4()), roles=["student"])
    return {"Authorization": f"Bearer {token}"}


class TestLogMistakeRoute:
    def test_log_requires_auth(self, client):
        resp = client.post("/v1/mistake-intelligence/mistakes")
        assert resp.status_code in (401, 403)

    def test_log_mistake_success(self, client, auth_headers):
        resp = client.post(
            "/v1/mistake-intelligence/mistakes",
            headers=auth_headers,
            params={
                "question_id": "q1",
                "mistake_type": "conceptual",
                "concept_tags": ["algebra"],
                "confidence_level": 0.5,
                "time_taken_seconds": 30.0,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert data["data"]["mistake_type"] == "conceptual"

    def test_log_mistake_invalid_type(self, client, auth_headers):
        resp = client.post(
            "/v1/mistake-intelligence/mistakes",
            headers=auth_headers,
            params={
                "question_id": "q1",
                "mistake_type": "invalid_type",
            },
        )
        assert resp.status_code == 400


class TestGetMistakesRoute:
    def test_get_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes")
        assert resp.status_code in (401, 403)

    def test_get_mistakes_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "mistakes" in data["data"]
        assert "total" in data["data"]

    def test_get_mistakes_by_type(self, client, auth_headers):
        resp = client.get(
            "/v1/mistake-intelligence/mistakes",
            headers=auth_headers,
            params={"mistake_type": "conceptual"},
        )
        assert resp.status_code == 200

    def test_get_mistakes_by_concept(self, client, auth_headers):
        resp = client.get(
            "/v1/mistake-intelligence/mistakes",
            headers=auth_headers,
            params={"concept": "algebra"},
        )
        assert resp.status_code == 200


class TestMistakeStatsRoute:
    def test_stats_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/stats")
        assert resp.status_code in (401, 403)

    def test_get_stats_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data


class TestAnalyzeGapsRoute:
    def test_gaps_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/gaps")
        assert resp.status_code in (401, 403)

    def test_analyze_gaps_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes/gaps", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "gaps" in data["data"]


class TestWeakConceptsRoute:
    def test_weak_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/weak-concepts")
        assert resp.status_code in (401, 403)

    def test_get_weak_concepts_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes/weak-concepts", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "weak_concepts" in data["data"]


class TestMasteryLevelRoute:
    def test_mastery_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/mastery/algebra")
        assert resp.status_code in (401, 403)

    def test_get_mastery_level_success(self, client, auth_headers):
        resp = client.get(
            "/v1/mistake-intelligence/mistakes/mastery/algebra",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert data["data"]["concept"] == "algebra"
        assert "mastery_level" in data["data"]


class TestStudyPlanRoute:
    def test_plan_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/study-plan")
        assert resp.status_code in (401, 403)

    def test_get_study_plan_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes/study-plan", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "study_plan" in data["data"]


class TestPredictionsRoute:
    def test_predictions_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/predictions")
        assert resp.status_code in (401, 403)

    def test_get_predictions_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes/predictions", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "predictions" in data["data"]


class TestHighRiskRoute:
    def test_high_risk_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/high-risk")
        assert resp.status_code in (401, 403)

    def test_get_high_risk_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes/high-risk", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "high_risk_concepts" in data["data"]


class TestTrendRoute:
    def test_trend_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/trend/algebra")
        assert resp.status_code in (401, 403)

    def test_get_trend_success(self, client, auth_headers):
        resp = client.get(
            "/v1/mistake-intelligence/mistakes/trend/algebra",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert data["data"]["concept"] == "algebra"
        assert "trend" in data["data"]


class TestClusterRoute:
    def test_cluster_requires_auth(self, client):
        resp = client.post("/v1/mistake-intelligence/mistakes/cluster")
        assert resp.status_code in (401, 403)

    def test_cluster_success(self, client, auth_headers):
        resp = client.post(
            "/v1/mistake-intelligence/mistakes/cluster",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "clusters" in data["data"]
        assert "stats" in data["data"]


class TestClusterStatsRoute:
    def test_cluster_stats_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/cluster/stats")
        assert resp.status_code in (401, 403)

    def test_get_cluster_stats_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes/cluster/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data


class TestReportRoute:
    def test_report_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/report")
        assert resp.status_code in (401, 403)

    def test_get_report_success(self, client, auth_headers):
        resp = client.get("/v1/mistake-intelligence/mistakes/report", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        report_data = data["data"]
        assert "mistake_stats" in report_data
        assert "knowledge_gaps" in report_data
        assert "predictions" in report_data
        assert "clusters" in report_data
        assert "study_plan" in report_data
