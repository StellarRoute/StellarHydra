# Celery task reference

Background work runs through `stellarhydra.workers.celery_app`.

## run_hydra_cycle

- **Name:** `stellarhydra.run_hydra_cycle`
- **Retries:** `max_retries=2`, `countdown=30` seconds on failure
- **Args:** optional `thread_id` forwarded to `run_cycle()`
- **Returns:** JSON-serializable `CycleResult` dict

## refresh_pair_watchlist

- **Name:** `stellarhydra.refresh_pair_watchlist`
- Calls `StellarRouteClient.fetch_pairs()` and returns up to 20 `base:quote` strings
- On API failure, falls back to `Settings.watchlist_pairs()` from env/YAML

## Worker settings

`celery_app.py` sets `worker_prefetch_multiplier=1` so long-running cycle tasks are not prefetched across workers.

Broker and result backend default to Redis DB 1 and 2 (`CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`).

See `tests/test_workers.py`.
