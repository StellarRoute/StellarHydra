# Contributing to StellarHydra

Thank you for helping build the Agentic Liquidity Balancer for Stellar DEX routing.

## Before you start

1. Read [docs/PRD.md](docs/PRD.md) for product scope and non-goals.
2. Read [docs/ROADMAP.md](docs/ROADMAP.md) for phase gates (0 through 3).
3. Skim [README.md](README.md) for architecture and configuration.

StellarHydra never replaces StellarRoute quote logic or executes on-chain swaps. All liquidity reads go through the StellarRoute HTTP API.

## Development workflow

```bash
git checkout main && git pull
git checkout -b feature/your-change
cp .env.example .env   # if first time
pip install -e ".[dev]"
docker-compose up -d redis
pytest tests -v
```

## Code layout

| Path | Responsibility |
|------|----------------|
| `src/stellarhydra/graph/` | LangGraph workflow (`hydra_graph.py`, state) |
| `src/stellarhydra/agents/` | Predictor, strategist, executor |
| `src/stellarhydra/integrations/` | StellarRoute client, Drips client, Redis cache |
| `src/stellarhydra/api/` | FastAPI admin service |
| `src/stellarhydra/workers/` | Celery tasks |

## Pull requests

- Branch from `main`, open PRs against `main`.
- Keep `DRIPS_DRY_RUN=true` unless explicitly testing sandbox Drips credentials.
- Ensure CI passes: `pytest`, `ruff check`, `mypy`.
- Use issue title prefixes: `[backend]`, `[integrations]`, `[documentation]`.
- Label Wave program issues with `Drip Wave` and `complexity:*` when applicable.

## Documentation changes

Place guides under `docs/`. Update README links when adding new top-level docs. Avoid em dashes in user-facing copy.

## Questions

Open a [GitHub issue](https://github.com/StellarRoute/StellarHydra/issues) with the `[documentation]` or `[backend]` prefix.
