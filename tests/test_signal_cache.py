# Unit tests for Redis signal cache history and cycle persistence.
from unittest.mock import MagicMock

from stellarhydra.integrations.signal_cache import SignalCache
from stellarhydra.models.signals import RoutingSignal


def _signal(pair: str = "native:USDC") -> RoutingSignal:
    base, quote = pair.split(":")
    return RoutingSignal(base=base, quote=quote, amount="100", slippage_bps=50)


def test_store_appends_to_history_list():
    client = MagicMock()
    cache = SignalCache(client=client)
    signal = _signal()

    cache.store(signal)

    assert client.setex.called
    client.lpush.assert_called_once()
    client.ltrim.assert_called_once()
    client.expire.assert_called_once()


def test_get_history_parses_signals():
    client = MagicMock()
    signal = _signal()
    client.lrange.return_value = [signal.model_dump_json()]
    cache = SignalCache(client=client)

    history = cache.get_history("native:USDC", limit=3)

    assert len(history) == 1
    assert history[0].pair_key() == "native:USDC"


def test_store_and_get_cycle():
    client = MagicMock()
    cache = SignalCache(client=client)

    cache.store_cycle("cycle-1", '{"status":"ok"}', ttl_seconds=60)
    client.setex.assert_called_with("hydra:cycle:cycle-1", 60, '{"status":"ok"}')

    client.get.return_value = '{"status":"ok"}'
    assert cache.get_cycle("cycle-1") == '{"status":"ok"}'
