# Unit tests for Celery task behavior.
from unittest.mock import MagicMock, patch

from stellarhydra.workers.celery_app import celery_app
from stellarhydra.workers.tasks import refresh_pair_watchlist, run_hydra_cycle


def test_celery_tasks_registered():
    assert "stellarhydra.run_hydra_cycle" in celery_app.tasks
    assert "stellarhydra.refresh_pair_watchlist" in celery_app.tasks
    assert run_hydra_cycle.name == "stellarhydra.run_hydra_cycle"
    assert refresh_pair_watchlist.name == "stellarhydra.refresh_pair_watchlist"


def test_run_hydra_cycle_returns_cycle_payload():
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {"cycle_id": "abc", "execution_status": "success"}

    with patch("stellarhydra.workers.tasks.run_cycle", return_value=mock_result):
        payload = run_hydra_cycle.run()

    assert payload["cycle_id"] == "abc"
    assert payload["execution_status"] == "success"


def test_refresh_pair_watchlist_persists_to_redis():
    with patch(
        "stellarhydra.integrations.stellarroute_client.StellarRouteClient.fetch_pairs",
        return_value=[{"base": "native", "quote": "USDC"}],
    ), patch("stellarhydra.integrations.signal_cache.SignalCache") as mock_cache_cls:
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        result = refresh_pair_watchlist.run()

    assert result["status"] == "refreshed"
    mock_cache.store_watchlist.assert_called_once_with(["native:USDC"])
