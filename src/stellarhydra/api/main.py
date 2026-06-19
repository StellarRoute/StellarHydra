# FastAPI application — health, metrics, and authenticated admin cycle trigger.
from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel

from stellarhydra.api.auth import require_admin_api_key
from stellarhydra.api.middleware import RequestLoggingMiddleware
from stellarhydra.config import get_settings
from stellarhydra.graph.hydra_graph import run_cycle
from stellarhydra.integrations.signal_cache import SignalCache
from stellarhydra.integrations.stellarroute_client import StellarRouteClient
from stellarhydra.observability.logging_config import configure_logging
from stellarhydra.observability.metrics import CYCLE_DURATION, CYCLE_TOTAL, DRIP_ACTIONS
from stellarhydra.observability.tracing import setup_tracing
from stellarhydra.security.audit import log_drip_action
from stellarhydra.security.kill_switch import is_kill_switch_active
from stellarhydra.security.secrets import validate_runtime_secrets


class CycleTriggerRequest(BaseModel):
    thread_id: str | None = None
    async_mode: bool = False


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    setup_tracing()
    for warning in validate_runtime_secrets(get_settings()):
        import logging

        logging.getLogger(__name__).warning("Config: %s", warning)
    yield


app = FastAPI(
    title="StellarHydra",
    description="Agentic Liquidity Balancer for Stellar DEX routing",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(RequestLoggingMiddleware)


@app.get("/health")
def health_check() -> dict:
    settings = get_settings()
    stellarroute_ok = False
    redis_ok = False

    try:
        StellarRouteClient(settings).health_check()
        stellarroute_ok = True
    except Exception:  # noqa: BLE001
        stellarroute_ok = False

    try:
        redis_ok = SignalCache(settings).ping()
    except Exception:  # noqa: BLE001
        redis_ok = False

    kill_switch_active = False
    try:
        kill_switch_active = is_kill_switch_active(StellarRouteClient(settings))
    except Exception:  # noqa: BLE001
        kill_switch_active = False

    status = "ok" if redis_ok else "degraded"
    return {
        "status": status,
        "components": {
            "stellarroute": "ok" if stellarroute_ok else "unreachable",
            "redis": "ok" if redis_ok else "unreachable",
            "kill_switch": "active" if kill_switch_active else "off",
        },
    }


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/admin/cycle/{cycle_id}")
def get_cycle_result(cycle_id: str, _api_key: str = Depends(require_admin_api_key)) -> dict:
    settings = get_settings()
    raw = SignalCache(settings).get_cycle(cycle_id)
    if not raw:
        raise HTTPException(status_code=404, detail=f"Cycle {cycle_id} not found")
    import json

    return json.loads(raw)


@app.post("/admin/cycle/trigger")
def trigger_cycle(
    body: CycleTriggerRequest | None = None,
    _api_key: str = Depends(require_admin_api_key),
) -> dict:
    req = body or CycleTriggerRequest()
    if req.async_mode:
        from stellarhydra.workers.tasks import run_hydra_cycle

        task = run_hydra_cycle.delay(thread_id=req.thread_id)
        return {"status": "queued", "task_id": task.id, "thread_id": req.thread_id}

    start = time.perf_counter()
    try:
        result = run_cycle(thread_id=req.thread_id)
    except Exception as exc:  # noqa: BLE001
        CYCLE_TOTAL.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    duration = time.perf_counter() - start
    CYCLE_DURATION.observe(duration)
    CYCLE_TOTAL.labels(status=result.execution_status).inc()

    if result.action_plan:
        DRIP_ACTIONS.labels(
            action=result.action_plan.action.value,
            dry_run=str(result.action_plan.dry_run).lower(),
        ).inc()
        log_drip_action(result.action_plan, result.execution_status)

    return result.model_dump(mode="json")
