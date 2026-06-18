# Prometheus metrics for Hydra cycle and API observability.
from __future__ import annotations

from prometheus_client import Counter, Histogram

CYCLE_TOTAL = Counter(
    "hydra_cycles_total",
    "Total Hydra LangGraph cycles executed",
    ["status"],
)

CYCLE_DURATION = Histogram(
    "hydra_cycle_duration_seconds",
    "Hydra cycle wall time",
    buckets=(0.5, 1, 2, 5, 10, 30, 60),
)

DRIP_ACTIONS = Counter(
    "hydra_drip_actions_total",
    "Drip actions by type",
    ["action", "dry_run"],
)

HTTP_REQUESTS = Counter(
    "hydra_http_requests_total",
    "HTTP requests to Hydra API",
    ["method", "path", "status"],
)
