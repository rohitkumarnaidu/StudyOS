"""Tests for Telemetry initialization."""

from unittest.mock import MagicMock, patch

import pytest

from studyos_api.core.telemetry import init_telemetry


class TestInitTelemetry:
    def test_no_otlp_endpoint(self) -> None:
        """Should log disabled when no endpoint is set."""
        mock_app = MagicMock()
        init_telemetry(mock_app, service_name="test", otlp_endpoint=None, sample_rate=1.0)

    def test_empty_otlp_endpoint(self) -> None:
        """Should log disabled when endpoint is empty string."""
        mock_app = MagicMock()
        init_telemetry(mock_app, service_name="test", otlp_endpoint="", sample_rate=1.0)

    def test_with_otlp_endpoint_import_error(self) -> None:
        """Should handle missing opentelemetry packages gracefully."""
        mock_app = MagicMock()
        with patch.dict("sys.modules", {"opentelemetry": None}):
            init_telemetry(mock_app, service_name="test", otlp_endpoint="http://localhost:4318", sample_rate=1.0)

    def test_otlp_success(self) -> None:
        """Should initialize telemetry when OTLP endpoint is set and packages are available."""
        mock_app = MagicMock()
        mock_instrumentor = MagicMock()

        with patch.dict("sys.modules", {
            "opentelemetry": MagicMock(trace=MagicMock(sampling=MagicMock(TraceBasedSampler=MagicMock(return_value=MagicMock())))),
            "opentelemetry.exporter.otlp.proto.http.trace_exporter": MagicMock(OTLPSpanExporter=MagicMock()),
            "opentelemetry.instrumentation.fastapi": MagicMock(FastAPIInstrumentor=mock_instrumentor),
            "opentelemetry.sdk.resources": MagicMock(Resource=MagicMock(create=MagicMock())),
            "opentelemetry.sdk.trace": MagicMock(TracerProvider=MagicMock()),
            "opentelemetry.sdk.trace.export": MagicMock(BatchSpanProcessor=MagicMock()),
        }):
            init_telemetry(mock_app, service_name="test-svc", otlp_endpoint="http://localhost:4318", sample_rate=0.5)
            mock_instrumentor.instrument_app.assert_called_once_with(mock_app)

    def test_otlp_init_exception(self) -> None:
        """Should handle unexpected exceptions during telemetry init."""
        mock_app = MagicMock()

        with patch.dict("sys.modules", {
            "opentelemetry": MagicMock(),
            "opentelemetry.exporter.otlp.proto.http.trace_exporter": MagicMock(OTLPSpanExporter=MagicMock(side_effect=RuntimeError("unexpected error"))),
            "opentelemetry.instrumentation.fastapi": MagicMock(),
            "opentelemetry.sdk.resources": MagicMock(),
            "opentelemetry.sdk.trace": MagicMock(),
            "opentelemetry.sdk.trace.export": MagicMock(),
        }):
            init_telemetry(mock_app, service_name="test-svc", otlp_endpoint="http://localhost:4318", sample_rate=1.0)
