# Troubleshooting

## StellarRoute shows unreachable in `/health`

**Symptoms:** `"stellarroute": "unreachable"` in health JSON.

**Checks:**
1. Is StellarRoute API running? Default URL: `http://localhost:8080`
2. Is `STELLARROUTE_API_URL` correct in `.env`?
3. Firewall or Docker network isolation between containers?

Cycles still run but `collect_signals` may return empty signals.

## Redis shows unreachable

**Symptoms:** `"status": "degraded"`, `"redis": "unreachable"`.

**Checks:**
1. `docker-compose up -d redis`
2. `REDIS_URL` matches compose port (`redis://localhost:6379/0`)

Signal caching and Celery require Redis.

## Admin trigger returns 401

**Cause:** Missing or wrong `X-Admin-Api-Key` header.

**Fix:** Match `HYDRA_ADMIN_API_KEY` in `.env`.

## Admin trigger returns 500

Check API logs for graph exceptions. Common causes:
- Import errors after local code changes (re-run `pip install -e ".[dev]"`)
- Unexpected StellarRoute response shape (open an issue with response sample)

## Celery worker not processing tasks

1. Confirm worker is running: `celery -A stellarhydra.workers.celery_app worker --loglevel=info`
2. Confirm `CELERY_BROKER_URL` points to running Redis
3. Check worker logs for connection errors

## Drips live mode fails immediately

Ensure `DRIPS_API_KEY` is set and `DRIPS_DRY_RUN=false`. Verify API URL against current Drips Wave documentation.
