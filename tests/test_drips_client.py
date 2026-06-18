# Unit tests for Drips client dry-run execution.
from stellarhydra.integrations.drips_client import DripsClient
from stellarhydra.config import Settings
from stellarhydra.models.predictions import DripActionPlan, DripActionType


def test_drips_dry_run_returns_payload():
    client = DripsClient(Settings(DRIPS_DRY_RUN=True))
    plan = DripActionPlan(
        action=DripActionType.CREATE_STREAM,
        pair="native:USDC",
        stream_amount_xlm=50.0,
        target_path=["native->USDC"],
        rationale="test",
        dry_run=True,
    )
    result = client.execute_plan(plan)
    assert result["status"] == "dry_run"
    assert result["payload"]["action"] == "create_stream"


def test_drips_no_op_skipped():
    client = DripsClient(Settings(DRIPS_DRY_RUN=True))
    plan = DripActionPlan(action=DripActionType.NO_OP, pair="none")
    result = client.execute_plan(plan)
    assert result["status"] == "skipped"
