# Audit log helper for drip action plans and admin operations.
from __future__ import annotations

import structlog

from stellarhydra.models.predictions import DripActionPlan

audit_logger = structlog.get_logger("hydra.audit")


def log_drip_action(plan: DripActionPlan, execution_status: str) -> None:
    audit_logger.info(
        "drip_action",
        action=plan.action.value,
        pair=plan.pair,
        amount_xlm=plan.stream_amount_xlm,
        dry_run=plan.dry_run,
        policy_ok=plan.policy_ok,
        rationale=plan.rationale,
        execution_status=execution_status,
    )
