# LangGraph multi-agent workflow: collect signals, predict, decide, execute drip actions.
from __future__ import annotations

import logging
import uuid
from typing import Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from stellarhydra.agents.executor import execute_drip_plan
from stellarhydra.agents.predictor import predict_bottlenecks
from stellarhydra.agents.strategist import decide_drip_action
from stellarhydra.config import Settings, get_settings
from stellarhydra.graph.state import HydraState
from stellarhydra.integrations.signal_cache import SignalCache
from stellarhydra.integrations.stellarroute_client import StellarRouteClient
from stellarhydra.graph.hitl import hitl_review_required
from stellarhydra.models.predictions import CycleResult, DripActionType
from stellarhydra.security.kill_switch import is_kill_switch_active

logger = logging.getLogger(__name__)

COLLECT_SIGNALS = "collect_signals"
PREDICT = "predict"
DECIDE = "decide"
EXECUTE = "execute"
FINALIZE = "finalize"


def collect_signals(state: HydraState, settings: Settings | None = None) -> Command[
    Literal["predict"]
]:
    """Pull routing signals from StellarRoute for each watchlist pair."""
    cfg = settings or get_settings()
    cycle_id = state.get("cycle_id") or str(uuid.uuid4())
    client = StellarRouteClient(cfg)
    cache = SignalCache(cfg)

    try:
        signals = client.fetch_watchlist_signals()
        for signal in signals:
            if signal.stellarroute_healthy:
                cache.store(signal)

        # Attach neutral sentiment stub per unique base asset (Phase 2 hook).
        from stellarhydra.agents.sentiment import fetch_sentiment_stub

        seen_assets: set[str] = set()
        for signal in signals:
            asset = signal.base
            if asset in seen_assets:
                continue
            seen_assets.add(asset)
            sentiment = fetch_sentiment_stub(asset)
            logger.debug("Sentiment stub for %s: score=%s", asset, sentiment.score)
    except Exception as exc:  # noqa: BLE001 — degrade gracefully in orchestrator
        logger.exception("Signal collection failed")
        return Command(
            update={
                "cycle_id": cycle_id,
                "signals": [],
                "errors": [f"collect_signals: {exc}"],
            },
            goto=PREDICT,
        )

    return Command(
        update={"cycle_id": cycle_id, "signals": signals},
        goto=PREDICT,
    )


def predict(state: HydraState, settings: Settings | None = None) -> Command[Literal["decide"]]:
    """Run bottleneck prediction over collected signals."""
    cfg = settings or get_settings()
    signals = state.get("signals") or []
    cache = SignalCache(cfg)
    history_by_pair = {s.pair_key(): cache.get_history(s.pair_key()) for s in signals}
    predictions = predict_bottlenecks(signals, cfg, history_by_pair=history_by_pair)
    return Command(update={"predictions": predictions}, goto=DECIDE)


def decide(state: HydraState, settings: Settings | None = None) -> Command[
    Literal["execute", "finalize"]
]:
    """Map predictions to a policy-checked drip action plan."""
    cfg = settings or get_settings()
    predictions = state.get("predictions") or []
    plan = decide_drip_action(predictions, cfg)

    if plan.action == DripActionType.NO_OP:
        return Command(update={"action_plan": plan, "skip_execution": True}, goto=FINALIZE)

    if not plan.policy_ok:
        return Command(
            update={
                "action_plan": plan,
                "skip_execution": True,
                "errors": ["Policy cap would be exceeded; skipping execution"],
            },
            goto=FINALIZE,
        )

    yaml_policy = cfg.yaml_config().get("policy", {})
    hitl_threshold = float(yaml_policy.get("hitl_threshold_xlm", 500))

    if hitl_review_required(plan.stream_amount_xlm, yaml_threshold=hitl_threshold):
        return Command(
            update={
                "action_plan": plan,
                "skip_execution": True,
                "errors": [f"HITL review required for {plan.stream_amount_xlm} XLM/hour plan"],
            },
            goto=FINALIZE,
        )

    return Command(update={"action_plan": plan, "skip_execution": False}, goto=EXECUTE)


