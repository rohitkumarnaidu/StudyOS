"""Tests for MistakeIntelligenceController."""

import uuid
from unittest.mock import MagicMock

import pytest

from studyos_api.controllers.mistake_intelligence_controller import MistakeIntelligenceController


@pytest.fixture
def controller():
    return MistakeIntelligenceController()


@pytest.fixture
def mock_request():
    request = MagicMock()
    request.url.path = "/v1/mistake-intelligence/mistakes"
    request.method = "GET"
    return request


class TestLogMistake:
    @pytest.mark.asyncio
    async def test_log_mistake_success(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.log_mistake(
            request=mock_request,
            profile_id=profile_id,
            question_id="q1",
            mistake_type="conceptual",
            concept_tags=["algebra"],
            confidence_level=0.5,
        )
        assert "data" in result
        assert result["data"]["mistake_type"] == "conceptual"
        assert result["data"]["question_id"] == "q1"

    @pytest.mark.asyncio
    async def test_log_mistake_invalid_type(self, controller, mock_request):
        profile_id = uuid.uuid4()
        with pytest.raises(Exception):
            await controller.log_mistake(
                request=mock_request,
                profile_id=profile_id,
                question_id="q1",
                mistake_type="invalid_type",
            )


class TestGetUserMistakes:
    @pytest.mark.asyncio
    async def test_get_all_mistakes(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_user_mistakes(request=mock_request, profile_id=profile_id)
        assert "data" in result
        assert "mistakes" in result["data"]
        assert "total" in result["data"]

    @pytest.mark.asyncio
    async def test_get_mistakes_by_type(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_user_mistakes(
            request=mock_request,
            profile_id=profile_id,
            mistake_type="conceptual",
        )
        assert "data" in result

    @pytest.mark.asyncio
    async def test_get_mistakes_by_concept(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_user_mistakes(
            request=mock_request,
            profile_id=profile_id,
            concept="algebra",
        )
        assert "data" in result


class TestGetMistakeStats:
    @pytest.mark.asyncio
    async def test_get_stats(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_mistake_stats(request=mock_request, profile_id=profile_id)
        assert "data" in result
        assert "meta" in result


class TestAnalyzeGaps:
    @pytest.mark.asyncio
    async def test_analyze_gaps(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.analyze_gaps(
            request=mock_request,
            profile_id=profile_id,
            min_attempts=3,
        )
        assert "data" in result
        assert "gaps" in result["data"]
        assert "total" in result["data"]


class TestGetWeakConcepts:
    @pytest.mark.asyncio
    async def test_get_weak_concepts(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_weak_concepts(
            request=mock_request,
            profile_id=profile_id,
            top_n=3,
        )
        assert "data" in result
        assert "weak_concepts" in result["data"]


class TestGetMasteryLevel:
    @pytest.mark.asyncio
    async def test_get_mastery_level(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_mastery_level(
            request=mock_request,
            profile_id=profile_id,
            concept="algebra",
        )
        assert "data" in result
        assert result["data"]["concept"] == "algebra"
        assert "mastery_level" in result["data"]


class TestGetStudyPlan:
    @pytest.mark.asyncio
    async def test_get_study_plan(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_study_plan(
            request=mock_request,
            profile_id=profile_id,
            max_concepts=3,
        )
        assert "data" in result
        assert "study_plan" in result["data"]


class TestPredictMistakes:
    @pytest.mark.asyncio
    async def test_predict_all_concepts(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.predict_mistakes(
            request=mock_request,
            profile_id=profile_id,
        )
        assert "data" in result
        assert "predictions" in result["data"]

    @pytest.mark.asyncio
    async def test_predict_specific_concepts(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.predict_mistakes(
            request=mock_request,
            profile_id=profile_id,
            concepts=["algebra", "geometry"],
        )
        assert "data" in result


class TestGetHighRiskConcepts:
    @pytest.mark.asyncio
    async def test_get_high_risk(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_high_risk_concepts(
            request=mock_request,
            profile_id=profile_id,
            threshold=0.6,
        )
        assert "data" in result
        assert "high_risk_concepts" in result["data"]
        assert result["data"]["threshold"] == 0.6


class TestGetImprovementTrend:
    @pytest.mark.asyncio
    async def test_get_trend(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_improvement_trend(
            request=mock_request,
            profile_id=profile_id,
            concept="algebra",
        )
        assert "data" in result
        assert result["data"]["concept"] == "algebra"
        assert "trend" in result["data"]


class TestClusterMistakes:
    @pytest.mark.asyncio
    async def test_cluster(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.cluster_mistakes(
            request=mock_request,
            profile_id=profile_id,
            min_cluster_size=2,
        )
        assert "data" in result
        assert "clusters" in result["data"]
        assert "stats" in result["data"]


class TestGetClusterStats:
    @pytest.mark.asyncio
    async def test_get_cluster_stats(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_cluster_stats(
            request=mock_request,
            profile_id=profile_id,
        )
        assert "data" in result
        assert "meta" in result


class TestGetFullIntelligenceReport:
    @pytest.mark.asyncio
    async def test_get_report(self, controller, mock_request):
        profile_id = uuid.uuid4()
        result = await controller.get_full_intelligence_report(
            request=mock_request,
            profile_id=profile_id,
        )
        assert "data" in result
        report = result["data"]
        assert "mistake_stats" in report
        assert "knowledge_gaps" in report
        assert "predictions" in report
        assert "clusters" in report
        assert "study_plan" in report
        assert "meta" in result
