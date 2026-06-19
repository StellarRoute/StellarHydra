# Metrics and logging

## Structured logging

Configured in `src/stellarhydra/observability/logging_config.py` at API startup.

Set level with `HYDRA_LOG_LEVEL` (default `INFO`).

## Prometheus metrics

Defined in `src/stellarhydra/observability/metrics.py`:

| Metric | Labels | Description |
|--------|--------|-------------|
| `hydra_cycle_total` | `status` | Cycle completions (success, error, dry_run, etc.) |
| `hydra_cycle_duration_seconds` | none | Histogram of cycle wall time |
| `hydra_drip_actions_total` | `action`, `dry_run` | Drip plans executed or simulated |

Scrape `GET /metrics` on the admin API port.

## OpenTelemetry

Optional tracing via `src/stellarhydra/observability/tracing.py`.

| Variable | Purpose |
|----------|---------|
| `HYDRA_ENABLE_OTEL` | Master switch |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Collector URL |

Disabled by default in local dev.

## Audit trail

Drip actions log through `src/stellarhydra/security/audit.py` when triggered via the admin API.
