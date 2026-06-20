# Architecture

**Agentic Liquidity Balancer (ALB) — system architecture and contributor guardrails**

| Field | Value |
|-------|-------|
| Status | Draft / Phase 0 |
| References | [PRD](PRD.md), [Architecture overview](architecture/overview.md), [LangGraph workflow](architecture/langgraph-workflow.md) |
| Companion system | [StellarRoute](https://github.com/StellarRoute/StellarRoute) |

---

## 1. ALB coverage model

StellarHydra operates as a **predictive overlay** on top of the StellarRoute routing stack.
Its coverage model addresses the gap between **static indexed state** (what StellarRoute knows at query time)
and **dynamic liquidity demand** (where capital will be needed in the next 5-60 minutes).

### Coverage scope

```
                    StellarRoute scope
+-----------------------------------------------------------+
|  SDEX offers . Soroban AMM reserves . normalized liquidity  |
|  +-----------------------------------------------------+  |
|  |  Route engine (Rust) -> quotes, paths, orderbook     |  |
|  +----------------------+------------------------------+  |
|                         | HTTP / API                      |
+-------------------------+---------------------------------+
                          v
+-----------------------------------------------------------+
|  StellarHydra ALB scope                                    |
|  +----------+  +-----------+  +--------+  +-----------+  |
|  | Signals  |-> | Predict   |-> | Decide |-> | Execute   |  |
|  | (ingest) |  | (analyze) |  | (plan)  |  | (drip)     |  |
|  +----------+  +-----------+  +--------+  +-----------+  |
|                         |                                  |
|                         v                                  |
|              Drips Wave programmable streams                |
+-----------------------------------------------------------+
```

### What the ALB covers

| Layer | Covered by | Detail |
|-------|-----------|--------|
| **State indexing** | StellarRoute | SDEX offers, Soroban AMM reserves -> Postgres -> API |
| **Route computation** | StellarRoute | Pathfinding, multi-hop, health scoring |
| **Quote serving** | StellarRoute | REST `/api/v1/quote`, `/api/v1/routes`, `/api/v1/orderbook` |
| **Signal ingestion** | Hydra `collect_signals` | Poll StellarRoute API, persist to Redis cache |
| **Bottleneck prediction** | Hydra `predict` | Threshold-based heuristics on slippage, depth, path health |
| **Drip planning** | Hydra `decide` | Map predictions to stream create/adjust/pause under policy caps |
| **Stream execution** | Hydra `execute` | Drips Wave API calls (or dry-run log) |

---

## 2. Data flow

Each **cycle** invokes the four-node LangGraph in sequence.
Checkpointed state (`thread_id` per cycle) ensures auditability.

```
+--------------+     +--------------+     +--------------+     +--------------+
|  Collect     |---->|   Predict    |---->|    Decide    |---->|   Execute    |
|  Signals     |     |              |     |              |     |              |
|              |     |              |     |              |     |              |
| StellarRoute |     | Slippage     |     | Stream plan  |     | Drips Wave   |
| API -> Redis |     | thresholds   |     | Policy caps  |     | API / dry-run|
+--------------+     +--------------+     +--------------+     +--------------+
```

### 2.1 Collect signals

- **Entry:** `agents/collector.py` - `collect_signals(state)`
- **Input:** Watchlist pairs from `Settings.watchlist_pairs()`
- **Action:** For each pair, call StellarRoute `quote`, `routes`, `orderbook`
- **Output:** `RoutingSignal[]` cached in Redis with TTL (`HYDRA_SIGNAL_TTL_SECONDS`)

### 2.2 Predict bottlenecks

- **Entry:** `agents/predictor.py` - `predict(state)`
- **Input:** Recent signal history from Redis window
- **Heuristics (Phase 1):** Quote slippage vs baseline, route path count drops, orderbook depth
- **Output:** Ranked `BottleneckPrediction[]` with confidence, horizon_minutes

### 2.3 Decide drip actions

- **Entry:** `agents/strategist.py` - `decide(state)`
- **Actions:** `create_stream`, `adjust_rate`, `pause_stream`, `no_op`
- **Constraints:** Per-hour XLM cap, asset allowlist, dry-run mode

### 2.4 Execute

- **Entry:** `agents/executor.py` - `execute(state)`
- **Action:** Drips Wave API call (or dry-run log)
- **Audit:** All plans logged via `security/audit.py`

---

## 3. Key design decisions

| Decision | Rationale |
|----------|-----------|
| **HTTP-only coupling to StellarRoute** | No Rust workspace dependency; independent deploy lifecycle |
| **LangGraph with edgeless Command routing** | Flexible multi-agent loop without hard-coded edges |
| **Redis signal cache (not Postgres)** | Ephemeral signals; TTL-based expiry avoids schema migrations |
| **Celery worker for async cycles** | Decouples cycle execution from API server; retry support |
| **Default DRIPS_DRY_RUN=true** | Safety-first; live streams require explicit opt-in |

---

## 4. Non-goals (NG1-NG5)

These boundaries define what StellarHydra intentionally does **not** do.

| ID | Non-goal | Rationale | How to avoid scope creep |
|----|----------|-----------|--------------------------|
| NG1 | **Replace StellarRoute pathfinder or quote logic** | Rust engine stays authoritative for all quote and path computation | Submit routing changes to StellarRoute, not Hydra |
| NG2 | **On-chain swap execution** | Hydra funds paths; execution stays with StellarRoute + Soroban router | Keep Drips integration read- and stream-only |
| NG3 | **Full sentiment/NLP pipeline in v0** | Stub hooks only until labelled data exists | Use sentiment stub; no external NLP deps in Phase 0-1 |
| NG4 | **Autonomous mainnet fund movement without guardrails** | HITL or policy caps must gate real fund movements | Do not remove dry-run defaults or bypass policy caps |
| NG5 | **Indexer duplication** | All reads go through StellarRoute API or shared Postgres replica | No direct Stellar RPC, Soroban subscriptions, or independent scraping |

Non-goal violations are architectural and caught in code review.
Phase-gated exceptions are tracked in [ROADMAP.md](ROADMAP.md).

---

## 5. References

- [PRD.md](PRD.md) - Product requirements, goals, target users
- [Architecture overview](architecture/overview.md) - Component map, runtime processes, source layout
- [LangGraph workflow](architecture/langgraph-workflow.md) - Node-level details for the Hydra state graph
- [StellarRoute](https://github.com/StellarRoute/StellarRoute) - Authoritative router (companion system)
- [Drips Wave](https://drips.network/) - Programmable cash flow protocol
- [ROADMAP.md](ROADMAP.md) - Phase gates and exit criteria

---

## 6. Reviewer checklist

### Content correctness
- [ ] StellarRoute links point to StellarRoute/StellarRoute
- [ ] Non-goals match definitions in PRD section 3
- [ ] Data flow order: collect -> predict -> decide -> execute
- [ ] Config variable names match .env.example and config.py
- [ ] API paths match the StellarRoute contract in PRD section 4

### Boundary clarity
- [ ] No language implying Hydra replaces StellarRoute (NG1)
- [ ] No suggestions of on-chain execution (NG2)
- [ ] No production NLP pipeline assumptions (NG3)
- [ ] DRIPS_DRY_RUN=true presented as default safety posture (NG4)
- [ ] All data sourcing described as StellarRoute API-driven (NG5)

### Readability
- [ ] Tables used for structured information
- [ ] Terminology consistent with PRD glossary
- [ ] Cross-references use relative paths within docs/
