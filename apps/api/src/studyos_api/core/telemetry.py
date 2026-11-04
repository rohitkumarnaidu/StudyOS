"""OpenTelemetry instrumentation for FastAPI — traces, metrics, logging."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = structlog.get_logger(__name__)


def init_telemetry(
    app: FastAPI,
    service_name: str,
    otlp_endpoint: str | None,
    sample_rate: float,
) -> None:
    """Initialize OpenTelemetry instrumentation on the FastAPI app.

    Falls back to no-op if OTLP endpoint is not configured.
    """
    if not otlp_endpoint:
        logger.info("telemetry.disabled", reason="no OTLP endpoint configured")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})

        provider = TracerProvider(
            resource=resource,
            sampler=trace.sampling.TraceBasedSampler(sample_rate),
        )

        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        FastAPIInstrumentor.instrument_app(app)

        logger.info(
            "telemetry.initialized",
            service=service_name,
            endpoint=otlp_endpoint,
            sample_rate=sample_rate,
        )
    except ImportError:
        logger.warning(
            "telemetry.import_error",
            hint="pip install opentelemetry-api opentelemetry-sdk "
            "opentelemetry-exporter-otlp-proto-http "
            "opentelemetry-instrumentation-fastapi",
        )
    except Exception as e:
        logger.error("telemetry.init_failed", error=str(e))
