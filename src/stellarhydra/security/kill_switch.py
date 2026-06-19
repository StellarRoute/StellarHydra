# Kill switch guard when StellarRoute reports active trading halt.
from __future__ import annotations

from typing import Any

from stellarhydra.integrations.stellarroute_client import StellarRouteClient, StellarRouteError


def is_kill_switch_active(client: StellarRouteClient | None = None) -> bool:
    """Return True when StellarRoute dependency health indicates a kill switch."""
    from stellarhydra.config import get_settings

    sr_client = client or StellarRouteClient()
    settings = get_settings()
    try:
        deps = sr_client.fetch_health_deps()
    except (StellarRouteError, Exception):
        return settings.hydra_kill_switch_fail_closed

    kill = deps.get("kill_switch") or deps.get("killSwitch")
    if isinstance(kill, dict):
        return bool(kill.get("active") or kill.get("enabled"))
    if isinstance(kill, bool):
        return kill
    return bool(deps.get("kill_switch_active"))
