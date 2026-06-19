# Strategist decision rules

`decide_drip_action()` maps the highest-confidence `BottleneckPrediction` to a `DripActionPlan`.

## No-action paths

- Empty predictions → `NO_OP`, pair `"none"`.
- Pair assets outside `allowed_assets()` → `NO_OP`, `policy_ok=False`.
- **LOW** severity with confidence `< 0.5` → `NO_OP` (below action threshold).

## Drip amount tiers

| Severity | Default XLM amount |
|----------|-------------------|
| LOW (actionable) | 50 |
| MEDIUM | 150 |
| HIGH | 300 |

Amount is capped at `hydra_max_drip_xlm_per_hour`. If the tier exceeds the cap, amount is reduced to the cap and `policy_ok` may be false.

## Action type selection

- `confidence >= 0.7` → `ADJUST_RATE`
- Otherwise → `CREATE_STREAM`

`dry_run` mirrors `DRIPS_DRY_RUN` / settings. The graph `decide` node skips execution when `policy_ok` is false.

See `src/stellarhydra/agents/strategist.py` and `tests/test_strategist.py`.
