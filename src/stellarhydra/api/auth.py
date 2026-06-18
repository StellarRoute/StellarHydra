# API key authentication for Hydra admin endpoints.
from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from stellarhydra.config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_admin_api_key(api_key: str | None = Security(_api_key_header)) -> str:
    expected = get_settings().hydra_admin_api_key
    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key
