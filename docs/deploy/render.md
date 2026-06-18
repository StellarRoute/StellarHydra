# Render deployment skeleton for StellarHydra (Phase 3).
#
# Prerequisites: StellarRoute Phase A API URL, Redis instance, secrets in Render dashboard.

## Services

| Service | Type | Command |
|---------|------|---------|
| hydra-api | Web | `uvicorn stellarhydra.api.main:app --host 0.0.0.0 --port $PORT` |
| hydra-worker | Worker | `celery -A stellarhydra.workers.celery_app worker --loglevel=info` |
| redis | Redis | Managed Redis or Render Redis |

## Environment

Set all variables from `.env.example`. Bind HTTP to `0.0.0.0:$PORT` per Render requirements.

## Health checks

- Path: `/health`
- Expect `200` with `redis: ok` when cache is reachable

## Notes

- Keep `DRIPS_DRY_RUN=true` until Drips Wave API contract is confirmed (PRD OQ1).
- Co-locate with StellarRoute Phase A when hosting credits are available (PRD OQ6).
