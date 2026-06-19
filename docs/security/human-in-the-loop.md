# Human-in-the-loop approval (stub)

Phase 3 mainnet gating will require operator approval for large drip plans. The stub lives in `graph/hitl.py` and is not wired into the LangGraph cycle yet.

## Threshold check

```python
hitl_review_required(plan_amount_xlm, threshold_xlm=500.0) -> bool
```

Returns true when the planned XLM amount is at or above the threshold (default 500 XLM).

## Interrupt payload

`hitl_interrupt_payload(plan)` returns a dict suitable for future `interrupt()` integration:

- `type`: `"drip_approval_required"`
- `plan`: serialized drip plan
- `message`: operator-facing prompt

Integrators should call these helpers from the `execute` node once mainnet execution is enabled.
