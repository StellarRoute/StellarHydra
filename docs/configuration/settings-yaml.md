# settings.yaml overlay

StellarHydra loads optional policy and StellarRoute defaults from `config/settings.yaml`. Environment variables always win for connection strings and secrets; YAML fills in policy thresholds and watchlist pairs when present.

## What the code reads

| YAML section | Keys consumed | Fallback |
|--------------|---------------|----------|
| `policy` | `slippage_alert_bps`, `min_orderbook_depth_native`, `prediction_horizon_minutes`, `allowed_assets` | Matching `HYDRA_*` env vars |
| `watchlist.pairs` | `base`, `quote` per entry | Merged with `HYDRA_WATCHLIST` |
| `stellarroute` | `quote_amount`, `default_slippage_bps` | Used by the StellarRoute client |

Sections named `redis` and `drips` in the sample file mirror env defaults but are **not** read by `Settings.yaml_config()` today. Use `REDIS_URL`, `HYDRA_REDIS_KEY_PREFIX`, and `DRIPS_DRY_RUN` instead.

## Watchlist merge order

`Settings.watchlist_pairs()` parses `HYDRA_WATCHLIST` first, then appends YAML `watchlist.pairs` without duplicates. Example env value: `native:USDC,USDC:native`.

## Allowed assets gate

When `policy.allowed_assets` is non-empty, the strategist returns `NO_OP` with `policy_ok=False` if either side of the top prediction pair is missing from the set.

See `src/stellarhydra/config.py` and `config/settings.yaml`.
