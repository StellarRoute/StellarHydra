# Prometheus metrics reference

Metrics register on import of `observability/metrics.py` and expose at `/metrics` on the API.

## Defined metrics

| Name | Type | Labels | Incremented where |
|------|------|--------|-------------------|
| `hydra_cycles_total` | Counter | `status` | After each `run_cycle` completes |
| `hydra_cycle_duration_seconds` | Histogram | (none) | Cycle wall time |
| `hydra_drip_actions_total` | Counter | `action`, `dry_run` | After Drips execution attempt |
| `hydra_http_requests_total` | Counter | `method`, `path`, `status` | Request middleware |

Note the plural `hydra_cycles_total` (some older docs used `hydra_cycle_total`).

## Gaps

If middleware does not yet increment `hydra_http_requests_total`, the counter will remain zero until wired. Check `api/middleware.py` for the latest instrumentation.

See `src/stellarhydra/observability/metrics.py` and `api/main.py`.
