# Agents

StellarHydra splits decision logic across three agents under `src/stellarhydra/agents/`.

## Predictor (`predictor.py`)

**Input:** list of `RoutingSignal` from StellarRoute (quote depth, slippage, health flags).

**Output:** list of `BottleneckPrediction` for pairs exceeding `HYDRA_SLIPPAGE_ALERT_BPS` within `HYDRA_PREDICTION_HORIZON_MINUTES`.

The predictor uses heuristics over signal freshness and slippage; it does not call external ML services in v0.

## Strategist (`strategist.py`)

**Input:** bottleneck predictions and policy settings (`HYDRA_MAX_DRIP_XLM_PER_HOUR`, watchlist).

**Output:** `DripActionPlan` with action type (`CREATE`, `ADJUST`, `PAUSE`, `NO_OP`), target pair, amount, and `policy_ok` flag.

Policy caps reject plans that would exceed hourly XLM drip limits.

## Executor (`executor.py`)

**Input:** approved `DripActionPlan`.

**Output:** execution status string and optional Drips API response metadata.

When `DRIPS_DRY_RUN=true`, the executor logs the payload and returns success without calling Drips.

## Sentiment stub (`sentiment.py`)

Placeholder hooks for future sentiment/NLP inputs (PRD non-goal NG3 for v0). Not wired into the main graph yet.
