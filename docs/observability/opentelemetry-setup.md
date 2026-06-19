# OpenTelemetry setup

Tracing is opt-in via `HYDRA_ENABLE_OTEL=true`.

## Required packages

`observability/tracing.py` imports OpenTelemetry SDK and OTLP exporter modules. These are **not** listed in `pyproject.toml` today. Install manually when enabling tracing:

```
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
```

If imports fail, startup logs a warning and continues without tracing.

## Configuration

| Variable | Purpose |
|----------|---------|
| `HYDRA_ENABLE_OTEL` | Master switch |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP gRPC endpoint for span export |

Service name is hardcoded to `stellarhydra` in the `Resource` attributes.

See `src/stellarhydra/observability/tracing.py`.
