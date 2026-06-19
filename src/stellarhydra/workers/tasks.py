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
    """Refresh watchlist from StellarRoute /api/v1/pairs when available."""
    from stellarhydra.config import get_settings
    from stellarhydra.integrations.stellarroute_client import StellarRouteClient, StellarRouteError

    settings = get_settings()
    fallback = [f"{b}:{q}" for b, q in settings.watchlist_pairs()]

    try:
        client = StellarRouteClient(settings)
        pairs_data = client.fetch_pairs()
        refreshed: list[str] = []
        for item in pairs_data[:20]:
            base = str(item.get("base") or item.get("base_asset") or "")
            quote = str(item.get("quote") or item.get("quote_asset") or "")
            if base and quote:
                refreshed.append(f"{base}:{quote}")
        if refreshed:
            from stellarhydra.integrations.signal_cache import SignalCache

            SignalCache(settings).store_watchlist(refreshed)
            return {"pairs": refreshed, "status": "refreshed", "source": "stellarroute"}
    except (StellarRouteError, Exception) as exc:  # noqa: BLE001
        logger.warning("Watchlist refresh failed, using configured pairs: %s", exc)

    return {"pairs": fallback, "status": "ok", "source": "config"}
