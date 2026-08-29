from __future__ import annotations

import argparse
from pathlib import Path

from .report import render_json, render_text
from .workflow import IncidentLensApp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="incidentlens", description="Evidence-first incident investigation")
    parser.add_argument("--db", default=".incidentlens/incidents.db", help="SQLite incident store")
    sub = parser.add_subparsers(dest="command", required=True)

    investigate = sub.add_parser("investigate", help="Run an investigation")
    investigate.add_argument("scenario")
    investigate.add_argument("--engine", choices=("native", "langgraph"), default="native")
    investigate.add_argument("--use-llm", action="store_true")
    investigate.add_argument("--inject-failure", action="store_true")
    investigate.add_argument("--approve", action="store_true")
    investigate.add_argument("--json", action="store_true")

    resume = sub.add_parser("resume", help="Resolve a persisted human gate")
    resume.add_argument("incident_id")
    resume.add_argument("--engine", choices=("native", "langgraph"), default="native")
    decision = resume.add_mutually_exclusive_group(required=True)
    decision.add_argument("--approve", action="store_true")
    decision.add_argument("--reject", action="store_true")
    resume.add_argument("--note", default="")
    resume.add_argument("--json", action="store_true")

    evaluate = sub.add_parser("evaluate", help="Evaluate all deterministic scenarios")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    app = IncidentLensApp(Path(args.db))
    if args.command == "investigate":
        state = app.investigate(
            args.scenario,
            inject_failure=args.inject_failure,
            use_llm=args.use_llm,
            engine=args.engine,
        )
        if args.approve:
            state = app.decide(state.incident_id, True, "Approved from investigate command")
        print(render_json(state) if args.json else render_text(state))
        return 0
    if args.command == "resume":
        if args.engine == "langgraph":
            from .langgraph_adapter import resume_graph

            state = resume_graph(app, args.incident_id, args.approve, args.note)
        else:
            state = app.decide(args.incident_id, args.approve, args.note)
        print(render_json(state) if args.json else render_text(state))
        return 0
    if args.command == "evaluate":
        failed = False
        for item in app.catalog.list():
            state = app.investigate(item["id"], inject_failure=True)
            result = app.evaluate(state)
            failed = failed or not all(
                result[key] for key in ("top_1_correct", "top_3_correct", "multisignal_evidence", "tool_recovery")
            ) or result["unsafe_write"]
            print(f"{item['id']}: {result}")
        return 1 if failed else 0
    return 2
