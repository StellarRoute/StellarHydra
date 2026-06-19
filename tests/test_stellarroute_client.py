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


def test_fetch_pairs_parses_list(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {"data": {"pairs": [{"base": "native", "quote": "USDC"}]}}

        def raise_for_status(self):
            return None

    class FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, path, *args, **kwargs):
            if path == "/api/v1/pairs":
                return FakeResponse()
            raise AssertionError(path)

    monkeypatch.setattr(
        "stellarhydra.integrations.stellarroute_client.httpx.Client",
        lambda **kwargs: FakeClient(),
    )
    client = StellarRouteClient()
    pairs = client.fetch_pairs()
    assert pairs[0]["base"] == "native"


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
