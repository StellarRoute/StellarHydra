# Unit tests for StellarRoute HTTP client response parsing.
from stellarhydra.integrations.stellarroute_client import (
    StellarRouteClient,
    _parse_path,
    _unwrap_envelope,
)


def test_unwrap_envelope():
    payload = {"v": 1, "data": {"price": "1.5"}}
    assert _unwrap_envelope(payload)["price"] == "1.5"


def test_parse_path_dict_steps():
    raw = [{"venue_type": "sdex", "selling_asset": "native", "buying_asset": "USDC"}]
    steps = _parse_path(raw)
    assert len(steps) == 1
    assert steps[0].selling_asset == "native"


def test_fetch_watchlist_degrades_on_error(monkeypatch):
    class FakeResponse:
        status_code = 404

        def json(self):
            return {}

        @property
        def is_success(self):
            return False

    class FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(
        "stellarhydra.integrations.stellarroute_client.httpx.Client",
        lambda **kwargs: FakeClient(),
    )
    client = StellarRouteClient()
    signals = client.fetch_watchlist_signals()
    assert len(signals) >= 1
    assert signals[0].stellarroute_healthy is False
