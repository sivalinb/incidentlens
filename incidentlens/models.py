from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Evidence:
    id: str
    signal: str
    source: str
    query: str
    summary: str
    raw: dict[str, Any]
    collected_at: str = field(default_factory=utc_now)


@dataclass
class ToolFailure:
    tool: str
    error: str
    attempt: int
    strategy: str
    recovered: bool = False
    recorded_at: str = field(default_factory=utc_now)


@dataclass
class Hypothesis:
    cause: str
    confidence: float
    verdict: str
    evidence_ids: list[str]
    rationale: str


@dataclass
class TimelineEvent:
    node: str
    message: str
    outcome: str
    at: str = field(default_factory=utc_now)


@dataclass
class IncidentState:
    incident_id: str
    scenario_id: str
    status: str
    modes: dict[str, str]
    alert: dict[str, Any]
    evidence: list[Evidence] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    tool_failures: list[ToolFailure] = field(default_factory=list)
    recommendation: dict[str, Any] = field(default_factory=dict)
    approval: bool | None = None
    reviewer_note: str = ""
    timeline: list[TimelineEvent] = field(default_factory=list)
    final_action: str = "none"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def add_event(self, node: str, message: str, outcome: str) -> None:
        self.timeline.append(TimelineEvent(node=node, message=message, outcome=outcome))
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IncidentState":
        copied = dict(data)
        copied["evidence"] = [Evidence(**item) for item in copied.get("evidence", [])]
        copied["hypotheses"] = [Hypothesis(**item) for item in copied.get("hypotheses", [])]
        copied["tool_failures"] = [ToolFailure(**item) for item in copied.get("tool_failures", [])]
        copied["timeline"] = [TimelineEvent(**item) for item in copied.get("timeline", [])]
        return cls(**copied)
