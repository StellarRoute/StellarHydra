# Admin API authentication

Hydra admin routes require a static API key sent on every request.

## Header name

```
X-API-Key: <HYDRA_ADMIN_API_KEY>
```

FastAPI reads this via `APIKeyHeader(name="X-API-Key")` in `api/auth.py`.

Some older docs and README snippets reference `X-Admin-Api-Key`; that header is **not** checked by the server. Update clients and curl examples to use `X-API-Key`.

## Failure mode

Missing or mismatched keys return HTTP 401 with `"Invalid or missing API key"`.

The expected value comes from `HYDRA_ADMIN_API_KEY` (default `change-me-in-production`).

See `tests/test_api.py` for request examples.
