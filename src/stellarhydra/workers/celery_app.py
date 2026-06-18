# Celery application factory for async Hydra cycle execution.
from __future__ import annotations

from celery import Celery

from stellarhydra.config import get_settings

settings = get_settings()

celery_app = Celery(
    "stellarhydra",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["stellarhydra.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)
