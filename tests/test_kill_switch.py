# Unit tests for StellarRoute kill switch guard.
from unittest.mock import MagicMock

from stellarhydra.security.kill_switch import is_kill_switch_active


def test_kill_switch_active_from_nested_payload():
    client = MagicMock()
    client.fetch_health_deps.return_value = {"kill_switch": {"active": True}}
    assert is_kill_switch_active(client) is True


def test_kill_switch_inactive_when_missing():
    client = MagicMock()
    client.fetch_health_deps.return_value = {"database": "ok"}
    assert is_kill_switch_active(client) is False
