"""Tests for error handling — covering uncovered lines."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from studyos_api.core.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    problem,
    unhandled_exception_handler,
    validation_exception_handler,
)


class TestProblem:
    def test_minimal_problem(self) -> None:
        body = problem(type_uri="https://example.com/error", title="Error", status_code=500)
        assert body["type"] == "https://example.com/error"
        assert body["title"] == "Error"
        assert body["status"] == 500

    def test_problem_with_detail(self) -> None:
        body = problem(
            type_uri="https://example.com/error", title="Error", status_code=400, detail="Bad input"
        )
        assert body["detail"] == "Bad input"

    def test_problem_with_instance(self) -> None:
        body = problem(
            type_uri="https://example.com/error",
            title="Error",
            status_code=404,
            instance="/users/123",
        )
        assert body["instance"] == "/users/123"

    def test_problem_with_extensions(self) -> None:
        body = problem(
            type_uri="https://example.com/error",
            title="Error",
            status_code=422,
            extensions={"code": "validation"},
        )
        assert body["code"] == "validation"


class TestAppError:
    def test_default_values(self) -> None:
        err = AppError(code="test_error", title="Test Error")
        assert err.code == "test_error"
        assert err.title == "Test Error"
        assert err.status_code == 400

    def test_custom_values(self) -> None:
        err = AppError(
            code="not_found",
            title="Not Found",
            status_code=404,
            detail="Item 123 not found",
        )
        assert err.code == "not_found"
        assert err.status_code == 404

    def test_extensions(self) -> None:
        err = AppError(
            code="rate_limited",
            title="Rate Limited",
            status_code=429,
            extensions={"retry_after": 60},
        )
        assert err.extensions == {"retry_after": 60}


class TestErrorHandlers:
    @pytest.fixture
    def app(self) -> FastAPI:
        app = FastAPI()
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(HTTPException, http_exception_handler)
        app.add_exception_handler(Exception, unhandled_exception_handler)
        app.add_exception_handler(RequestValidationError, validation_exception_handler)
        return app

    def test_app_error_handler(self, app: FastAPI) -> None:
        @app.get("/app-error")
        def raise_app_error():
            raise AppError(
                code="bad_request", title="Bad Request", status_code=400, detail="Invalid input"
            )

        client = TestClient(app)
        resp = client.get("/app-error")
        assert resp.status_code == 400
        data = resp.json()
        assert data["title"] == "Bad Request"
        assert data["code"] == "bad_request"

    def test_http_exception_handler(self, app: FastAPI) -> None:
        @app.get("/http-error")
        def raise_http_error():
            raise HTTPException(status_code=404, detail="Not found")

        client = TestClient(app)
        resp = client.get("/http-error")
        assert resp.status_code == 404

    def test_validation_exception_handler(self, app: FastAPI) -> None:
        from pydantic import BaseModel

        class Item(BaseModel):
            name: str

        @app.post("/validation")
        def create_item(item: Item):
            return item

        client = TestClient(app)
        resp = client.post("/validation", json={"name": 123})
        assert resp.status_code == 422
