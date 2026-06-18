# Unit tests for drip decision policy and action plans.
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
    plan = decide_drip_action([prediction], Settings(hydra_max_drip_xlm_per_hour=100))
    assert plan.stream_amount_xlm == 100.0
