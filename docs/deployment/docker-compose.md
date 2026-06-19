# Docker Compose

File: `docker-compose.yml` at repo root.

## Services

| Service | Image / build | Purpose |
|---------|---------------|---------|
| `redis` | Redis 7 | Signal cache, Celery broker/backends |
| `api` | Dockerfile | FastAPI admin service |
| `worker` | Dockerfile | Celery worker |

## Quick start

```bash
docker-compose up -d redis    # minimum for local dev
docker-compose up -d          # full stack
```

## Ports

- Redis: `6379` (host mapped)
- API: `8090` (when full stack running)

## Environment

Compose loads `.env` for StellarRoute URL, Drips settings, and admin key. Mount or copy `.env` before starting API/worker containers.

## Dockerfile

Single `Dockerfile` builds the Python package with `pip install -e .`. Production hardening (non-root user, multi-stage) is tracked for Phase 3.

See also [deploy/render.md](../deploy/render.md) for hosted deployment.
