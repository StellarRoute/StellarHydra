# Drip execution agent — invokes Drips client and records audit metadata.
from __future__ import annotations

import logging
from typing import Any

from stellarhydra.integrations.drips_client import DripsClient, DripsError
from stellarhydra.models.predictions import DripActionPlan

logger = logging.getLogger(__name__)


def execute_drip_plan(plan: DripActionPlan, client: DripsClient | None = None) -> dict[str, Any]:
    drips = client or DripsClient()
    try:
        result = drips.execute_plan(plan)
        logger.info(
            "Drip execution complete action=%s pair=%s status=%s",
            plan.action.value,
            plan.pair,
            result.get("status"),
        )
        return result
    except DripsError as exc:
        logger.error("Drip execution failed: %s", exc)
        return {"status": "error", "message": str(exc)}
