# LangGraph checkpointing

Cycles compiled with `MemorySaver` support thread-scoped replay for debugging and future HITL resume.

## thread_id generation

`run_cycle()` builds:

```
thread_id = f"{HYDRA_CHECKPOINT_THREAD_PREFIX}{uuid4()}"
```

unless the caller passes an explicit `thread_id` (CLI `--thread-id`).

## MemorySaver limits

The in-process `MemorySaver` checkpointer does not survive process restarts. Production deployments should swap in Postgres or Redis checkpoint backends before enabling interrupt/resume.

## CLI flag

`stellarhydra-cycle --thread-id custom-id` reuses checkpoint state for repeated invocations in the same process.

See `src/stellarhydra/cli.py`, `graph/hydra_graph.py`, and `tests/test_graph.py`.
