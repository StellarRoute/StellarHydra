# Unit tests for drip executor error handling.
from unittest.mock import MagicMock

from stellarhydra.agents.executor import execute_drip_plan
from stellarhydra.integrations.drips_client import DripsError
from stellarhydra.models.predictions import DripActionPlan, DripActionType


def test_executor_returns_error_on_drips_failure():
    client = MagicMock()
    client.execute_plan.side_effect = DripsError("upstream 503")
    plan = DripActionPlan(
        action=DripActionType.ADJUST_RATE,
        pair="native:USDC",
        stream_amount_xlm=100.0,
    )

    result = execute_drip_plan(plan, client=client)

    assert result["status"] == "error"
    assert "503" in result["message"]
