# Drips Wave client

Implementation: `src/stellarhydra/integrations/drips_client.py`

## Purpose

Submit drip stream create/adjust/pause requests to the Drips Wave API, or simulate them when dry-run is enabled.

## Configuration

| Variable | Purpose |
|----------|---------|
| `DRIPS_API_URL` | API base (default `https://api.drips.network`) |
| `DRIPS_API_KEY` | Bearer token when live |
| `DRIPS_DRY_RUN` | When `true`, skip HTTP and log intended payload |

## Dry-run default

`DRIPS_DRY_RUN=true` is the safe default in `.env.example`. The executor returns success with status `dry_run` and writes an audit log entry via `security/audit.py`.

## Live mode checklist

1. Confirm Drips Wave API contract (PRD open question OQ1).
2. Set `DRIPS_API_KEY` from sandbox or production credentials.
3. Set `DRIPS_DRY_RUN=false`.
4. Enable HITL approval stub before mainnet funds (Phase 3).

## Testing

`tests/test_drips_client.py` covers dry-run paths and HTTP error handling with mocks.
