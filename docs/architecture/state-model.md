# Graph state model

`HydraState` is a `TypedDict` in `src/stellarhydra/graph/state.py` passed between LangGraph nodes.

## Fields

| Field | Type | Set by | Description |
|-------|------|--------|-------------|
| `cycle_id` | `str` | `collect_signals` | UUID for this cycle run |
| `signals` | `list[RoutingSignal]` | `collect_signals` | Raw StellarRoute signals for watchlist pairs |
| `predictions` | `list[BottleneckPrediction]` | `predict` | Heuristic bottleneck forecasts |
| `action_plan` | `DripActionPlan` | `decide` | Planned Drips action with policy metadata |
| `skip_execution` | `bool` | `decide` | True when action is `NO_OP` or policy blocks execution |
| `execution_status` | `str` | `execute` | Result label (e.g. `dry_run`, `success`, `error`) |
| `errors` | `list[str]` | any node | Non-fatal error messages accumulated across nodes |

## Result object

`run_cycle()` returns a Pydantic `CycleResult` (`models/predictions.py`) suitable for JSON serialization from the admin API:

```json
{
  "cycle_id": "...",
  "execution_status": "dry_run",
  "predictions": [...],
  "action_plan": {...}
}
```

## Checkpointing

The graph uses `MemorySaver` with thread IDs prefixed by `HYDRA_CHECKPOINT_THREAD_PREFIX` (default `cycle-`). Persistent Postgres checkpointing is a future enhancement tracked in GitHub issues.
