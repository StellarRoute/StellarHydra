# Local development setup

This guide walks through running StellarHydra on your machine. StellarHydra is a Python companion to [StellarRoute](https://github.com/StellarRoute/StellarRoute); it reads routing signals from the StellarRoute API and plans Drips Wave liquidity actions.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Application runtime |
| Docker + Compose | recent | Redis (required); optional full stack |
| StellarRoute API | running locally or remote | Signal source for watchlist pairs |

StellarRoute is not bundled in this repo. For local signal collection, start StellarRoute from its own repository (default API port `8080`).

## First-time setup

```bash
git clone https://github.com/StellarRoute/StellarHydra.git
cd StellarHydra
cp .env.example .env
pip install -e ".[dev]"
docker-compose up -d redis
```

Edit `.env` if your StellarRoute instance is not at `http://localhost:8080`. Keep `DRIPS_DRY_RUN=true` until you have sandbox Drips credentials.

## Run one cycle (CLI)

```bash
stellarhydra-cycle
# equivalent:
python scripts/run_cycle.py
```

A successful dry-run cycle prints a JSON `CycleResult` with predictions and the planned drip action (or `NO_OP`).

## Run the admin API

```bash
uvicorn stellarhydra.api.main:app --host 0.0.0.0 --port 8090
```

| Endpoint | Auth | Notes |
|----------|------|-------|
| `GET /health` | none | Checks StellarRoute reachability and Redis ping |
| `GET /metrics` | none | Prometheus exposition format |
| `POST /admin/cycle/trigger` | `X-Admin-Api-Key` header | Runs one LangGraph cycle synchronously |

## Run Celery worker (async cycles)

```bash
celery -A stellarhydra.workers.celery_app worker --loglevel=info
```

## Verify the install

```bash
pytest tests -v
ruff check src tests
```

See also [configuration/env-vars.md](../configuration/env-vars.md) and [architecture/langgraph-workflow.md](../architecture/langgraph-workflow.md).
