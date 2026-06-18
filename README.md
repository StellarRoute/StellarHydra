# StellarHydra

[![CI](https://github.com/StellarRoute/StellarHydra/actions/workflows/ci.yml/badge.svg)](https://github.com/StellarRoute/StellarHydra/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Agentic Liquidity Balancer (ALB) for Stellar DEX routing.**

StellarHydra is a Python companion to [StellarRoute](https://github.com/StellarRoute/StellarRoute). It predicts where liquidity will be needed on Stellar DEX paths and proactively adjusts [Drips Wave](https://drips.network/) programmable cash flow streams so routes stay well-funded. StellarRoute remains the authoritative router; StellarHydra is a predictive overlay, not a replacement.

| | StellarRoute | StellarHydra |
|---|--------------|--------------|
| **Role** | Quote and route execution from indexed on-chain state | Predict bottlenecks and pre-position liquidity |
| **Stack** | Rust (indexer, API, routing engine) | Python (LangGraph, FastAPI, Celery) |
| **Coupling** | Source of truth for `/api/v1/quote`, `/api/v1/routes`, orderbooks | HTTP client to StellarRoute API only (v0) |

---

## Problem and solution

StellarRoute serves optimal swap routes from SDEX offers and Soroban AMM reserves at query time. When volume shifts, high-traffic paths can become under-funded before the indexer reflects the imbalance. Traders then see elevated slippage or thin routes even when alternatives exist.

StellarHydra closes that gap:

1. **Ingest** live routing signals from the StellarRoute API (quotes, routes, orderbook depth, health).
2. **Predict** near-term bottlenecks and volume shifts across asset pairs and hop sequences.
3. **Decide** policy-checked actions (create, adjust, or pause Drips streams).
4. **Execute** against the Drips Wave API, or log intended payloads in dry-run mode.

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │         StellarRoute API            │
                    │  quotes · routes · orderbooks       │
                    └─────────────────┬───────────────────┘
                                      │ HTTP
                                      ▼
┌──────────────┐   collect_signals   ┌──────────────┐   predict   ┌──────────────┐
│    Redis     │◄────────────────────│  LangGraph   │────────────►│   Predictor  │
│ signal cache │                     │  multi-agent │             │    agent     │
│ + Celery     │                     │    loop      │             └──────┬───────┘
└──────┬───────┘                     └──────┬───────┘                    │
       │                                    │ decide                     │
       │                                    ▼                            │
       │                             ┌──────────────┐                    │
       │                             │  Strategist  │◄───────────────────┘
       │                             │    agent     │
       │                             └──────┬───────┘
       │                                    │ execute
       │                                    ▼
       │                             ┌──────────────┐
       └────────────────────────────►│   Executor   │──────► Drips Wave API
                                     │  (+ audit)   │        (or dry-run log)
                                     └──────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  FastAPI admin service  ·  /health  ·  /metrics  ·  /admin/cycle/trigger    │
└─────────────────────────────────────────────────────────────────────────────┘
```

**LangGraph workflow** (`collect_signals` → `predict` → `decide` → `execute`) uses edgeless `Command` routing with checkpointed state per cycle. **Redis** backs the signal cache (`hydra:signals:*`) and Celery broker. **Celery workers** run periodic cycles asynchronously. **FastAPI** exposes health, Prometheus metrics, and an authenticated admin trigger.

See [docs/PRD.md](docs/PRD.md) for full requirements and [docs/architecture/hydra_graph_planned.mmd](docs/architecture/hydra_graph_planned.mmd) for the planned graph diagram.

---

## Quick start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for Redis and optional full stack)
- A running [StellarRoute](https://github.com/StellarRoute/StellarRoute) API (local default: `http://localhost:8080`) for live signals, or tolerate degraded collection in dry-run

### Clone and configure

```bash
git clone https://github.com/StellarRoute/StellarHydra.git
cd StellarHydra
cp .env.example .env
# Edit .env (see Configuration below)
```

### Start Redis (minimum for local dev)

```bash
docker-compose up -d redis
```

To run the full stack (Redis, API, Celery worker):

```bash
docker-compose up -d
```

### Install and run one cycle

```bash
pip install -e ".[dev]"

# CLI entry point
stellarhydra-cycle

# Or equivalent script
python scripts/run_cycle.py
```

With `DRIPS_DRY_RUN=true` (default), the cycle completes without live Drips API calls and prints a JSON `CycleResult`.

### Start the admin API locally

```bash
uvicorn stellarhydra.api.main:app --host 0.0.0.0 --port 8090
```

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /health` | None | StellarRoute and Redis reachability |
| `GET /metrics` | None | Prometheus metrics |
| `POST /admin/cycle/trigger` | `X-Admin-Api-Key` | Run one cycle on demand |

---

## Project structure

```
StellarHydra/
├── src/stellarhydra/
│   ├── agents/           # Predictor, strategist, executor, sentiment stub
│   ├── api/              # FastAPI app, auth, middleware
│   ├── graph/            # LangGraph workflow (hydra_graph.py, state, HITL stub)
│   ├── integrations/     # StellarRoute client, Drips client, Redis signal cache
│   ├── models/           # RoutingSignal, BottleneckPrediction, DripActionPlan
│   ├── observability/    # Structured logging, metrics, OpenTelemetry hooks
│   ├── security/         # Secrets validation, audit logging
│   ├── workers/          # Celery app and tasks (run_hydra_cycle)
│   ├── config.py         # Pydantic settings from env
│   └── cli.py            # stellarhydra-cycle CLI
├── tests/                # Unit tests (graph, agents, API, integrations)
├── scripts/run_cycle.py  # Thin wrapper around CLI
├── config/settings.yaml
├── docs/
│   ├── PRD.md
│   ├── ROADMAP.md
│   └── deploy/render.md
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

---

## Configuration

All runtime settings load from environment variables. Copy [`.env.example`](.env.example) to `.env` and adjust.

| Variable | Default | Purpose |
|----------|---------|---------|
| `STELLARROUTE_API_URL` | `http://localhost:8080` | StellarRoute REST base URL |
| `STELLARROUTE_TIMEOUT_SECONDS` | `15` | HTTP timeout for StellarRoute client |
| `REDIS_URL` | `redis://localhost:6379/0` | Signal cache |
| `HYDRA_REDIS_KEY_PREFIX` | `hydra:` | Redis key namespace |
| `HYDRA_SIGNAL_TTL_SECONDS` | `300` | TTL on cached signals |
| `DRIPS_API_URL` | `https://api.drips.network` | Drips Wave API base |
| `DRIPS_API_KEY` | (empty) | Required when `DRIPS_DRY_RUN=false` |
| `DRIPS_DRY_RUN` | `true` | Log plans instead of calling Drips |
| `HYDRA_MAX_DRIP_XLM_PER_HOUR` | `1000` | Policy cap for drip actions |
| `HYDRA_SLIPPAGE_ALERT_BPS` | `100` | Slippage threshold for predictions |
| `HYDRA_PREDICTION_HORIZON_MINUTES` | `30` | Prediction lookahead window |
| `HYDRA_WATCHLIST` | `native:USDC,USDC:native` | Comma-separated base:quote pairs |
| `HYDRA_ADMIN_API_KEY` | `change-me-in-production` | Protects admin routes |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Celery result backend |

Additional keys for observability and LangGraph checkpoints are documented in `.env.example`.

---

## Development

### Tests and lint

```bash
pytest tests -v
ruff check src tests
mypy src/stellarhydra
```

CI runs the same checks on every push and pull request to `main`.

### Celery worker (async cycles)

```bash
celery -A stellarhydra.workers.celery_app worker --loglevel=info
```

### Contributing

StellarHydra is built as a reference integration for **Drips Wave** programmable liquidity on Stellar, alongside the StellarRoute routing stack.

1. Read [docs/PRD.md](docs/PRD.md) and [docs/ROADMAP.md](docs/ROADMAP.md) to understand scope and phase gates.
2. Pick an open issue labeled [`help wanted`](https://github.com/StellarRoute/StellarHydra/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) or file a new one with the `[backend]`, `[integrations]`, or `[documentation]` prefix.
3. Branch from `main`, open a PR against `main`, and ensure CI passes.
4. Keep `DRIPS_DRY_RUN=true` unless you are explicitly testing sandbox Drips credentials.

Phase-scoped work is tracked in [GitHub Issues](https://github.com/StellarRoute/StellarHydra/issues). Documentation gaps (for example ARCHITECTURE.md and ADR for Postgres read replica vs API-only) are listed there.

### Deployment

See [docs/deploy/render.md](docs/deploy/render.md) for Render deployment notes. Default to dry-run until the Drips Wave API contract is confirmed (PRD OQ1).

---

## Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **0** | Scaffold: repo layout, deps, CI, docker-compose | Current |
| **1** | Core loop: LangGraph E2E, StellarRoute client, Drips dry-run | Next |
| **2** | Feature complete: Celery, Redis cache, policy caps, watchlist, retries | Planned |
| **3** | Production hardening: auth, metrics, OTel, Docker deploy, HITL stub | Planned |

Full exit criteria, timeline, and StellarRoute milestone alignment: [docs/ROADMAP.md](docs/ROADMAP.md).

---

## Non-goals and guardrails

StellarHydra intentionally does **not**:

| Guardrail | Rationale |
|-----------|-----------|
| Replace StellarRoute pathfinder or quote logic | Rust engine stays authoritative (NG1) |
| Execute on-chain swaps | Execution remains StellarRoute + Soroban router (NG2) |
| Run a full sentiment/NLP pipeline in v0 | Stub hooks only until labeled data exists (NG3) |
| Move mainnet funds without guardrails | Default dry-run, policy caps, HITL required before production (NG4) |
| Duplicate the StellarRoute indexer | All liquidity reads go through StellarRoute API (NG5) |

---

## License

MIT. See [LICENSE](LICENSE).

---

## Links

- **StellarHydra:** https://github.com/StellarRoute/StellarHydra
- **StellarRoute (companion router):** https://github.com/StellarRoute/StellarRoute
- **Drips Wave:** https://drips.network/
