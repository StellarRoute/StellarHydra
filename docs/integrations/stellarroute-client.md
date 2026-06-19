# StellarRoute client

Implementation: `src/stellarhydra/integrations/stellarroute_client.py`

## Purpose

Fetch routing signals for watchlist pairs from the StellarRoute REST API. StellarHydra does not index chain state directly.

## Configuration

- `STELLARROUTE_API_URL` (default `http://localhost:8080`)
- `STELLARROUTE_TIMEOUT_SECONDS` (default `15`)

## Methods (conceptual)

| Method | StellarRoute path | Used for |
|--------|-------------------|----------|
| `health_check()` | health endpoint | Admin `/health` component |
| `fetch_watchlist_signals()` | quotes/routes for each `HYDRA_WATCHLIST` pair | Cycle signal collection |

## Signal model

Signals map to `RoutingSignal` (`models/signals.py`) with fields for base/quote assets, slippage, depth, freshness, and `stellarroute_healthy`.

## Failure modes

Network errors and HTTP failures propagate from `collect_signals`, which catches them and continues with empty signals plus an error string in graph state.

## Testing

Unit tests mock HTTP responses in `tests/test_stellarroute_client.py`.