def execute(state: HydraState, settings: Settings | None = None) -> Command[Literal["finalize"]]:
    """Execute drip plan via Drips client (dry-run by default)."""
    cfg = settings or get_settings()
    if is_kill_switch_active(StellarRouteClient(cfg)):
        return Command(
            update={
                "skip_execution": True,
                "errors": ["StellarRoute kill switch active; skipping drip execution"],
            },
            goto=FINALIZE,
        )

    plan = state.get("action_plan")
    if plan is None:
        return Command(
            update={"errors": ["execute: missing action_plan"]},
            goto=FINALIZE,
        )

    result = execute_drip_plan(plan)
    status = result.get("status", "unknown")
    if status == "error":
        return Command(
            update={"execution_result": result, "errors": [result.get("message", "drip error")]},
            goto=FINALIZE,
        )

    return Command(update={"execution_result": result}, goto=FINALIZE)


def finalize(state: HydraState, settings: Settings | None = None) -> Command[Literal["__end__"]]:
    """Assemble cycle result for observability and API responses."""
    cfg = settings or get_settings()
    execution = state.get("execution_result") or {}
    skip = state.get("skip_execution", False)
    if skip:
        status = "skipped"
    elif execution.get("status") == "error":
        status = "failed"
    elif execution.get("status") in ("dry_run", "success", "completed"):
        status = "success"
    else:
        status = execution.get("status", "completed")

    cycle_result = CycleResult(
        cycle_id=state.get("cycle_id") or "unknown",
        signals_collected=len(state.get("signals") or []),
        predictions=state.get("predictions") or [],
        action_plan=state.get("action_plan"),
        execution_status=str(status),
        errors=state.get("errors") or [],
    )
    try:
        cache = SignalCache(cfg)
        cache.store_cycle(cycle_result.cycle_id, cycle_result.model_dump_json())
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to persist cycle result to Redis: %s", exc)
    return Command(update={"cycle_result": cycle_result}, goto=END)


def build_hydra_graph(settings: Settings | None = None):
    """Compile edgeless LangGraph with MemorySaver checkpointing."""
    cfg = settings or get_settings()

    def _collect(state: HydraState):
        return collect_signals(state, cfg)

    def _predict(state: HydraState):
        return predict(state, cfg)

    def _decide(state: HydraState):
        return decide(state, cfg)

    def _execute(state: HydraState):
        return execute(state, cfg)

    def _finalize(state: HydraState):
        return finalize(state, cfg)

    builder = StateGraph(HydraState)
    builder.add_node(COLLECT_SIGNALS, _collect, destinations=(PREDICT,))
    builder.add_node(PREDICT, _predict, destinations=(DECIDE,))
    builder.add_node(DECIDE, _decide, destinations=(EXECUTE, FINALIZE))
    builder.add_node(EXECUTE, _execute, destinations=(FINALIZE,))
    builder.add_node(FINALIZE, _finalize, destinations=(END,))
    builder.add_edge(START, COLLECT_SIGNALS)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


def run_cycle(thread_id: str | None = None, settings: Settings | None = None) -> CycleResult:
    """Invoke one full Hydra cycle and return the finalized result."""
    cfg = settings or get_settings()
    app = build_hydra_graph(cfg)
    tid = thread_id or f"{cfg.hydra_checkpoint_thread_prefix}{uuid.uuid4()}"
    config = {"configurable": {"thread_id": tid}}

    final_state = app.invoke({"cycle_id": tid}, config=config)
    result = final_state.get("cycle_result")
    if isinstance(result, CycleResult):
        return result
    return CycleResult(cycle_id=tid, execution_status="unknown")


def main() -> None:
    logging.basicConfig(level=get_settings().hydra_log_level)
    result = run_cycle()
    print(f"Cycle {result.cycle_id} status={result.execution_status}")
    print(f"Signals={result.signals_collected} predictions={len(result.predictions)}")
    if result.action_plan:
        print(f"Action={result.action_plan.action.value} pair={result.action_plan.pair}")


if __name__ == "__main__":
    main()
