# Unit tests for human-in-the-loop threshold helpers.
from stellarhydra.graph.hitl import hitl_interrupt_payload, hitl_review_required


def test_hitl_required_at_threshold():
    assert hitl_review_required(500.0, yaml_threshold=500.0) is True


def test_hitl_not_required_below_threshold():
    assert hitl_review_required(499.99, yaml_threshold=500.0) is False


def test_hitl_interrupt_payload_shape():
    plan = {"action": "adjust_rate", "pair": "native:USDC", "stream_amount_xlm": 600.0}
    payload = hitl_interrupt_payload(plan)
    assert payload["type"] == "drip_approval_required"
    assert payload["plan"] == plan
    assert "Review" in payload["message"]
