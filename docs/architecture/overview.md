# Architecture overview

StellarHydra is a predictive overlay on [StellarRoute](https://github.com/StellarRoute/StellarRoute). It ingests live routing signals, predicts liquidity bottlenecks, and plans Drips Wave stream adjustments under policy caps.

## Component map

```
StellarRoute API  --->  StellarRouteClient  --->  SignalCache (Redis)
                              |
                              v
                        LangGraph cycle
                     (collect -> predict -> decide -> execute)
                              |
                              v
                        DripsClient (or dry-run log)
```

## Runtime processes

| Process | Entry point | Port (default) |
|---------|-------------|----------------|
| CLI cycle | `stellarhydra-cycle` / `scripts/run_cycle.py` | n/a |
| Admin API | `stellarhydra.api.main:app` | 8090 |
| Celery worker | `stellarhydra.workers.celery_app` | n/a |

## Source layout

```
src/stellarhydra/
  graph/hydra_graph.py    # LangGraph StateGraph + run_cycle()
  agents/                 # predict, decide, execute logic
  integrations/           # HTTP clients and Redis cache
  api/                    # FastAPI health, metrics, admin trigger
  workers/                # Celery task wrapper
  models/                 # RoutingSignal, BottleneckPrediction, DripActionPlan
  observability/          # logging, metrics, OpenTelemetry hooks
  security/               # secrets validation, audit logging
  config.py               # Pydantic settings from env
```

## Design constraints (from PRD)

- StellarRoute remains authoritative for quotes and routes.
- No on-chain swap execution in Hydra.
- Default `DRIPS_DRY_RUN=true` until Drips contract is confirmed.
- All liquidity state reads go through StellarRoute API, not a duplicated indexer.

See [langgraph-workflow.md](langgraph-workflow.md) for node-level detail.
