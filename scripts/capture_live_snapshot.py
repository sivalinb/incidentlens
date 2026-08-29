from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from incidentlens.live import LiveTelemetryClient


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture read-only local OpenTelemetry Demo telemetry")
    parser.add_argument("--service", required=True)
    parser.add_argument("--minutes", type=int, default=10)
    parser.add_argument("--metric-query", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    end_us = int(time.time() * 1_000_000)
    start_us = end_us - args.minutes * 60 * 1_000_000
    snapshot = LiveTelemetryClient().capture(args.service, args.metric_query, start_us, end_us)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

