# Redis signal cache

Implementation: `src/stellarhydra/integrations/signal_cache.py`

## Purpose

Cache healthy `RoutingSignal` objects between cycles to reduce StellarRoute API load and support short-term trend heuristics in the predictor.

## Key format

```
{HYDRA_REDIS_KEY_PREFIX}signals:{base}:{quote}
```

Default prefix: `hydra:`

Example: `hydra:signals:native:USDC`

## TTL

Controlled by `HYDRA_SIGNAL_TTL_SECONDS` (default `300` seconds).

## Operations

| Method | Behavior |
|--------|----------|
| `store(signal)` | Serialize and SET with TTL |
| `get(base, quote)` | GET and deserialize |
| `ping()` | Used by admin `/health` for Redis component |

## Redis databases

| DB | Service |
|----|---------|
| `0` | Signal cache (`REDIS_URL`) |
| `1` | Celery broker (`CELERY_BROKER_URL`) |
| `2` | Celery results (`CELERY_RESULT_BACKEND`) |

Use separate logical databases to avoid key collisions.
