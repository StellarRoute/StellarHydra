# Unit tests for Redis signal cache helpers.
from unittest.mock import MagicMock

from stellarhydra.integrations.signal_cache import SignalCache


def test_store_and_get_watchlist():
    client = MagicMock()
    client.get.return_value = '["native:USDC","XLM:BTC"]'
    cache = SignalCache(client=client)

    cache.store_watchlist(["native:USDC", "XLM:BTC"])
    client.setex.assert_called_once()
    pairs = cache.get_watchlist()
    assert pairs == ["native:USDC", "XLM:BTC"]


def test_get_watchlist_returns_none_when_missing():
    client = MagicMock()
    client.get.return_value = None
    cache = SignalCache(client=client)
    assert cache.get_watchlist() is None
