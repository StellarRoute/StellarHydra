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

## Drips Wave contributor workflow

- Maintainers mark Wave-eligible issues with the `Drip Wave` label and one complexity label: `complexity:low`, `complexity:medium`, or `complexity:high`.
- Contributors should pick an open, unassigned issue and check for active PRs before starting.
- During an active Wave cycle, maintainers should assign accepted contributors quickly with GitHub assignees so work is visible and duplicate effort is reduced.
- PR descriptions should mention the issue, the validation performed, and whether the change affects live Drips behavior or only dry-run planning.
- Do not replace StellarRoute routing or quote logic. PRD NG1 keeps StellarRoute authoritative; StellarHydra is a predictive overlay that reads through the StellarRoute HTTP API.
- Keep `DRIPS_DRY_RUN=true` unless a maintainer explicitly asks for sandbox credential testing.

## Pull requests

- Branch from `main`, open PRs against `main`. Use an issue-numbered name such as `feature/31-drips-wave-runbook`.
- Keep `DRIPS_DRY_RUN=true` unless explicitly testing sandbox Drips credentials.
- Ensure CI passes: `pytest`, `ruff check`, `mypy`.
- Use issue title prefixes: `[backend]`, `[integrations]`, `[documentation]`.
- Label Wave program issues with `Drip Wave` and `complexity:*` when applicable.

## Documentation changes

Place guides under `docs/`. Update README links when adding new top-level docs. Avoid em dashes in user-facing copy.

## Questions

Open a [GitHub issue](https://github.com/StellarRoute/StellarHydra/issues) with the `[documentation]` or `[backend]` prefix.
