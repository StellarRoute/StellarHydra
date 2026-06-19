# Production Dockerfile

The root `Dockerfile` builds a non-editable install suitable for API and worker containers.

## Build steps

1. Base image: `python:3.11-slim`
2. Copy `pyproject.toml`, `README.md`, and `src/`
3. Run `pip install .` (not `pip install -e .`)
4. Default CMD runs uvicorn on port 8090

## Compose service names

`docker-compose.yml` defines:

| Service | Command |
|---------|---------|
| `hydra-api` | `uvicorn stellarhydra.api.main:app --host 0.0.0.0 --port 8090` |
| `hydra-worker` | `celery -A stellarhydra.workers.celery_app worker --loglevel=info` |

Older deployment notes that reference services named `api` and `worker` should be updated to these names.

Workers reuse the same image; only the container command differs.
