from __future__ import annotations

import operator
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Any, TypedDict
from uuid import uuid4

from .llm import OpenAICompatibleHypothesisEngine
from .models import Evidence, Hypothesis, IncidentState, ToolFailure, TimelineEvent, utc_now
from .reasoning import EvidenceCritic, RuleBasedHypothesisEngine
from .tools import EmptyToolResult, ReplayTelemetryTools, TransientToolError


class GraphState(TypedDict, total=False):
    incident_id: str
    scenario_id: str
    status: str
    modes: dict[str, str]
    alert: dict[str, Any]
    evidence: Annotated[list[dict[str, Any]], operator.add]
    hypotheses: list[dict[str, Any]]
    tool_failures: Annotated[list[dict[str, Any]], operator.add]
    recommendation: dict[str, Any]
    approval: bool | None
    reviewer_note: str
    timeline: Annotated[list[dict[str, Any]], operator.add]
    final_action: str
    created_at: str
    updated_at: str
    inject_failure: bool
    use_llm: bool


def _event(node: str, message: str, outcome: str) -> dict[str, Any]:
    return asdict(TimelineEvent(node=node, message=message, outcome=outcome))


def _collect_node(state: GraphState, signal: str, scenario: dict[str, Any]) -> dict[str, Any]:
    tools = ReplayTelemetryTools(inject_failure=bool(state.get("inject_failure")))
    failures: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for attempt in (1, 2):
        try:
            evidence = tools.collect(scenario, signal, attempt)
            if failures:
                failures[-1]["recovered"] = True
            events.append(_event(signal, f"Collected {evidence.id} using {evidence.query}", "success"))
            return {"evidence": [asdict(evidence)], "tool_failures": failures, "timeline": events, "updated_at": utc_now()}
        except (TransientToolError, EmptyToolResult) as exc:
            strategy = "narrow query" if isinstance(exc, TransientToolError) else "widen filters"
            failures.append(asdict(ToolFailure(tool=signal, error=str(exc), attempt=attempt, strategy=strategy)))
            events.append(_event(signal, f"{exc}; {strategy}", "retry"))
    raise RuntimeError(f"{signal} exhausted two bounded attempts")


def build_graph(app: Any, connection: sqlite3.Connection):
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        from langgraph.graph import END, START, StateGraph
        from langgraph.types import interrupt
    except ImportError as exc:
        raise RuntimeError("Install the optional graph runtime with: pip install -e '.[langgraph]'") from exc

    checkpointer = SqliteSaver(connection)
    builder = StateGraph(GraphState)

    def metrics(state: GraphState) -> dict[str, Any]:
        return _collect_node(state, "metrics", app.catalog.load(state["scenario_id"]))

    def logs(state: GraphState) -> dict[str, Any]:
        return _collect_node(state, "logs", app.catalog.load(state["scenario_id"]))

    def traces(state: GraphState) -> dict[str, Any]:
        return _collect_node(state, "trace", app.catalog.load(state["scenario_id"]))

    def reason(state: GraphState) -> dict[str, Any]:
        evidence = [Evidence(**item) for item in state["evidence"]]
        engine = OpenAICompatibleHypothesisEngine() if state.get("use_llm") else RuleBasedHypothesisEngine()
        hypotheses = engine.generate(state["alert"], evidence)
        return {
            "hypotheses": [asdict(item) for item in hypotheses],
            "timeline": [_event("hypothesis", "Generated three evidence-cited alternatives", "success")],
            "updated_at": utc_now(),
        }

    def criticize(state: GraphState) -> dict[str, Any]:
        evidence = [Evidence(**item) for item in state["evidence"]]
        hypotheses = [Hypothesis(**item) for item in state["hypotheses"]]
        reviewed = EvidenceCritic().review(evidence, hypotheses)
        return {
            "hypotheses": [asdict(item) for item in reviewed],
            "timeline": [_event("critic", "Hypotheses ranked and evidence citations validated", "success")],
            "updated_at": utc_now(),
        }

    def prepare_gate(state: GraphState) -> dict[str, Any]:
        scenario = app.catalog.load(state["scenario_id"])
        return {
            "recommendation": dict(scenario["recommendation"]),
            "status": "awaiting_approval",
            "final_action": "none",
            "timeline": [_event("human_gate", "Write-like remediation remains blocked pending human decision", "interrupt")],
            "updated_at": utc_now(),
        }

    def human_gate(state: GraphState) -> dict[str, Any]:
        decision = interrupt(
            {
                "type": "write_action_approval",
                "incident_id": state["incident_id"],
                "recommendation": state["recommendation"],
                "evidence_ids": [item["id"] for item in state["evidence"]],
                "leading_hypothesis": state["hypotheses"][0],
            }
        )
        return {"approval": bool(decision["approved"]), "reviewer_note": str(decision.get("note", ""))}

    def finalize(state: GraphState) -> dict[str, Any]:
        if state.get("approval"):
            return {
                "status": "approved_pending_verification",
                "final_action": "verification_plan_only",
                "timeline": [_event("human_gate", "Plan approved; no production action executed", "approved")],
                "updated_at": utc_now(),
            }
        return {
            "status": "rejected",
            "final_action": "none",
            "timeline": [_event("human_gate", "Recommendation rejected; investigation stopped safely", "rejected")],
            "updated_at": utc_now(),
        }

    for name, node in (
        ("metrics", metrics),
        ("logs", logs),
        ("traces", traces),
        ("reason", reason),
        ("criticize", criticize),
        ("prepare_gate", prepare_gate),
        ("human_gate", human_gate),
        ("finalize", finalize),
    ):
        builder.add_node(name, node)
    builder.add_edge(START, "metrics")
    builder.add_edge("metrics", "logs")
    builder.add_edge("logs", "traces")
    builder.add_edge("traces", "reason")
    builder.add_edge("reason", "criticize")
    builder.add_edge("criticize", "prepare_gate")
    builder.add_edge("prepare_gate", "human_gate")
    builder.add_edge("human_gate", "finalize")
    builder.add_edge("finalize", END)
    return builder.compile(checkpointer=checkpointer)


