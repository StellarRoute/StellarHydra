# Unit tests for bottleneck prediction heuristics.
from stellarhydra.agents.predictor import predict_bottlenecks
from stellarhydra.models.predictions import BottleneckSeverity
from stellarhydra.models.signals import RoutingSignal


def test_predict_bottlenecks_flags_high_slippage():
    signal = RoutingSignal(
        base="native",
        quote="USDC",
        amount="100",
        slippage_bps=50,
        price_impact_bps=150,
        orderbook_bid_depth=10.0,
        stellarroute_healthy=True,
    )
    predictions = predict_bottlenecks([signal])
    assert len(predictions) >= 1
    assert predictions[0].severity in {BottleneckSeverity.MEDIUM, BottleneckSeverity.HIGH}


def test_predict_bottlenecks_skips_healthy_signal():
    signal = RoutingSignal(
        base="native",
        quote="USDC",
        amount="100",
        slippage_bps=50,
        price_impact_bps=5,
        orderbook_bid_depth=10000.0,
        route_count=3,
        stellarroute_healthy=True,
    )
    predictions = predict_bottlenecks([signal])
    assert predictions == []


def test_predict_bottlenecks_boosts_when_slippage_rises():
    current = RoutingSignal(
        base="native",
        quote="USDC",
        amount="100",
        slippage_bps=50,
        price_impact_bps=120,
        orderbook_bid_depth=500.0,
        route_count=2,
        stellarroute_healthy=True,
    )
    prior = RoutingSignal(
        base="native",
        quote="USDC",
        amount="100",
        slippage_bps=50,
        price_impact_bps=50,
        orderbook_bid_depth=500.0,
        route_count=2,
        stellarroute_healthy=True,
    )
    predictions = predict_bottlenecks(
        [current],
        history_by_pair={"native:USDC": [prior]},
    )
    assert predictions
    assert "rising" in predictions[0].reason
