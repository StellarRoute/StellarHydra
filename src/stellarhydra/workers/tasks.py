# Celery tasks for periodic Hydra liquidity balancing cycles.
from __future__ import annotations

import logging

from stellarhydra.graph.hydra_graph import run_cycle
from stellarhydra.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="stellarhydra.run_hydra_cycle", bind=True, max_retries=2)
def run_hydra_cycle(self, thread_id: str | None = None) -> dict:
    """Run one LangGraph cycle asynchronously."""
    try:
        result = run_cycle(thread_id=thread_id)
        return result.model_dump(mode="json")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Hydra cycle task failed")
        raise self.retry(exc=exc, countdown=30) from exc


@celery_app.task(name="stellarhydra.refresh_pair_watchlist")
def refresh_pair_watchlist() -> dict:
    """Placeholder for watchlist refresh from StellarRoute /api/v1/pairs."""
    from stellarhydra.config import get_settings

    pairs = get_settings().watchlist_pairs()
    return {"pairs": [f"{b}:{q}" for b, q in pairs], "status": "ok"}
