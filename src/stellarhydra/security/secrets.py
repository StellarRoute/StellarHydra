# Secret and credential validation helpers.
from __future__ import annotations

from stellarhydra.config import Settings


def validate_runtime_secrets(settings: Settings) -> list[str]:
    """Return list of configuration warnings (non-fatal)."""
    warnings: list[str] = []
    if settings.hydra_admin_api_key == "change-me-in-production":
        warnings.append("HYDRA_ADMIN_API_KEY is default; change before production")
    if not settings.drips_dry_run and not settings.drips_api_key:
        warnings.append("DRIPS_DRY_RUN=false but DRIPS_API_KEY is empty")
    return warnings
