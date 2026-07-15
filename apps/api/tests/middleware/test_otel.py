"""Tests for OpenTelemetry middleware."""

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.testclient import TestClient

from studyos_api.middleware.otel import OTelMiddleware


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()

    @app.get("/ok")
    async def ok() -> dict:
        return {"status": "ok"}

    @app.get("/error")
    async def error() -> JSONResponse:
        return JSONResponse(status_code=500, content={"error": "server error"})

    @app.get("/slow")
    async def slow() -> dict:
        import time
        time.sleep(0.1)
        return {"status": "slow"}

    app.add_middleware(OTelMiddleware, service_name="test-api", sample_rate=1.0)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


class TestOTelMiddleware:
    def test_success_request(self, client: TestClient) -> None:
        response = client.get("/ok")
        assert response.status_code == 200
        assert "x-service-name" in response.headers
        assert response.headers["x-service-name"] == "test-api"
        assert "x-response-time-ms" in response.headers

    def test_error_request(self, client: TestClient) -> None:
        response = client.get("/error")
        assert response.status_code == 500

    def test_request_id_passthrough(self, client: TestClient) -> None:
        response = client.get("/ok", headers={"x-request-id": "req-123"})
        assert response.headers["x-request-id"] == "req-123"

    def test_slow_request(self, client: TestClient) -> None:
        response = client.get("/slow")
        assert response.status_code == 200
        response_time = float(response.headers["x-response-time-ms"])
        assert response_time >= 100

    def test_metrics_initial(self, app: FastAPI) -> None:
        middleware = None
        for m in app.user_middleware:
            if m.cls == OTelMiddleware:
                middleware = m
        # Middleware is added via add_middleware, not directly accessible
        # Test metrics via a fresh instance
        otel = OTelMiddleware(app, service_name="test", sample_rate=0.1)
        metrics = otel.metrics
        assert metrics["total_requests"] == 0
        assert metrics["total_errors"] == 0
        assert metrics["error_rate"] == 0.0
        assert metrics["avg_latency_ms"] == 0.0

    def test_metrics_after_requests(self, app: FastAPI) -> None:
        otel = OTelMiddleware(app, service_name="test", sample_rate=0.1)
        otel._request_count = 100
        otel._error_count = 5
        otel._latency_total = 10.0
        metrics = otel.metrics
        assert metrics["total_requests"] == 100
        assert metrics["total_errors"] == 5
        assert metrics["error_rate"] == 0.05
        assert metrics["avg_latency_ms"] == 100.0

    def test_reset_metrics(self, app: FastAPI) -> None:
        otel = OTelMiddleware(app, service_name="test", sample_rate=0.1)
        otel._request_count = 50
        otel._error_count = 3
        otel._latency_total = 5.0
        otel.reset_metrics()
        metrics = otel.metrics
        assert metrics["total_requests"] == 0
        assert metrics["total_errors"] == 0
        assert metrics["avg_latency_ms"] == 0.0

    def test_service_name_in_metrics(self, app: FastAPI) -> None:
        otel = OTelMiddleware(app, service_name="my-service", sample_rate=0.5)
        metrics = otel.metrics
        assert metrics["service_name"] == "my-service"
        assert metrics["sample_rate"] == 0.5
