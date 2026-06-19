# Testing guide

## Run all tests

```bash
pytest tests -v
```

## Test layout

| File | Covers |
|------|--------|
| `tests/test_graph.py` | LangGraph node routing and `run_cycle` |
| `tests/test_predictor.py` | Bottleneck heuristics |
| `tests/test_strategist.py` | Policy caps and action selection |
| `tests/test_drips_client.py` | Drips dry-run and HTTP mocks |
| `tests/test_stellarroute_client.py` | StellarRoute HTTP client |
| `tests/test_api.py` | FastAPI health, metrics, admin auth |
| `tests/test_workers.py` | Celery task wiring |

## Lint and type check

```bash
ruff check src tests
mypy src/stellarhydra
```

CI (`.github/workflows/ci.yml`) runs pytest, ruff, and mypy on every push and PR to `main`.

## Writing new tests

- Mock external HTTP (StellarRoute, Drips) with `pytest` fixtures or `unittest.mock`.
- Use `DRIPS_DRY_RUN=true` in test env.
- Graph tests should not require live Redis; patch `SignalCache` when needed.
