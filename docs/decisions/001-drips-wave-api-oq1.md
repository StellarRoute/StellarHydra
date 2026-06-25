# ADR 001: Drips Wave API OQ1 tracker

| Field | Value |
|-------|-------|
| Status | Open |
| Owner | StellarHydra maintainers |
| External dependency | Drips Wave maintainers |
| Last reviewed | 2026-06-26 |
| Related PRD question | `docs/PRD.md` Section 6, OQ1 |

## Context

PRD OQ1 asks which Drips Wave endpoints and authentication model are canonical for Stellar stream CRUD. The answer blocks live F4 execution because `DripsClient` currently has only provisional stream endpoints and a dry-run-safe execution path.

The maintainer participation workflow in the Drips docs says maintainers join a Wave Program, install/sync the Drips Wave GitHub App for their organization, add issues to a program, and assign complexity/point values through the Drips app or Wave labels. That flow is issue and reward oriented; it does not yet document a stable public stream CRUD API for StellarHydra to call directly.

## Current DripsClient behavior

`src/stellarhydra/integrations/drips_client.py` currently:

- Builds a payload from `DripActionPlan` with `action`, `pair`, `amount_xlm`, `target_path`, and `rationale`.
- Returns a dry-run payload when either `Settings.drips_dry_run` or `plan.dry_run` is true.
- Requires `DRIPS_API_KEY` before any live request when `DRIPS_DRY_RUN=false`.
- Uses `DRIPS_API_URL` from settings, defaulting to `https://api.drips.network`.
- Maps actions to provisional endpoints:
  - `CREATE_STREAM` -> `/v1/streams/create`
  - `ADJUST_RATE` -> `/v1/streams/adjust`
  - `PAUSE_STREAM` -> `/v1/streams/pause`

## Known gaps

- No confirmed Wave sandbox base URL for Stellar stream CRUD.
- No confirmed auth scheme for live stream writes: GitHub OAuth session, Wave API key, GitHub App installation token, or a separate partner token.
- No confirmed request/response schemas for create, adjust, and pause stream actions.
- No confirmed idempotency mechanism for retry-safe executor calls.
- No confirmed rate limits, error taxonomy, or webhook callback contract for completed Wave actions.
- No confirmed mapping from StellarHydra's `pair` / `target_path` fields to Drips Wave program, issue, or stream identifiers.

## Working hypotheses

| Hypothesis | Confidence | Verification |
|------------|------------|--------------|
| Live writes should stay behind `DRIPS_DRY_RUN=false` until Drips confirms a write API. | High | Keep default dry-run true and require explicit credentials. |
| Wave issue complexity and points are managed through the Drips app or Wave labels, not the stream CRUD endpoints. | Medium | Verify with Drips maintainer workflow and maintainer FAQ. |
| API clients will need a program or repository identifier in addition to the stream action payload. | Medium | Ask Drips maintainers for sandbox schema. |
| Idempotency should use a StellarHydra-generated request id or cycle id. | Medium | Confirm whether Drips accepts an idempotency header or body field. |

## Candidate sandbox and docs URLs

| Purpose | URL | Status |
|---------|-----|--------|
| Drips Wave app | `https://drips.network/wave` | Confirmed product surface |
| Maintainer participation docs | `https://docs.drips.network/wave/maintainers/participating-in-a-wave/` | Confirmed workflow reference |
| Maintainer FAQ | `https://docs.drips.network/wave/maintainers/faq/` | Confirmed issue/complexity reference |
| Current configured API base | `https://api.drips.network` | Configured default; stream CRUD contract unverified |
| Stellar stream sandbox | TBD | Needs Drips maintainer confirmation |

## Verification steps

1. Ask Drips maintainers whether a public or partner sandbox exists for Stellar stream CRUD.
2. Confirm the auth model for live writes and whether `DRIPS_API_KEY` is the right credential abstraction.
3. Request canonical endpoint paths, request bodies, response bodies, and error codes for create, adjust, and pause stream actions.
4. Confirm idempotency expectations for retries from a Celery worker.
5. Confirm how Wave program, repo, issue, point value, and contributor identity map to any stream identifier.
6. Update `DripsClient` endpoint mapping and tests only after the contract is confirmed.
7. Keep Phase 2 live execution blocked until this ADR is updated to `Accepted` or superseded.

## Decision status

No production endpoint decision is accepted yet. StellarHydra should continue to use dry-run payload logging for F4 until OQ1 is resolved.
