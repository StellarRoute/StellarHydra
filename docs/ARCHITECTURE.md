# StellarHydra Architecture & Contributor Guardrails

StellarHydra is an **Agentic Liquidity Balancer (ALB)** designed as a companion overlay to [StellarRoute](https://github.com/StellarRoute/StellarRoute). It proactively monitors DEX routing conditions and dynamically orchestrates [Drips Wave](https://drips.network/) continuous cash flow streams to keep cross-asset paths well-funded before orderbook imbalances cause elevated trader slippage.

---

## 1. System Role & Authoritative Router Boundary

StellarHydra is **not** a router and does not execute swaps. It operates strictly as a predictive liquidity overlay.

| Dimension | [StellarRoute](https://github.com/StellarRoute/StellarRoute) (Authoritative) | StellarHydra (Predictive ALB Overlay) |
|---|---|---|
| **Role** | Authoritative routing, quote calculation, and execution | Bottleneck prediction and proactive liquidity provisioning |
| **Engine** | High-performance Rust pathfinder & on-chain indexer | Python multi-agent system (LangGraph, FastAPI, Celery) |
| **Data Authority** | Source of truth for `/api/v1/quote`, `/api/v1/routes`, orderbooks | Consumes StellarRoute API via HTTP / WebSocket signals |
| **Funds** | Direct transaction path construction for user swaps | Programmable Drips streaming channels to pre-fund pools |

For complete requirements and roadmap definitions, refer to [docs/PRD.md](PRD.md).

---

## 2. ALB Overlay Model & Data Flow

StellarHydra executes a multi-agent cyclical loop powered by LangGraph:

```
                      ┌─────────────────────────────────────────┐
                      │            StellarRoute API             │
                      │   /quotes · /routes · /orderbooks       │
                      └────────────────────┬────────────────────┘
                                           │ HTTP signals
                                           ▼
┌──────────────┐     collect_signals  ┌─────────────────────────┐     predict     ┌──────────────┐
│    Redis     │◄─────────────────────│        LangGraph        │────────────────►│  Predictor   │
│ signal cache │                      │       multi-agent       │                 │    agent     │
│  + Celery    │                      │          loop           │                 └──────┬───────┘
└──────┬───────┘                      └────────────┬────────────┘                        │
       │                                           │ decide                              │
       │                                           ▼                                     │
       │                                    ┌──────────────┐                             │
       │                                    │  Strategist  │◄────────────────────────────┘
       │                                    │    agent     │
       │                                    └──────┬───────┘
       │                                           │ execute
       │                                           ▼
       │                                    ┌──────────────┐
       └───────────────────────────────────►│   Executor   │────────► Drips Wave API
                                            │  (+ audit)   │          (or dry-run log)
                                            └──────────────┘
```

1. **Signal Ingestion**: Periodically polls or streams market data from StellarRoute endpoints (`/api/v1/pairs`, `/api/v1/quote`, `/api/v1/orderbook`, and `/health/deps`).
2. **Bottleneck Prediction**: Evaluates historical signal buffers to flag routes experiencing slippage spikes or reserve depletion.
3. **Strategy Synthesis**: Strategist maps predicted bottlenecks to actionable Drips streaming actions (`create_stream`, `adjust_rate`, `pause_stream`, `no_op`).
4. **Guarded Execution**: Actions are audited against hard safety policy caps before dispatching to Drips Wave or logging in dry-run mode.

For deep-dive workflow specifications and state graphs, see [docs/architecture/overview.md](architecture/overview.md) and [docs/architecture/langgraph-workflow.md](architecture/langgraph-workflow.md).

---

## 3. Explicit Non-Goals (NG1–NG5)

Contributors proposing changes to router, predictor, or indexer modules must adhere strictly to these non-goals:

| Non-Goal | Description | Technical Rationale |
|---|---|---|
| **NG1** | **Replace StellarRoute pathfinder or quote logic** | Single responsibility: the high-throughput Rust engine in [StellarRoute](https://github.com/StellarRoute/StellarRoute) remains the sole authoritative source of truth for routing. |
| **NG2** | **On-chain swap execution (Phase B StellarRoute scope)** | The ALB pre-positions and funds liquidity paths; swap execution remains solely within StellarRoute and Soroban router contracts. |
| **NG3** | **Full sentiment/NLP pipeline in v0** | Maintain system reliability; keep lightweight stub hooks only until verified, labeled DEX sentiment datasets exist. |
| **NG4** | **Autonomous mainnet fund movement without guardrails** | Capital preservation: human-in-the-loop (HITL) authorization and strict programmatic policy caps are mandatory before any live mainnet capital dispatch. |
| **NG5** | **Indexer duplication** | Eliminate redundant ledger parsing: all normalized liquidity state reads must go through StellarRoute APIs or a shared database read replica. |

---

## 4. Reviewer & Contributor Checklist

When opening or reviewing pull requests in StellarHydra, verify each item:

- [ ] **Router Boundary**: Does the PR avoid duplicating or altering route finding and quote math, delegating entirely to [StellarRoute](https://github.com/StellarRoute/StellarRoute)?
- [ ] **Non-Goal Conformance**: Are all five non-goals (NG1–NG5) respected?
- [ ] **Policy Caps**: Are all Drips stream manipulations bound by hard rate limits and allowed-asset validation?
- [ ] **Dry-Run Safety**: Can new features execute cleanly under dry-run mode without issuing mutating external API calls?
- [ ] **State Determinism**: Does state modification follow the LangGraph reducer patterns defined in [docs/architecture/state-reducers.md](architecture/state-reducers.md)?

---

## 5. References

- [PRD.md](PRD.md): Product requirements document and Phase 0 roadmap.
- [docs/architecture/overview.md](architecture/overview.md): System architecture and agent component overview.
- [docs/architecture/langgraph-workflow.md](architecture/langgraph-workflow.md): LangGraph workflow topology and checkpointing model.
- [docs/architecture/hydra_graph_planned.mmd](architecture/hydra_graph_planned.mmd): Graph topology diagram.
