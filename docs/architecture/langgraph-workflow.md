# LangGraph workflow

The core cycle lives in `src/stellarhydra/graph/hydra_graph.py`. It uses LangGraph `Command` routing with an in-memory checkpointer (`MemorySaver`).

## Node sequence

```
START -> collect_signals -> predict -> decide -> execute -> finalize -> END
                                      \-> finalize (NO_OP or policy block)
```

| Node | Function | Purpose |
|------|----------|---------|
| `collect_signals` | `collect_signals()` | Fetch watchlist signals via `StellarRouteClient`, cache healthy signals in Redis |
| `predict` | `predict()` | Run `predict_bottlenecks()` over collected signals |
| `decide` | `decide()` | Map predictions to a policy-checked `DripActionPlan` via strategist |
| `execute` | `execute()` | Call `execute_drip_plan()` (live or dry-run) |
| `finalize` | `finalize()` | Build `CycleResult` with status and errors |

## Error handling

`collect_signals` catches exceptions and continues to `predict` with empty signals and an error string in state. This lets the admin API and Celery worker report partial failures instead of crashing the graph.

## Entry points

- **CLI / admin trigger:** `run_cycle()` compiles the graph and invokes it once.
- **Celery:** `stellarhydra.workers.tasks.run_hydra_cycle` wraps `run_cycle()`.

## State

Graph state is typed as `HydraState` (`src/stellarhydra/graph/state.py`). See [state-model.md](state-model.md).

## HITL stub

`src/stellarhydra/graph/hitl.py` holds a placeholder for human-in-the-loop approval before live Drips execution (Phase 3).
