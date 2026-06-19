# CLI reference

## `stellarhydra-cycle`

Entry point declared in `pyproject.toml`, implemented in `src/stellarhydra/cli.py`.

Runs a single LangGraph cycle and prints JSON to stdout.

```bash
pip install -e .
stellarhydra-cycle
```

Equivalent wrapper:

```bash
python scripts/run_cycle.py
```

## Exit behavior

- Prints `CycleResult` as JSON on success.
- Non-zero exit code on unhandled exceptions (same graph path as admin trigger).

## Environment

Reads the same `.env` variables as the API and Celery worker. Minimum requirements:

- Redis reachable if signal caching is expected
- StellarRoute reachable for live signals (cycle degrades gracefully if not)

## When to use CLI vs API vs Celery

| Mode | Use case |
|------|----------|
| CLI | Local debugging, CI smoke tests |
| Admin API | On-demand cycle from ops tooling |
| Celery | Scheduled production cycles |
