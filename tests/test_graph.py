# Unit tests for LangGraph cycle orchestration with mocked StellarRoute.
from unittest.mock import patch

from stellarhydra.graph.hydra_graph import run_cycle
from stellarhydra.models.signals import RoutingSignal


def test_run_cycle_completes_with_mocked_signals():
    mock_signal = RoutingSignal(
        base="native",
        quote="USDC",
        amount="100",
        slippage_bps=50,
        price_impact_bps=200,
        orderbook_bid_depth=5.0,
        stellarroute_healthy=True,
    )

    with patch(
        "stellarhydra.graph.hydra_graph.StellarRouteClient.fetch_watchlist_signals",
        return_value=[mock_signal],
    ), patch(
        "stellarhydra.graph.hydra_graph.SignalCache.store",
        return_value=None,
    ):
        result = run_cycle(thread_id="test-cycle-1")

    assert result.cycle_id == "test-cycle-1"
    assert result.signals_collected == 1
    assert len(result.predictions) >= 1
    assert result.action_plan is not None
