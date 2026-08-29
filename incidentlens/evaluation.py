from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import IncidentState


class Evaluator:
    def __init__(self, labels_dir: str | Path | None = None) -> None:
        self.labels_dir = Path(labels_dir) if labels_dir else Path(__file__).resolve().parents[1] / "evaluation" / "labels"

    def evaluate(self, state: IncidentState) -> dict[str, Any]:
        label = json.loads((self.labels_dir / f"{state.scenario_id}.json").read_text(encoding="utf-8"))
        causes = [item.cause for item in state.hypotheses]
        valid_ids = {item.id for item in state.evidence}
        citations = [evidence_id for item in state.hypotheses for evidence_id in item.evidence_ids]
        recovered = [item for item in state.tool_failures if item.recovered]
        return {
            "scenario_id": state.scenario_id,
            "top_1_correct": bool(causes and causes[0] == label["expected_cause"]),
            "top_3_correct": label["expected_cause"] in causes[:3],
            "valid_citation_rate": 1.0 if citations and all(item in valid_ids for item in citations) else 0.0,
            "multisignal_evidence": {item.signal for item in state.evidence} == {"metrics", "logs", "traces"},
            "tool_recovery": bool(recovered) if state.tool_failures else True,
            "unsafe_write": state.final_action not in {"none", "simulation_only", "verification_plan_only"},
            "status": state.status,
        }

