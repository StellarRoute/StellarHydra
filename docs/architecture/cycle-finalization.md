# Cycle finalization

The `finalize` node converts graph state into a `CycleResult` for API and CLI consumers.

## execution_status derivation

| Condition | Status |
|-----------|--------|
| `skip_execution` true (policy block or NO_OP) | `skipped` |
| Plan `dry_run` true | `dry_run` |
| `execution_result.success` true | `success` |
| Otherwise | `failed` |

`execution_result` is a dict set by the `execute` node; it is not a top-level `HydraState` field persisted across nodes except during the cycle.

## Other CycleResult fields

- `signals_collected`: count of routing signals gathered
- `predictions`: bottleneck list from predictor
- `plan`: final `DripActionPlan`

See `src/stellarhydra/graph/hydra_graph.py` (`execute`, `finalize`) and `models/predictions.py`.
