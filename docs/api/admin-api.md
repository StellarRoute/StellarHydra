# Admin API reference

FastAPI app: `src/stellarhydra/api/main.py`

## Start locally

```bash
uvicorn stellarhydra.api.main:app --host 0.0.0.0 --port 8090
```

Default port comes from `HYDRA_API_PORT`.

## Endpoints

### `GET /health`

No authentication. Returns dependency status:

```json
{
  "status": "ok",
  "components": {
    "stellarroute": "ok",
    "redis": "ok"
  }
}
```

`status` is `degraded` when Redis is unreachable. StellarRoute unreachable is reported in `components` but does not alone flip top-level status.

### `GET /metrics`

No authentication. Prometheus text exposition (`prometheus_client.generate_latest`).

Metrics include `hydra_cycle_total`, `hydra_cycle_duration_seconds`, and `hydra_drip_actions_total` (see observability docs).

### `POST /admin/cycle/trigger`

**Auth:** header `X-Admin-Api-Key` must match `HYDRA_ADMIN_API_KEY`.

Runs `run_cycle()` synchronously. Returns `CycleResult` JSON. HTTP 500 on unhandled graph errors.

Example:

```bash
curl -X POST http://localhost:8090/admin/cycle/trigger \
  -H "X-Admin-Api-Key: change-me-in-production"
```

## Middleware

`RequestLoggingMiddleware` logs request metadata. Startup runs `validate_runtime_secrets()` and warns on insecure defaults (e.g. default admin key in production).
