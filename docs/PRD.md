# StellarHydra Product Requirements Document

**Agentic Liquidity Balancer (ALB) for Stellar DEX routing**

| Field | Value |
|-------|-------|
| Version | 0.1 (draft) |
| Status | Scaffold / pre-alpha |
| Companion system | [StellarRoute](https://github.com/StellarRoute/StellarRoute) |
| Target repo | [StellarHydra](https://github.com/StellarRoute/StellarHydra) |

---

## 1. Problem Statement

StellarRoute computes optimal swap routes from **static, indexed on-chain state**: SDEX offers and Soroban AMM reserves unified in Postgres (`normalized_liquidity`), filtered by routing health (freshness, TVL, anomaly scoring), and served via REST (`/api/v1/quote`, `/api/v1/routes`, `/api/v1/orderbook`). Quotes are correct **at query time**, but they do not anticipate **where liquidity will be needed next**.

When trading volume shifts (market velocity, sentiment, scheduled events, or pool rebalancing), high-traffic paths can become under-funded before the indexer reflects the imbalance. Traders then see elevated slippage, excluded venues, or suboptimal multi-hop paths even though alternative routes exist.

**StellarHydra** closes this gap by acting as an Agentic Liquidity Balancer (ALB):

1. Ingest live signals from StellarRoute (quotes, routes, orderbook depth, health exclusions).
2. Predict near-term bottlenecks and volume shifts across asset pairs and hop sequences.
3. Proactively adjust **programmable liquidity streams** via [Drips Wave](https://drips.network/) so alternative multi-hop paths are better funded when traders query StellarRoute.

StellarRoute remains the **source of truth for execution routing**. StellarHydra is a **predictive overlay** that pre-positions liquidity, not a replacement router.

---

## 2. Target Users

| Persona | Need | How StellarHydra helps |
|---------|------|------------------------|
| **StellarRoute operators** | Keep quote quality high under load | Automated drip adjustments before slippage spikes |
| **Liquidity providers / treasuries** | Deploy capital efficiently across paths | Stream-based rebalancing tied to predicted demand |
| **Wallet / dApp integrators** | Reliable best-execution quotes | Fewer stale or thin-route failures at peak times |
| **Drips ecosystem builders** | Real-world streaming use cases on Stellar | ALB as reference integration for Wave programmable cash flows |

---

## 3. Goals and Non-Goals

### Goals

| ID | Goal |
|----|------|
| G1 | Predict liquidity bottlenecks 5-60 minutes ahead using StellarRoute API data and lightweight heuristics (Phase 1), extensible to ML (Phase 2+) |
| G2 | Recommend and execute Drips stream create/update/pause actions for target paths |
| G3 | Run as a multi-agent LangGraph workflow with auditable state transitions |
| G4 | Integrate with StellarRoute without modifying its Rust core (HTTP client + optional Redis signal cache) |
| G5 | Operate asynchronously via Redis-backed workers for periodic cycles and event triggers |
| G6 | Provide observability (metrics, structured logs, health endpoints) suitable for Phase A co-deployment |

### Non-Goals

| ID | Non-Goal | Rationale |
|----|----------|-----------|
| NG1 | Replace StellarRoute pathfinder or quote logic | Single responsibility; Rust engine stays authoritative |
| NG2 | On-chain swap execution (Phase B StellarRoute scope) | ALB funds paths; execution remains StellarRoute + Soroban router |
| NG3 | Full sentiment/NLP pipeline in v0 | Stub hooks only until labeled data exists |
| NG4 | Autonomous mainnet fund movement without guardrails | Human-in-the-loop or policy caps required before production |
| NG5 | Indexer duplication | All normalized liquidity reads go through StellarRoute API or shared Postgres read replica (future) |

---

## 4. Core Features

Each feature includes an acceptance criterion verifiable in CI or manual E2E.

### F1: Signal ingestion from StellarRoute

Poll or subscribe to StellarRoute endpoints:

- `GET /api/v1/pairs`, `/api/v1/markets`
- `GET /api/v1/orderbook/:base/:quote`
- `GET /api/v1/quote/:base/:quote` (amount, slippage_bps, quote_type)
- `GET /api/v1/routes/:base/:quote`
- `GET /health/deps` (indexer/API freshness proxy)

**Acceptance:** Given a configured `STELLARROUTE_API_URL`, a cycle loads at least one pair's quote + route and persists a normalized `RoutingSignal` record.

### F2: Bottleneck prediction agent

Analyze recent signal history (Redis cache or in-memory window) to flag pairs/paths where:

- Quote slippage exceeds configurable threshold vs. baseline
- Route path count drops or health exclusions increase
- Orderbook depth on primary hop falls below minimum

**Acceptance:** Predictor returns a ranked list of `BottleneckPrediction` with confidence, horizon_minutes, and affected path steps.

### F3: Drip decision agent

Map predictions to Drips actions: `create_stream`, `adjust_rate`, `pause_stream`, or `no_op`. Respect policy caps (max XLM per hour, allowed asset allowlist).

**Acceptance:** For a synthetic high-slippage signal, strategist emits a `DripActionPlan` with rationale and does not exceed configured caps.

### F4: Drips Wave integration

HTTP client for Drips Wave API (GitHub-authenticated). Supports dry-run mode writing plans to Redis/Postgres without API calls.

**Acceptance:** With `DRIPS_DRY_RUN=true`, executor logs intended API payload; with credentials + `DRIPS_DRY_RUN=false`, client posts to Wave sandbox (manual verification).

### F5: LangGraph orchestration

Multi-node graph: `collect_signals` → `predict` → `decide` → `execute` with edgeless `Command` routing and checkpointed state (`thread_id` per cycle).

**Acceptance:** `python -m stellarhydra.graph.hydra_graph` or `scripts/run_cycle.py` completes one full cycle in dry-run and prints final state summary.

### F6: Async worker queue

Celery (or compatible) tasks on Redis: `run_hydra_cycle`, `refresh_pair_watchlist`. Key naming: `hydra:signals:{pair}`, `hydra:cycle:{id}` with TTL.

**Acceptance:** Task enqueued via worker module imports; unit test mocks broker and asserts task registration.

### F7: Admin / health API

FastAPI service: `/health`, `/metrics`, `/admin/cycle/trigger` (auth required in production).

**Acceptance:** Health returns StellarRoute reachability and Redis connectivity status.

### F8: Security and audit

API key auth for admin routes, secret loading from env, structured audit log for every Drip action plan.

**Acceptance:** Unauthenticated admin request returns 401; audit entry contains action type, pair, amount, timestamp.

---

## 5. Technical Constraints

| Constraint | Detail |
|------------|--------|
| **Language** | Python 3.11+ |
| **Orchestration** | LangGraph (edgeless Command routing, MemorySaver dev / PostgresSaver prod) |
| **Queue / cache** | Redis 7+ (`REDIS_URL`); TTL on cache keys; consistent key prefix `hydra:` |
| **StellarRoute coupling** | HTTP only in v0; no Rust workspace dependency |
| **StellarRoute API surface** | Quote/routes read `normalized_liquidity` via API; optional Redis quote cache on StellarRoute side (`stellarroute:*` keys) is read-only for Hydra |
| **Drips** | Wave API; GitHub token or Wave API key at runtime |
| **Deployment** | Docker Compose (Redis + worker + API); Render/K8s skeleton in Phase 3 |
| **No dependency install in scaffold** | `pyproject.toml` / `requirements.txt` declare deps; CI uses them |
| **Mainnet safety** | Default `DRIPS_DRY_RUN=true`; explicit env flip for live streams |

### StellarRoute integration reference

| StellarRoute component | Hydra usage |
|------------------------|-------------|
| Indexer → `normalized_liquidity` | Indirect via quote/route API freshness |
| `crates/routing` health scoring | Mirror thresholds in Hydra policy config |
| API Redis cache | Optional read of cache metrics endpoint `/metrics/cache` |
| Kill switch (`stellarroute:kill_switches`) | Hydra must halt drip execution when StellarRoute reports kill switch active (future hook) |

---

## 6. Open Questions

| # | Question | Owner | Impact |
|---|----------|-------|--------|
| OQ1 | Which Drips Wave endpoints and auth model are canonical for stream CRUD on Stellar? | Drips / product | Blocks live F4 |
| OQ2 | Will Hydra share StellarRoute Postgres read replica or API-only? | Infra | Latency vs. coupling |
| OQ3 | Minimum viable pair watchlist: top N by volume or configurable YAML? | Product | Signal cost |
| OQ4 | Human-in-the-loop required for all mainnet drip changes, or only above cap? | Compliance | Graph HITL node |
| OQ5 | Soroban router contract address for path validation pre-drip? | StellarRoute contracts | On-chain alignment |
| OQ6 | Co-deploy with StellarRoute Phase A hosting (Render) or separate service? | Infra | CI/CD |
| OQ7 | Sentiment data source (X, Discord, Stellar expert) if pursued in Phase 2+? | ML | Feature scope |

---

## Appendix: Glossary

| Term | Definition |
|------|------------|
| **ALB** | Agentic Liquidity Balancer |
| **Drip** | Drips programmable cash flow stream |
| **Signal** | Normalized snapshot from StellarRoute APIs |
| **Cycle** | One LangGraph invocation: ingest → predict → decide → execute |
