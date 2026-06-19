# Drip decision agent — maps predictions to policy-checked action plans.
from __future__ import annotations

from stellarhydra.config import Settings, get_settings
from stellarhydra.models.predictions import (
    BottleneckPrediction,
    BottleneckSeverity,
    DripActionPlan,
    DripActionType,
)


def decide_drip_action(
    predictions: list[BottleneckPrediction],
    settings: Settings | None = None,
) -> DripActionPlan:
    """Choose a drip action for the highest-confidence prediction."""
    cfg = settings or get_settings()
    dry_run = cfg.drips_dry_run
    yaml_policy = cfg.yaml_config().get("policy", {})
    yaml_max = yaml_policy.get("max_drip_xlm_per_hour")
    max_xlm = cfg.hydra_max_drip_xlm_per_hour
    if yaml_max is not None:
        max_xlm = min(max_xlm, float(yaml_max))

    if not predictions:
        return DripActionPlan(
            action=DripActionType.NO_OP,
            pair="none",
            rationale="No bottlenecks predicted",
            dry_run=dry_run,
        )

    top = predictions[0]
    allowed = cfg.allowed_assets()
    if allowed:
        base, _, quote = top.pair.partition(":")
        if base not in allowed or quote not in allowed:
            return DripActionPlan(
                action=DripActionType.NO_OP,
                pair=top.pair,
                rationale=f"Pair assets not in allowlist: {top.pair}",
                dry_run=dry_run,
                policy_ok=False,
            )

    if top.severity == BottleneckSeverity.LOW and top.confidence < 0.5:
        return DripActionPlan(
            action=DripActionType.NO_OP,
            pair=top.pair,
            rationale=f"Low severity ({top.confidence:.2f}) below action threshold",
            dry_run=dry_run,
        )

    if top.severity == BottleneckSeverity.LOW and top.confidence >= 0.5:
        return DripActionPlan(
            action=DripActionType.PAUSE_STREAM,
            pair=top.pair,
            rationale=f"Recovered liquidity; pause prior drip ({top.reason})",
            dry_run=dry_run,
        )

    # Scale drip amount by severity; cap via policy.
    amount = 50.0
    if top.severity == BottleneckSeverity.MEDIUM:
        amount = 150.0
    elif top.severity == BottleneckSeverity.HIGH:
        amount = 300.0

    policy_ok = amount <= max_xlm
    if not policy_ok:
        amount = max_xlm

    action = DripActionType.ADJUST_RATE if top.confidence >= 0.7 else DripActionType.CREATE_STREAM

    return DripActionPlan(
        action=action,
        pair=top.pair,
        stream_amount_xlm=amount,
        target_path=top.affected_hops,
        rationale=f"{top.reason} (confidence={top.confidence:.2f})",
        dry_run=dry_run,
        policy_ok=policy_ok,
    )
