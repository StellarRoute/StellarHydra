# HydraState error accumulation

Graph state uses LangGraph reducers so errors from multiple nodes merge instead of overwriting.

## errors field

In `graph/state.py`, `errors` is typed as:

```python
Annotated[list[str], operator.add]
```

Each node may return `{"errors": ["message"]}` and LangGraph concatenates lists across steps.

## Where errors are appended

- `collect_signals`: StellarRoute fetch failures (non-degraded path)
- `decide`: policy or planning failures
- `execute`: Drips client failures

Downstream nodes should treat a non-empty `errors` list as diagnostic context; execution may still complete with `execution_status=failed`.