def _checkpoint_path(app: Any) -> Path:
    return Path(app.store.path).parent / "langgraph-checkpoints.sqlite"


def _to_incident_state(data: dict[str, Any]) -> IncidentState:
    keys = {
        "incident_id", "scenario_id", "status", "modes", "alert", "evidence", "hypotheses",
        "tool_failures", "recommendation", "approval", "reviewer_note", "timeline", "final_action",
        "created_at", "updated_at",
    }
    payload = {key: value for key, value in data.items() if key in keys}
    return IncidentState.from_dict(payload)


def run_graph(app: Any, scenario_id: str, *, inject_failure: bool = False, use_llm: bool = False) -> IncidentState:
    scenario = app.catalog.load(scenario_id)
    incident_id = f"IL-{uuid4().hex[:8].upper()}"
    initial: GraphState = {
        "incident_id": incident_id,
        "scenario_id": scenario_id,
        "status": "investigating",
        "modes": {
            "telemetry_mode": "deterministic_replay",
            "reasoning_mode": "llm" if use_llm else "deterministic_rubric",
            "orchestration_engine": "langgraph",
            "action_mode": "simulation",
        },
        "alert": scenario["alert"],
        "evidence": [],
        "hypotheses": [],
        "tool_failures": [],
        "recommendation": {},
        "approval": None,
        "reviewer_note": "",
        "timeline": [_event("scope", "Alert boundary and incident window recorded", "success")],
        "final_action": "none",
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "inject_failure": inject_failure,
        "use_llm": use_llm,
    }
    path = _checkpoint_path(app)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    try:
        graph = build_graph(app, connection)
        result = graph.invoke(initial, config={"configurable": {"thread_id": incident_id}})
    finally:
        connection.close()
    state = _to_incident_state(result)
    app.store.save(state)
    return state


def resume_graph(app: Any, incident_id: str, approved: bool, note: str = "") -> IncidentState:
    try:
        from langgraph.types import Command
    except ImportError as exc:
        raise RuntimeError("Install the optional graph runtime with: pip install -e '.[langgraph]'") from exc
    path = _checkpoint_path(app)
    if not path.exists():
        raise KeyError(f"No LangGraph checkpoint database exists for {incident_id}")
    connection = sqlite3.connect(path, check_same_thread=False)
    try:
        graph = build_graph(app, connection)
        result = graph.invoke(
            Command(resume={"approved": approved, "note": note}),
            config={"configurable": {"thread_id": incident_id}},
        )
    finally:
        connection.close()
    state = _to_incident_state(result)
    app.store.save(state)
    return state

