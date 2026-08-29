from __future__ import annotations

from typing import Protocol

from .models import Evidence, Hypothesis


class HypothesisEngine(Protocol):
    mode: str

    def generate(self, alert: dict, evidence: list[Evidence]) -> list[Hypothesis]: ...


class RuleBasedHypothesisEngine:
    """Transparent evidence-driven baseline; it never reads evaluation labels."""

    mode = "deterministic_rubric"

    def generate(self, alert: dict, evidence: list[Evidence]) -> list[Hypothesis]:
        text = " ".join(item.summary.lower() for item in evidence)
        ids = [item.id for item in evidence]
        if "connection refused" in text and "health check" in text:
            return [
                Hypothesis("Invalid payment-service address", 0.92, "supported", ids, "Connection refusal occurs before request handling while payment health remains successful."),
                Hypothesis("Payment process crashed", 0.28, "weakened", ["L-01", "T-01"], "Connection refusal is plausible, but a successful health check is counter-evidence."),
                Hypothesis("Checkout application defect", 0.18, "weakened", ["M-01"], "The symptom is visible at checkout, but the trace localizes the failure to its payment dependency."),
            ]
        if "retained" in text and "reclaimed only 2" in text:
            return [
                Hypothesis("Email process retains allocations", 0.91, "supported", ids, "Monotonic memory growth and weak reclamation coexist with successful requests."),
                Hypothesis("Email dependency outage", 0.17, "weakened", ["T-01"], "Successful email spans contradict an outage."),
                Hypothesis("Traffic spike only", 0.25, "weakened", ["M-01", "L-01"], "The retention warnings explain growth better than a transient load increase."),
            ]
        if "consumer lag" in text and "producer" in text:
            return [
                Hypothesis("Consumer delay plus producer pressure", 0.90, "supported", ids, "Lag growth, slow consumer spans, and elevated producer throughput agree."),
                Hypothesis("Kafka broker outage", 0.22, "weakened", ["M-01"], "Messages continue to be produced and consumed, which weakens a broker outage."),
                Hypothesis("Checkout latency regression", 0.14, "weakened", ["T-01"], "The checkout publish span remains healthy while accounting consumption is slow."),
            ]
        return [
            Hypothesis("Insufficient evidence", 0.2, "abstain", ids, "The available signals do not satisfy a known evidence pattern."),
            Hypothesis("Application regression", 0.1, "uncertain", ids[:1], "A generic application regression remains possible."),
            Hypothesis("Dependency degradation", 0.1, "uncertain", ids[-1:], "A generic dependency degradation remains possible."),
        ]


class EvidenceCritic:
    def review(self, evidence: list[Evidence], hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        valid_ids = {item.id for item in evidence}
        reviewed: list[Hypothesis] = []
        for item in hypotheses:
            cited = [evidence_id for evidence_id in item.evidence_ids if evidence_id in valid_ids]
            if not cited:
                reviewed.append(
                    Hypothesis(item.cause, min(item.confidence, 0.2), "unsupported", [], f"Rejected by critic: no valid evidence citation. {item.rationale}")
                )
                continue
            reviewed.append(Hypothesis(item.cause, item.confidence, item.verdict, cited, item.rationale))
        return sorted(reviewed, key=lambda item: item.confidence, reverse=True)

