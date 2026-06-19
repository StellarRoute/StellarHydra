# Celery workers

## App module

`src/stellarhydra/workers/celery_app.py` defines the Celery application.

## Task

`src/stellarhydra/workers/tasks.py`:

- `run_hydra_cycle` invokes `run_cycle()` from the LangGraph module.

## Start worker

```bash
celery -A stellarhydra.workers.celery_app worker --loglevel=info
```

## Broker configuration

| Variable | Default |
|----------|---------|
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` |

Use Redis DB `1` for broker and DB `2` for results to avoid colliding with signal cache on DB `0`.

## Scheduling

Periodic beat schedules are not enabled in v0 scaffold. Use external cron, Render cron jobs, or add `celery beat` in Phase 2.

## Testing

`tests/test_workers.py` verifies task registration and mocked execution.
