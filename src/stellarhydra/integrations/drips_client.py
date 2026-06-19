# HTTP client for Drips Wave API with dry-run mode for safe development.
from __future__ import annotations

import logging
import uuid
from typing import Any

import httpx

from stellarhydra.config import Settings, get_settings
from stellarhydra.models.predictions import DripActionPlan, DripActionType

logger = logging.getLogger(__name__)


class DripsError(Exception):
    """Raised when Drips Wave API call fails."""


class DripsClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def execute_plan(self, plan: DripActionPlan) -> dict[str, Any]:
        if plan.action == DripActionType.NO_OP:
            return {"status": "skipped", "reason": "no_op", "dry_run": plan.dry_run}

        payload = {
            "action": plan.action.value,
            "pair": plan.pair,
            "amount_xlm": plan.stream_amount_xlm,
            "target_path": plan.target_path,
            "rationale": plan.rationale,
        }

        if self._settings.drips_dry_run or plan.dry_run:
            logger.info("DRIPS dry-run payload: %s", payload)
            return {
                "status": "dry_run",
                "request_id": str(uuid.uuid4()),
                "payload": payload,
            }

        if not self._settings.drips_api_key:
            raise DripsError("DRIPS_API_KEY required when DRIPS_DRY_RUN=false")

        headers = {
            "Authorization": f"Bearer {self._settings.drips_api_key}",
            "Content-Type": "application/json",
        }
        endpoint = {
            DripActionType.CREATE_STREAM: "/v1/streams/create",
            DripActionType.ADJUST_RATE: "/v1/streams/adjust",
            DripActionType.PAUSE_STREAM: "/v1/streams/pause",
        }.get(plan.action, "/v1/streams/adjust")
        url = f"{self._settings.drips_api_url.rstrip('/')}{endpoint}"

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                raise DripsError(f"Drips API error {response.status_code}: {response.text}")
            return response.json()
