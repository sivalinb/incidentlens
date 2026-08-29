from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from .evaluation import Evaluator
from .llm import OpenAICompatibleHypothesisEngine
from .models import IncidentState, ToolFailure
from .persistence import IncidentStore
from .reasoning import EvidenceCritic, HypothesisEngine, RuleBasedHypothesisEngine
from .scenarios import ScenarioCatalog
from .tools import EmptyToolResult, ReplayTelemetryTools, TransientToolError


class IncidentLensApp:
    def __init__(self, db_path: str | Path = ".incidentlens/incidents.db") -> None:
        self.catalog = ScenarioCatalog()
        self.store = IncidentStore(db_path)
        self.critic = EvidenceCritic()
        self.evaluator = Evaluator()

    def investigate(
        self,
        scenario_id: str,
        *,
        inject_failure: bool = False,
        use_llm: bool = False,
        engine: str = "native",
    ) -> IncidentState:
        if engine == "langgraph":
            from .langgraph_adapter import run_graph

            return run_graph(self, scenario_id, inject_failure=inject_failure, use_llm=use_llm)
        scenario = self.catalog.load(scenario_id)
        state = IncidentState(
            incident_id=f"IL-{uuid4().hex[:8].upper()}",
            scenario_id=scenario_id,
            status="investigating",
            modes={
                "telemetry_mode": "deterministic_replay",
                "reasoning_mode": "llm" if use_llm else "deterministic_rubric",
                "orchestration_engine": "native_python",
                "action_mode": "simulation",
            },
            alert=scenario["alert"],
        )
        state.add_event("scope", "Alert boundary and incident window recorded", "success")
        tools = ReplayTelemetryTools(inject_failure=inject_failure)
        for signal in ("metrics", "logs", "trace"):
            self._collect(state, scenario, tools, signal)
        reasoning: HypothesisEngine = OpenAICompatibleHypothesisEngine() if use_llm else RuleBasedHypothesisEngine()
        state.hypotheses = self.critic.review(state.evidence, reasoning.generate(state.alert, state.evidence))
        state.add_event("critic", "Hypotheses ranked and evidence citations validated", "success")
        state.recommendation = dict(scenario["recommendation"])
        state.status = "awaiting_approval"
        state.final_action = "none"
        state.add_event("human_gate", "Write-like remediation remains blocked pending human decision", "interrupt")
        self.store.save(state)
        return state

    def _collect(self, state: IncidentState, scenario: dict, tools: ReplayTelemetryTools, signal: str) -> None:
        for attempt in (1, 2):
            try:
                evidence = tools.collect(scenario, signal, attempt)
                state.evidence.append(evidence)
                for failure in state.tool_failures:
                    if failure.tool == signal and not failure.recovered:
                        failure.recovered = True
                state.add_event(signal, f"Collected {evidence.id} using {evidence.query}", "success")
                return
            except (TransientToolError, EmptyToolResult) as exc:
                strategy = "narrow query" if isinstance(exc, TransientToolError) else "widen filters"
                state.tool_failures.append(ToolFailure(tool=signal, error=str(exc), attempt=attempt, strategy=strategy))
                state.add_event(signal, f"{exc}; {strategy}", "retry")
        state.status = "failed"
        self.store.save(state)
        raise RuntimeError(f"{signal} exhausted two bounded attempts")

    def decide(self, incident_id: str, approved: bool, note: str = "") -> IncidentState:
        state = self.store.load(incident_id)
        if state.status != "awaiting_approval":
            raise ValueError(f"Incident is in '{state.status}', not awaiting_approval")
        state.approval = approved
        state.reviewer_note = note
        if approved:
            state.status = "approved_pending_verification"
            state.final_action = "verification_plan_only"
            state.add_event("human_gate", "Plan approved; no production action executed", "approved")
        else:
            state.status = "rejected"
            state.final_action = "none"
            state.add_event("human_gate", "Recommendation rejected; investigation stopped safely", "rejected")
        self.store.save(state)
        return state

    def evaluate(self, state: IncidentState) -> dict:
        return self.evaluator.evaluate(state)

