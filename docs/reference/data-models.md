# Data models reference

Pydantic models in `src/stellarhydra/models/` define the Hydra cycle wire format.

## RoutingSignal (`models/signals.py`)

| Field | Type | Notes |
|-------|------|-------|
| `base_asset`, `quote_asset` | str | Pair legs |
| `path` | list[PathStep] | Each step has `selling_asset`, `buying_asset`, `venue` |
| `price_impact_bps` | int \| None | From StellarRoute quote |
| `orderbook_bid_depth` | float \| None | Summed bid depth |
| `route_count` | int | Alternate routes available |
| `excluded_venue_count` | int | Policy-filtered venues |
| `stellarroute_healthy` | bool | False when fetch degraded |

`pair_key()` returns `"base:quote"`.

## BottleneckPrediction (`models/predictions.py`)

Severity enum: `LOW`, `MEDIUM`, `HIGH`. Includes `confidence`, `horizon_minutes`, `reason`, `affected_hops`, optional `predicted_slippage_bps`.

## DripActionPlan

`DripActionType`: `CREATE_STREAM`, `ADJUST_RATE`, `NO_OP`, `PAUSE_STREAM` (last is defined but unused in strategist today).

Fields: `pair`, `stream_amount_xlm`, `target_path`, `rationale`, `dry_run`, `policy_ok`.

## CycleResult

Returned by `finalize`: `signals_collected`, `predictions`, `plan`, `execution_status` (`skipped`, `dry_run`, `success`, `failed`).
