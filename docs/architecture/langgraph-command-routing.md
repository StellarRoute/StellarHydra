# LangGraph Command routing

`build_hydra_graph()` uses edgeless routing via `Command(update=..., goto=...)` instead of static conditional edges.

## Node destinations

Each node declares allowed `destinations` when registered:

- `collect_signals` → `predict`
- `predict` → `decide`
- `decide` → `execute` or `finalize`
- `execute` → `finalize`
- `finalize` → `END`

## decide branching

When the plan is `NO_OP` or `policy_ok` is false, `decide` returns `goto="finalize"` and sets `skip_execution=True`. Otherwise it routes to `execute`.

This matches the planned Mermaid diagram in `docs/architecture/hydra_graph_planned.mmd` but documents the runtime `Command` API explicitly.

See `src/stellarhydra/graph/hydra_graph.py`.
