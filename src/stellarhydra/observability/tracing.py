# OpenTelemetry tracing hooks (optional, enabled via HYDRA_ENABLE_OTEL).
from __future__ import annotations

import logging

from stellarhydra.config import get_settings

logger = logging.getLogger(__name__)


def setup_tracing() -> None:
    settings = get_settings()
    if not settings.hydra_enable_otel:
        logger.debug("OpenTelemetry disabled (HYDRA_ENABLE_OTEL=false)")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning("OpenTelemetry packages not installed; tracing skipped")
        return

    resource = Resource.create({"service.name": "stellarhydra"})
    provider = TracerProvider(resource=resource)
    if settings.otel_exporter_otlp_endpoint:
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    logger.info("OpenTelemetry tracing configured")
