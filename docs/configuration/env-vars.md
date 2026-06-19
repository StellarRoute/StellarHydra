# Environment variables

Settings load from `.env` via Pydantic (`src/stellarhydra/config.py`). Copy `.env.example` as a starting point.

## StellarRoute

| Variable | Default | Description |
|----------|---------|-------------|
| `STELLARROUTE_API_URL` | `http://localhost:8080` | Base URL for quotes, routes, health |
| `STELLARROUTE_TIMEOUT_SECONDS` | `15` | HTTP client timeout |

## Redis

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379/0` | Signal cache database |
| `HYDRA_REDIS_KEY_PREFIX` | `hydra:` | Key namespace |
| `HYDRA_SIGNAL_TTL_SECONDS` | `300` | TTL for cached signals |

Cached keys follow the pattern `{prefix}signals:{base}:{quote}`.

## Drips Wave

| Variable | Default | Description |
|----------|---------|-------------|
| `DRIPS_API_URL` | `https://api.drips.network` | Drips API base |
| `DRIPS_API_KEY` | empty | Required when `DRIPS_DRY_RUN=false` |
| `DRIPS_DRY_RUN` | `true` | Log plans instead of calling Drips |

## Policy

| Variable | Default | Description |
|----------|---------|-------------|
| `HYDRA_MAX_DRIP_XLM_PER_HOUR` | `1000` | Cap for drip actions |
| `HYDRA_SLIPPAGE_ALERT_BPS` | `100` | Slippage threshold (basis points) |
| `HYDRA_PREDICTION_HORIZON_MINUTES` | `30` | Prediction lookahead |
| `HYDRA_WATCHLIST` | `native:USDC` | Comma-separated `base:quote` pairs |

## Admin API

| Variable | Default | Description |
|----------|---------|-------------|
| `HYDRA_API_HOST` | `0.0.0.0` | Bind address |
| `HYDRA_API_PORT` | `8090` | Bind port |
| `HYDRA_ADMIN_API_KEY` | `change-me-in-production` | Protects `/admin/*` routes |

## Celery

| Variable | Default | Description |
|----------|---------|-------------|
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Task broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Result backend |

## Observability

| Variable | Default | Description |
|----------|---------|-------------|
| `HYDRA_LOG_LEVEL` | `INFO` | Python log level |
| `HYDRA_ENABLE_OTEL` | `false` | Enable OpenTelemetry export |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | empty | OTLP collector URL |
