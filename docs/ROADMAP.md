# StellarHydra Roadmap

Derived from [PRD.md](./PRD.md). Phases are sequential; exit criteria must pass before advancing.

---

## Phase 0: Scaffold

| Item | Detail |
|------|--------|
| **Objective** | Repository structure, dependency declarations, local dev wiring, CI skeleton |
| **Deliverables** | `pyproject.toml`, `requirements.txt`, `.env.example`, `docker-compose.yml`, package layout under `src/stellarhydra/`, GitHub Actions CI, README |
| **Exit criteria** | `pip install -e .` succeeds; `ruff`/`pytest` CI job runs (may skip integration tests); imports resolve |
| **Complexity** | Low |

---

## Phase 1: Core Loop (minimal E2E proof)

| Item | Detail |
|------|--------|
| **Objective** | Prove predict → decide → drip stub in one LangGraph cycle |
| **Deliverables** | `hydra_graph.py`, signal models, StellarRoute HTTP client, Drips dry-run client, `scripts/run_cycle.py`, unit tests for graph |
| **Exit criteria** | Dry-run cycle completes with `DripActionPlan` emitted; tests pass without live API keys |
| **Complexity** | Medium |

---

## Phase 2: Feature Complete

| Item | Detail |
|------|--------|
| **Objective** | Remaining PRD features, edge cases, error states |
| **Deliverables** | Celery tasks, Redis signal cache, multi-pair watchlist, policy caps, sentiment stub hook, retry/backoff on StellarRoute errors, expanded test suite |
| **Exit criteria** | Worker task runs cycle; Redis caches signals with TTL; failed StellarRoute call degrades gracefully; policy blocks over-cap drip |
| **Complexity** | High |

Phase 2 live Drips execution depends on OQ1. Track endpoint, auth, sandbox, and verification notes in [ADR 001](./decisions/001-drips-wave-api-oq1.md).

---

## Phase 3: Production Hardening

| Item | Detail |
|------|--------|
| **Objective** | Auth, security, observability, performance hooks, deploy pipeline skeleton |
| **Deliverables** | FastAPI admin API with API key auth, Prometheus metrics, OpenTelemetry hooks, Dockerfile, Render deploy notes, audit logging, HITL interrupt stub |
| **Exit criteria** | `/health` and `/metrics` live; unauthenticated admin blocked; deploy docs complete; CI builds Docker image |
| **Complexity** | Medium |

---

## Summary Timeline

| Phase | Focus | Complexity | Depends on | Target (relative) |
|-------|-------|------------|------------|-------------------|
| 0 | Scaffold | Low | — | Week 1 |
| 1 | Core loop E2E | Medium | Phase 0 | Week 2-3 |
| 2 | Feature complete | High | Phase 1, OQ1 ([Drips Wave API ADR](decisions/001-drips-wave-api-oq1.md)) | Week 4-7 |
| 3 | Production hardening | Medium | Phase 2, StellarRoute Phase A | Week 8-10 |

---

## Milestone mapping to StellarRoute

| StellarRoute milestone | StellarHydra alignment |
|------------------------|------------------------|
| Phase A: hosted API + quotes | Hydra reads production API; dry-run only |
| Phase A stable | Enable sandbox Drips streams |
| Phase B: on-chain swaps | Hydra validates paths against router contract (OQ5) |
| Post-audit mainnet swaps | HITL + cap policy for live drips (OQ4) |

---

## Risk register

| Risk | Mitigation | Phase |
|------|------------|-------|
| Drips API undocumented | Dry-run client + [OQ1 ADR tracker](decisions/001-drips-wave-api-oq1.md) | 1-2 |
| StellarRoute API rate limits | Redis cache, backoff, watchlist size cap | 2 |
| Autonomous fund movement | Default dry-run, policy caps, HITL stub | 1-3 |
| LangGraph checkpoint storage | MemorySaver dev; PostgresSaver documented for prod | 3 |
