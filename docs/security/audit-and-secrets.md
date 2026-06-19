# Audit and secrets

## Secret validation

`src/stellarhydra/security/secrets.py` runs `validate_runtime_secrets()` at API startup. Warnings include:

- Default `HYDRA_ADMIN_API_KEY` in non-dev environments
- `DRIPS_DRY_RUN=false` without `DRIPS_API_KEY`

Warnings log but do not block startup in v0.

## Admin API key

Protects `POST /admin/cycle/trigger`. Send as header:

```
X-Admin-Api-Key: <value of HYDRA_ADMIN_API_KEY>
```

Rotate the key in production and restrict network access to the admin port.

## Drips credentials

Store `DRIPS_API_KEY` only in environment or secret manager. Never commit `.env`.

## Audit logging

`src/stellarhydra/security/audit.py` records drip action plans and execution status when cycles run through the admin API. Format is structured logs suitable for log aggregation.

## Production checklist

- [ ] Change default admin API key
- [ ] Keep `DRIPS_DRY_RUN=true` until Drips contract verified
- [ ] Enable TLS termination in front of FastAPI
- [ ] Restrict Redis and Celery broker to private network
- [ ] Enable HITL before live fund movement (Phase 3)
