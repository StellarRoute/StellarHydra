# Bottleneck prediction agent — heuristic analysis of routing signals.
from __future__ import annotations

from stellarhydra.config import Settings, get_settings
from stellarhydra.models.predictions import BottleneckPrediction, BottleneckSeverity
from stellarhydra.models.signals import RoutingSignal


def predict_bottlenecks(
    signals: list[RoutingSignal],
    settings: Settings | None = None,
    history_by_pair: dict[str, list[RoutingSignal]] | None = None,
) -> list[BottleneckPrediction]:
    """Rank pairs by predicted liquidity stress using simple thresholds."""
    cfg = settings or get_settings()
    yaml_policy = cfg.yaml_config().get("policy", {})
    slippage_threshold = int(yaml_policy.get("slippage_alert_bps", cfg.hydra_slippage_alert_bps))
    min_depth = float(yaml_policy.get("min_orderbook_depth_native", 100))
    horizon = int(yaml_policy.get("prediction_horizon_minutes", cfg.hydra_prediction_horizon_minutes))

    predictions: list[BottleneckPrediction] = []

    for signal in signals:
        if not signal.stellarroute_healthy:
            predictions.append(
                BottleneckPrediction(
                    pair=signal.pair_key(),
                    severity=BottleneckSeverity.MEDIUM,
                    confidence=0.6,
                    horizon_minutes=horizon,
                    reason="StellarRoute API unhealthy for pair",
                    affected_hops=[step.selling_asset for step in signal.path],
                )
            )
            continue

        stress_score = 0.0
        reasons: list[str] = []

        impact = signal.price_impact_bps or 0
        if impact >= slippage_threshold:
            stress_score += 0.4
            reasons.append(f"price impact {impact} bps >= {slippage_threshold}")

        bid_depth = signal.orderbook_bid_depth or 0.0
        if bid_depth < min_depth:
            stress_score += 0.3
            reasons.append(f"bid depth {bid_depth} < {min_depth}")

        if signal.excluded_venue_count > 0:
            stress_score += 0.2
            reasons.append(f"{signal.excluded_venue_count} excluded venues")

        if signal.route_count <= 1:
            stress_score += 0.1
            reasons.append("single or no alternate routes")

        prior = (history_by_pair or {}).get(signal.pair_key()) or []
        if prior:
            prev_impact = prior[0].price_impact_bps or 0
            if impact > prev_impact + 10:
                stress_score += 0.15
                reasons.append(f"slippage rising vs prior snapshot ({prev_impact} -> {impact} bps)")

        if stress_score < 0.3:
            continue

        severity = BottleneckSeverity.LOW
        if stress_score >= 0.6:
            severity = BottleneckSeverity.HIGH
        elif stress_score >= 0.4:
            severity = BottleneckSeverity.MEDIUM

        predictions.append(
            BottleneckPrediction(
                pair=signal.pair_key(),
                severity=severity,
                confidence=min(stress_score, 0.95),
                horizon_minutes=horizon,
                reason="; ".join(reasons) or "elevated routing stress",
                affected_hops=[f"{s.selling_asset}->{s.buying_asset}" for s in signal.path],
                predicted_slippage_bps=impact or None,
            )
        )

    predictions.sort(key=lambda p: p.confidence, reverse=True)
    return predictions
