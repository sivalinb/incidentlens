from __future__ import annotations

import json
import os
from typing import Any, Callable
from urllib.request import Request, urlopen

from .models import Evidence, Hypothesis


class LLMContractError(RuntimeError):
    pass


class OpenAICompatibleHypothesisEngine:
    """Strict OpenAI-compatible adapter with no evaluation-label access."""

    mode = "llm"

    def __init__(self, transport: Callable[[Request], bytes] | None = None) -> None:
        self.base_url = os.environ.get("LLM_BASE_URL", "").rstrip("/")
        self.api_key = os.environ.get("LLM_API_KEY", "")
        self.model = os.environ.get("LLM_MODEL", "")
        self.transport = transport or self._default_transport
        if not all((self.base_url, self.api_key, self.model)):
            raise LLMContractError("Set LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL locally before --use-llm")

    @staticmethod
    def _default_transport(request: Request) -> bytes:
        with urlopen(request, timeout=60) as response:  # nosec: endpoint is user-configured
            return response.read()

    def generate(self, alert: dict, evidence: list[Evidence]) -> list[Hypothesis]:
        allowed_ids = {item.id for item in evidence}
        prompt_input = {
            "alert": alert,
            "evidence": [
                {"id": item.id, "signal": item.signal, "summary": item.summary, "query": item.query}
                for item in evidence
            ],
        }
        system = (
            "You are an evidence-first SRE investigator. Return JSON only with a top-level "
            "hypotheses array containing exactly three objects. Each object requires cause, "
            "confidence (0 to 1), verdict, evidence_ids, and rationale. Cite only supplied IDs. "
            "Do not claim that a remediation was executed."
        )
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(prompt_input, sort_keys=True)},
                ],
            }
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        raw_response = json.loads(self.transport(request).decode("utf-8"))
        try:
            content = raw_response["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            candidates = parsed["hypotheses"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMContractError("Model response did not satisfy the JSON response contract") from exc
        if not isinstance(candidates, list) or len(candidates) != 3:
            raise LLMContractError("Model must return exactly three hypotheses")
        result: list[Hypothesis] = []
        for candidate in candidates:
            confidence = float(candidate["confidence"])
            evidence_ids = list(candidate["evidence_ids"])
            if not 0 <= confidence <= 1:
                raise LLMContractError("Hypothesis confidence must be between 0 and 1")
            if not evidence_ids or not set(evidence_ids).issubset(allowed_ids):
                raise LLMContractError("Hypothesis cited an unknown or empty evidence ID")
            result.append(
                Hypothesis(
                    cause=str(candidate["cause"]),
                    confidence=confidence,
                    verdict=str(candidate["verdict"]),
                    evidence_ids=evidence_ids,
                    rationale=str(candidate["rationale"]),
                )
            )
        return sorted(result, key=lambda item: item.confidence, reverse=True)

