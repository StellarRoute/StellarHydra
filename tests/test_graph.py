# Unit tests for LangGraph cycle orchestration with mocked StellarRoute.
from pathlib import Path
from unittest.mock import patch

from stellarhydra.config import Settings
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
        "stellarhydra.graph.hydra_graph.SignalCache.get_history",
        return_value=[],
    ), patch(
        "stellarhydra.graph.hydra_graph.SignalCache.store_cycle",
        return_value=None,
    ), patch(
        "stellarhydra.graph.hydra_graph.is_kill_switch_active",
        return_value=False,
    ):
        result = run_cycle(thread_id="test-cycle-1")

    assert result.cycle_id == "test-cycle-1"
    assert result.signals_collected == 1
    assert len(result.predictions) >= 1
    assert result.action_plan is not None


def test_run_cycle_skips_when_policy_blocked():
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
    ), patch(
        "stellarhydra.graph.hydra_graph.SignalCache.get_history",
        return_value=[],
    ), patch(
        "stellarhydra.graph.hydra_graph.is_kill_switch_active",
        return_value=False,
    ):
        result = run_cycle(
            thread_id="policy-block",
            settings=Settings.model_construct(
                hydra_max_drip_xlm_per_hour=10,
                drips_dry_run=True,
                config_path=Path("/nonexistent/settings.yaml"),
            ),
        )

    assert result.execution_status == "skipped"
