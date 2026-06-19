# Predictor stress scoring

`predict_bottlenecks()` in `agents/predictor.py` ranks watchlist pairs using a weighted stress score built from each `RoutingSignal`.

## Unhealthy pairs

When `stellarroute_healthy` is false, the predictor emits a fixed **MEDIUM** prediction at confidence `0.6` with reason "StellarRoute API unhealthy for pair" and skips numeric scoring.

## Stress weights

| Signal condition | Weight added |
|------------------|--------------|
| `price_impact_bps >= slippage_alert_bps` | 0.4 |
| `orderbook_bid_depth < min_orderbook_depth_native` | 0.3 |
| `excluded_venue_count > 0` | 0.2 |
| `route_count <= 1` | 0.1 |

Thresholds come from YAML `policy` or env (`HYDRA_SLIPPAGE_ALERT_BPS`, etc.).

## Severity and filtering

- Pairs with `stress_score < 0.3` are dropped (no prediction).
- **LOW**: score in `[0.3, 0.4)`
- **MEDIUM**: score in `[0.4, 0.6)`
- **HIGH**: score `>= 0.6`

`confidence` is `min(stress_score, 0.95)`. Predictions sort descending by confidence.

See `tests/test_predictor.py` for worked examples.
