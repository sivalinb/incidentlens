from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import Evidence


class TelemetryToolError(RuntimeError):
    """Base class for telemetry failures."""


class TransientToolError(TelemetryToolError):
    """A retryable backend timeout or availability failure."""


class EmptyToolResult(TelemetryToolError):
    """A successful query that returned no usable evidence."""


class ReplayTelemetryTools:
    """Read-only tools over a deterministic scenario fixture."""

    def __init__(self, inject_failure: bool = False) -> None:
        self.inject_failure = inject_failure

    def collect(self, scenario: dict[str, Any], signal: str, attempt: int) -> Evidence:
        if signal not in {"metrics", "logs", "trace"}:
            raise ValueError(f"Unsupported signal: {signal}")
        if self.inject_failure and signal == "trace" and attempt == 1:
            raise TransientToolError("Jaeger request timed out after the bounded query window")

        payload = deepcopy(scenario[signal])
        query = payload["query"]
        if signal == "trace" and attempt > 1:
            query = payload.get("retry_query", query)
        raw = {key: value for key, value in payload.items() if key not in {"id", "source", "query", "retry_query", "summary"}}
        if not raw:
            raise EmptyToolResult(f"{signal} query returned no usable fields")
        return Evidence(
            id=payload["id"],
            signal="traces" if signal == "trace" else signal,
            source=payload["source"],
            query=query,
            summary=payload["summary"],
            raw=raw,
        )

