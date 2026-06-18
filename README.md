# StellarHydra — Agentic Liquidity Balancer for Stellar DEX routing

StellarHydra is a Python/LangGraph companion to [StellarRoute](https://github.com/StellarRoute/StellarRoute). It predicts liquidity bottlenecks on Stellar DEX paths and proactively adjusts [Drips](https://drips.network/) programmable cash flow streams so optimal routes stay well-funded.

## Architecture

```
StellarRoute API (quotes, routes, orderbooks)
        │
        ▼
  collect_signals ──► predict ──► decide ──► execute (Drips)
        │                                      │
        └──────── Redis signal cache ◄─────────┘
```

See [docs/PRD.md](docs/PRD.md) and [docs/ROADMAP.md](docs/ROADMAP.md).

## Quick start

```bash
cp .env.example .env
docker-compose up -d redis

# Install (not done in scaffold pass)
pip install -e ".[dev]"

# Run one dry-run cycle (requires StellarRoute API or tolerates degraded signals)
python scripts/run_cycle.py

# Start admin API
uvicorn stellarhydra.api.main:app --host 0.0.0.0 --port 8090
```

## Environment

| Variable | Purpose |
|----------|---------|
| `STELLARROUTE_API_URL` | StellarRoute REST base URL |
| `REDIS_URL` | Signal cache + Celery broker |
| `DRIPS_DRY_RUN` | Default `true`; set `false` only with `DRIPS_API_KEY` |
| `HYDRA_ADMIN_API_KEY` | Protects `/admin/cycle/trigger` |

## Development

```bash
pytest tests -v
ruff check src tests
celery -A stellarhydra.workers.celery_app worker --loglevel=info
```

## Deployment

See [docs/deploy/render.md](docs/deploy/render.md) for Render skeleton notes.

## License

MIT
