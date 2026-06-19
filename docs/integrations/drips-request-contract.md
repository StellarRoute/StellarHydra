# Drips HTTP request contract

`DripsClient.execute_plan()` posts drip adjustments to the Drips Wave API.

## Endpoint

`POST {DRIPS_API_URL}/v1/streams/adjust`

## Authentication

`Authorization: Bearer {DRIPS_API_KEY}` when the key is set.

## JSON body

| Field | Source |
|-------|--------|
| `action` | Plan action enum value |
| `pair` | Target pair string |
| `amount_xlm` | `stream_amount_xlm` |
| `target_path` | List of hop strings |
| `rationale` | Human-readable reason |

## Dry run and NO_OP

When `DRIPS_DRY_RUN` is true, the client returns a local JSON response without network I/O.

`NO_OP` plans return `{ "status": "skipped", "reason": ... }` without calling the API.

See `src/stellarhydra/integrations/drips_client.py` and `tests/test_drips_client.py`.
