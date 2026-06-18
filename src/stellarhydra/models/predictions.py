# Pydantic models for bottleneck predictions and drip action plans.
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class BottleneckSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BottleneckPrediction(BaseModel):
    pair: str
    severity: BottleneckSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    horizon_minutes: int
    reason: str
    affected_hops: list[str] = Field(default_factory=list)
    predicted_slippage_bps: int | None = None


class DripActionType(str, Enum):
    NO_OP = "no_op"
    CREATE_STREAM = "create_stream"
    ADJUST_RATE = "adjust_rate"
    PAUSE_STREAM = "pause_stream"


class DripActionPlan(BaseModel):
    action: DripActionType
    pair: str
    stream_amount_xlm: float = 0.0
    target_path: list[str] = Field(default_factory=list)
    rationale: str = ""
    dry_run: bool = True
    policy_ok: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CycleResult(BaseModel):
    cycle_id: str
    signals_collected: int = 0
    predictions: list[BottleneckPrediction] = Field(default_factory=list)
    action_plan: DripActionPlan | None = None
    execution_status: str = "pending"
    errors: list[str] = Field(default_factory=list)
