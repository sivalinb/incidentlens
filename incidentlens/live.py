from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen


JsonTransport = Callable[[Request], dict[str, Any]]


def default_transport(request: Request) -> dict[str, Any]:
    with urlopen(request, timeout=30) as response:  # nosec: endpoints are explicitly user-configured
        return json.loads(response.read().decode("utf-8"))


class LiveTelemetryClient:
    """Read-only client for a locally running OpenTelemetry Demo stack."""

    def __init__(
        self,
        prometheus_url: str = "http://localhost:9090",
        opensearch_url: str = "http://localhost:9200",
        jaeger_url: str = "http://localhost:16686",
        transport: JsonTransport = default_transport,
    ) -> None:
        self.prometheus_url = prometheus_url.rstrip("/")
        self.opensearch_url = opensearch_url.rstrip("/")
        self.jaeger_url = jaeger_url.rstrip("/")
        self.transport = transport

    def capture(self, service: str, metric_query: str, start_us: int, end_us: int) -> dict[str, Any]:
        metric_request = Request(f"{self.prometheus_url}/api/v1/query?{urlencode({'query': metric_query})}")
        log_body = json.dumps(
            {"size": 100, "query": {"bool": {"filter": [{"term": {"service.name": service}}]}}}
        ).encode()
        log_request = Request(
            f"{self.opensearch_url}/*/_search",
            data=log_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        trace_request = Request(
            f"{self.jaeger_url}/api/traces?{urlencode({'service': service, 'start': start_us, 'end': end_us, 'limit': 20})}"
        )
        return {
            "source": "OpenTelemetry Astronomy Shop local deployment",
            "telemetry_mode": "live_local_capture",
            "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "service": service,
            "window": {"start_us": start_us, "end_us": end_us},
            "metrics": self.transport(metric_request),
            "logs": self.transport(log_request),
            "traces": self.transport(trace_request),
            "read_only": True,
        }

