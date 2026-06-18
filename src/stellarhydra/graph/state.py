# LangGraph state schema for a single Hydra liquidity balancing cycle.
from __future__ import annotations

import operator
from typing import Annotated, Any

from typing_extensions import TypedDict

from stellarhydra.models.predictions import (
    BottleneckPrediction,
    CycleResult,
    DripActionPlan,
)
from stellarhydra.models.signals import RoutingSignal


class HydraState(TypedDict, total=False):
    cycle_id: str
    signals: list[RoutingSignal]
    predictions: list[BottleneckPrediction]
    action_plan: DripActionPlan | None
    execution_result: dict[str, Any]
    cycle_result: CycleResult
    errors: Annotated[list[str], operator.add]
    skip_execution: bool
