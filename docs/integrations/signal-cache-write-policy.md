# Signal cache write policy

Redis caching during `collect_signals` only persists **healthy** StellarRoute signals.

## collect_signals behavior

In `hydra_graph.py`, after fetching watchlist signals the node loops signals and calls `SignalCache.set()` only when `signal.stellarroute_healthy` is true. Unhealthy or degraded pairs are still passed to prediction but are not written to Redis.

## Key format

`SignalCache` keys use the pair string form `base:quote` (for example `native:USDC`), prefixed with `HYDRA_REDIS_KEY_PREFIX`. TTL comes from `HYDRA_SIGNAL_TTL_SECONDS`.

`get(pair)` expects the combined pair string, not separate base and quote arguments.

See `src/stellarhydra/integrations/signal_cache.py` and the `collect_signals` node in `hydra_graph.py`.
