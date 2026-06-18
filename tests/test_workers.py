# Unit tests for Celery task registration.
from stellarhydra.workers.celery_app import celery_app
from stellarhydra.workers.tasks import refresh_pair_watchlist, run_hydra_cycle


def test_celery_tasks_registered():
    assert "stellarhydra.run_hydra_cycle" in celery_app.tasks
    assert "stellarhydra.refresh_pair_watchlist" in celery_app.tasks
    assert run_hydra_cycle.name == "stellarhydra.run_hydra_cycle"
    assert refresh_pair_watchlist.name == "stellarhydra.refresh_pair_watchlist"
