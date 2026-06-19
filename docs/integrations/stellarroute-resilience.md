# StellarRoute client resilience

The HTTP client uses Tenacity retries and per-pair degradation during watchlist collection.

## Retry policy

`fetch_signal()` is decorated with `@retry` (3 attempts, exponential backoff). Transient HTTP failures on a single pair retry before surfacing.

## Watchlist degradation

`fetch_watchlist_signals()` iterates `Settings.watchlist_pairs()`. On failure for one pair it logs the error and appends a synthetic signal with `stellarroute_healthy=False` instead of aborting the whole batch.

This differs from a single `fetch_signal()` call, where the exception propagates after retries exhaust.

## Timeouts

`STELLARROUTE_TIMEOUT_SECONDS` (default 15) bounds each httpx request.

See `tests/test_stellarroute_client.py::test_fetch_watchlist_degrades_on_error`.
