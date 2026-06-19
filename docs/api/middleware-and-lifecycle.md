# FastAPI lifecycle and request logging

## Startup (`api/main.py` lifespan)

On startup the app:

1. Configures structlog via `configure_logging()`
2. Optionally enables OpenTelemetry when `HYDRA_ENABLE_OTEL` is true
3. Emits secret-configuration warnings (for example default admin key)

Shutdown is currently a no-op placeholder.

## Request middleware

`RequestLoggingMiddleware` assigns or propagates `X-Request-ID`, measures wall time, and logs structured fields:

- `request_id`
- `method`
- `path`
- `status`
- `duration_ms`

The response echoes `X-Request-ID` when present.

See `src/stellarhydra/api/middleware.py` and `observability/logging_config.py`.
