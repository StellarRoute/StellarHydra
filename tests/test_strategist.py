# Unit tests for drip decision policy and action plans.
from pathlib import Path

from stellarhydra.agents.strategist import decide_drip_action
from stellarhydra.config import Settings
from stellarhydra.models.predictions import BottleneckPrediction, BottleneckSeverity, DripActionType


def test_decide_no_op_when_empty():
    plan = decide_drip_action([])
    assert plan.action == DripActionType.NO_OP


def test_decide_adjust_rate_for_high_severity():
    prediction = BottleneckPrediction(
        pair="native:USDC",
        severity=BottleneckSeverity.HIGH,
        confidence=0.85,
        horizon_minutes=30,
        reason="test",
    )
    plan = decide_drip_action([prediction], Settings(hydra_max_drip_xlm_per_hour=1000))
    assert plan.action == DripActionType.ADJUST_RATE
    assert plan.stream_amount_xlm == 300.0
    assert plan.policy_ok is True


def test_decide_caps_at_policy_max():
    prediction = BottleneckPrediction(
        pair="native:USDC",
        severity=BottleneckSeverity.HIGH,
        confidence=0.9,
        horizon_minutes=30,
        reason="test",
    )
    plan = decide_drip_action(
        [prediction],
        Settings.model_construct(
            hydra_max_drip_xlm_per_hour=100,
            drips_dry_run=True,
            config_path=Path("/nonexistent/settings.yaml"),
        ),
    )
    assert plan.stream_amount_xlm == 100.0
    assert plan.policy_ok is False


def test_decide_rejects_disallowed_assets(monkeypatch, tmp_path):
    cfg_path = tmp_path / "settings.yaml"
    cfg_path.write_text(
        "policy:\n  allowed_assets:\n    - native\n",
        encoding="utf-8",
    )
    settings = Settings(config_path=cfg_path, hydra_watchlist="native:USDC")
    prediction = BottleneckPrediction(
        pair="native:USDC",
        severity=BottleneckSeverity.HIGH,
        confidence=0.9,
        horizon_minutes=30,
        reason="test",
    )
    plan = decide_drip_action([prediction], settings)
    assert plan.action == DripActionType.NO_OP
    assert plan.policy_ok is False
