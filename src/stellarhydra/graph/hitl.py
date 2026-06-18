# Human-in-the-loop interrupt stub for regulated mainnet drip changes (Phase 3).
from __future__ import annotations

from typing import Any


def hitl_review_required(plan_amount_xlm: float, threshold_xlm: float = 500.0) -> bool:
    """Return True when human approval should gate execution."""
    return plan_amount_xlm >= threshold_xlm


def hitl_interrupt_payload(plan: dict[str, Any]) -> dict[str, Any]:
    """Payload shape for future LangGraph interrupt() integration."""
    return {
        "type": "drip_approval_required",
        "plan": plan,
        "message": "Review drip plan before mainnet execution",
    }
