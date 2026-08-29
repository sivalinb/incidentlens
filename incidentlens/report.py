from __future__ import annotations

import json

from .models import IncidentState


def render_text(state: IncidentState) -> str:
    top = state.hypotheses[0] if state.hypotheses else None
    rows = [
        f"Incident             {state.incident_id}",
        f"Scenario             {state.scenario_id}",
        f"Telemetry mode       {state.modes['telemetry_mode']}",
        f"Orchestrator         {state.modes['orchestration_engine']}",
        f"Reasoning            {state.modes['reasoning_mode']}",
        f"Remediation          {state.modes['action_mode']}",
        f"Evidence             {', '.join(item.id for item in state.evidence)}",
        f"State                {state.status}",
        f"Action               {state.final_action}",
    ]
    if state.tool_failures:
        rows.insert(6, f"Recovery             {state.tool_failures[0].strategy}; retry succeeded")
    if top:
        rows.append(f"Leading cause        {top.cause} ({top.confidence:.0%})")
        rows.append(f"Citations            {', '.join(top.evidence_ids)}")
    rows.append("Production write     none")
    return "\n".join(rows)


def render_json(state: IncidentState) -> str:
    return json.dumps(state.to_dict(), indent=2, sort_keys=True)

