# Human-in-the-loop interrupt stub for regulated mainnet drip changes (Phase 3).
from __future__ import annotations

from typing import Any


def hitl_review_required(
    plan_amount_xlm: float,
    threshold_xlm: float | None = None,
    yaml_threshold: float | None = None,
) -> bool:
    """Return True when human approval should gate execution."""
    limit = threshold_xlm
    if limit is None:
        limit = yaml_threshold if yaml_threshold is not None else 500.0
    return plan_amount_xlm >= limit


def hitl_interrupt_payload(plan: dict[str, Any]) -> dict[str, Any]:
    """Payload shape for future LangGraph interrupt() integration."""
    return {
        "type": "drip_approval_required",
        "plan": plan,
        "message": "Review drip plan before mainnet execution",
    }
