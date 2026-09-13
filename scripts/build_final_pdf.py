from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "IncidentLens_Final_Step_by_Step_Guide.pdf"
NAVY = colors.HexColor("#0C2038")
TEAL = colors.HexColor("#008E70")
BLUE = colors.HexColor("#246BFE")
AMBER = colors.HexColor("#E6A400")
RED = colors.HexColor("#C83E45")
INK = colors.HexColor("#162536")
MUTED = colors.HexColor("#5E6D7C")
LIGHT = colors.HexColor("#F2F6F8")
PALE_TEAL = colors.HexColor("#E8F8F3")
PALE_BLUE = colors.HexColor("#EDF3FF")


def footer(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(colors.HexColor("#D9E3E8"))
    canvas.line(doc.leftMargin, 30, width - doc.rightMargin, 30)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 18, "IncidentLens - Completion and submission guide")
    canvas.drawRightString(width - doc.rightMargin, 18, f"Page {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverEyebrow", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=TEAL, spaceAfter=14, letterSpacing=1.2))
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=34, leading=37, textColor=NAVY, alignment=TA_LEFT, spaceAfter=16))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontSize=14, leading=20, textColor=MUTED, spaceAfter=20))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=NAVY, spaceBefore=2, spaceAfter=12))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=NAVY, spaceBefore=12, spaceAfter=7))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=9.3, leading=13.5, textColor=INK, spaceAfter=7))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontSize=7.7, leading=10.5, textColor=MUTED, spaceAfter=5))
styles.add(ParagraphStyle(name="Step", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=TEAL, spaceBefore=10, spaceAfter=3))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontSize=9, leading=13, textColor=INK, leftIndent=12, rightIndent=12, borderColor=TEAL, borderWidth=1, borderPadding=9, backColor=PALE_TEAL, spaceBefore=6, spaceAfter=10))
styles.add(ParagraphStyle(name="Warning", parent=styles["Callout"], borderColor=AMBER, backColor=colors.HexColor("#FFF8E7")))
styles.add(ParagraphStyle(name="CodeBlock", fontName="Courier", fontSize=7.2, leading=9.5, textColor=NAVY, spaceBefore=0, spaceAfter=0))
styles.add(ParagraphStyle(name="CenterSmall", parent=styles["Smallx"], alignment=TA_CENTER))


def p(text: str, style: str = "Bodyx") -> Paragraph:
    return Paragraph(text, styles[style])


def heading(text: str) -> list:
    return [p(text, "H1x"), HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=12)]


def h2(text: str) -> Paragraph:
    return p(text, "H2x")


def step(number: int, title: str, body: str) -> Table:
    result = Table(
        [[p(f"STEP {number:02d}", "Step")], [h2(title)], [p(body)]],
        colWidths=[515],
        hAlign="LEFT",
        splitByRow=0,
        splitInRow=0,
    )
    result.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return result


def code(text: str) -> Table:
    block = Preformatted(text.strip("\n"), styles["CodeBlock"])
    result = Table([[block]], colWidths=[515], hAlign="LEFT", splitByRow=0, splitInRow=0)
    result.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE_BLUE), ("BOX", (0, 0), (-1, -1), 0.7, BLUE), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return result


def table(data, widths, header=True, font_size=7.6):
    header_style = ParagraphStyle(name="_HeaderCell", fontName="Helvetica-Bold", fontSize=font_size, leading=font_size + 2, textColor=colors.white)
    cell_style = ParagraphStyle(name="_BodyCell", fontName="Helvetica", fontSize=font_size, leading=font_size + 2.4, textColor=INK)
    converted = []
    for row_index, row in enumerate(data):
        converted_row = []
        for cell in row:
            if hasattr(cell, "wrap"):
                converted_row.append(cell)
            else:
                converted_row.append(Paragraph(escape(str(cell)), header_style if header and row_index == 0 else cell_style))
        converted.append(converted_row)
    result = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CEDAE1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, LIGHT]),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    result.setStyle(TableStyle(commands))
    return result


def architecture_drawing() -> Drawing:
    drawing = Drawing(520, 220)
    labels = [
        (10, 150, 66, 36, "Alert", TEAL),
        (91, 150, 66, 36, "Metrics", BLUE),
        (172, 150, 66, 36, "Logs", BLUE),
        (253, 150, 66, 36, "Traces", BLUE),
        (334, 150, 76, 36, "Hypotheses", AMBER),
        (425, 150, 70, 36, "Critic", AMBER),
        (230, 60, 120, 42, "Human interrupt", RED),
    ]
    for x, y, w, h, label, color in labels:
        drawing.add(Rect(x, y, w, h, rx=7, ry=7, fillColor=color, strokeColor=color))
        drawing.add(String(x + w / 2, y + h / 2 - 3, label, textAnchor="middle", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    for x1, x2 in [(76, 91), (157, 172), (238, 253), (319, 334), (410, 425)]:
        drawing.add(Line(x1, 168, x2, 168, strokeColor=NAVY, strokeWidth=1.6))
    drawing.add(Line(460, 150, 350, 102, strokeColor=NAVY, strokeWidth=1.6))
    drawing.add(String(290, 125, "persist evidence and alternatives", textAnchor="middle", fontName="Helvetica", fontSize=7, fillColor=MUTED))
    drawing.add(String(290, 39, "approve -> verification plan only | reject -> stop safely", textAnchor="middle", fontName="Helvetica-Bold", fontSize=8, fillColor=NAVY))
    drawing.add(String(290, 17, "SQLite state + LangGraph checkpoint + append-only timeline", textAnchor="middle", fontName="Helvetica", fontSize=7.5, fillColor=MUTED))
    return drawing


def build() -> None:
    proof = json.loads((ROOT / "examples/output/langgraph-replay-state.json").read_text(encoding="utf-8"))
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=letter, rightMargin=42, leftMargin=42, topMargin=40, bottomMargin=42,
        title="IncidentLens Final Step-by-Step Guide", author="Sivalingan Babu",
    )
    story = []

    story += [Spacer(1, 0.55 * inch), p("MASTERING AGENTIC AI", "CoverEyebrow"), p("IncidentLens", "CoverTitle")]
    story += [p("Final completion report and step-by-step submission guide", "CoverSub")]
    story += [HRFlowable(width="100%", thickness=4, color=TEAL, spaceAfter=20)]
    story += [p("An evidence-first incident investigation agent that correlates metrics, logs, and traces, challenges its leading diagnosis, persists state, recovers from tool failure, and stops at a human approval boundary.", "CoverSub")]
    cover_data = [
        [p("PUBLIC DEMO", "Smallx"), p("https://incidentlens-demo.siva-babu.chatgpt.site", "Bodyx")],
        [p("REPOSITORY", "Smallx"), p("https://github.com/sivalinb/incidentlens", "Bodyx")],
        [p("VERIFIED", "Smallx"), p("25 Python tests, 5 website tests, 3/3 replay regressions", "Bodyx")],
        [p("FINAL STATE", "Smallx"), p("approved_pending_verification - no production write", "Bodyx")],
        [p("DATE", "Smallx"), p("August 29, 2026", "Bodyx")],
    ]
    cover = Table(cover_data, colWidths=[95, 385])
    cover.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#CEDAE1")), ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9E3E8")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story += [cover, Spacer(1, 16), p("IMPORTANT CREDIBILITY STATEMENT", "Step"), p("The checked-in proof uses deterministic replay and a deterministic evidence rubric. A real provider-backed model result remains explicitly pending until a credential is configured locally. Nothing in this package claims a production change was executed.", "Warning"), PageBreak()]

    story += heading("1. Executive outcome")
    story += [p("IncidentLens now contains a complete, runnable code base, real LangGraph orchestration, durable SQLite checkpointing, bounded telemetry recovery, strict model validation, read-only live capture adapters, a visual website source, CI, automated tests, proof artifacts, and submission documentation.")]
    status_rows = [
        ["Area", "Verified outcome", "Status"],
        ["Agent workflow", "Alert -> evidence -> hypotheses -> critic -> human gate", "Complete"],
        ["LangGraph", "SQLite checkpoint, interrupt, separate-process resume", "Complete"],
        ["Tool failure", "Injected Jaeger timeout, changed query, recovered retry", "Complete"],
        ["Safety", "Approval produces verification plan only", "Complete"],
        ["Tests", "25 Python + 5 website checks", "Passing"],
        ["Evaluation", "3/3 independent-label workflow regressions", "Passing"],
        ["Public demo", "Guided site reachable", "Complete"],
        ["Real model evidence", "Adapter and tests complete; credentialed run absent", "Pending credential"],
        ["Video and form", "Script and sequence complete", "User-owned action"],
    ]
    story += [table(status_rows, [105, 315, 95]), Spacer(1, 10), p("Do not describe the 3/3 result as generalized AI root-cause accuracy. It is a deterministic workflow regression covering evidence, state, failure recovery, and safety.", "Warning")]

    story += heading("2. Project requirement mapping")
    req_rows = [
        ["Assignment requirement", "IncidentLens evidence"],
        ["Multi-step task", "Scope, three telemetry agents, hypothesis generation, critic, approval, verification plan."],
        ["Decides what happens next", "Explicit graph edges, retry branches, stop conditions, approval and rejection transitions."],
        ["Calls tools", "Replay tools plus read-only Prometheus, OpenSearch, and Jaeger HTTP clients."],
        ["Holds state", "Typed incident state, SQLite incident store, LangGraph SQLite checkpointer."],
        ["Recovers from errors", "Timeout and empty-result classes; one bounded retry using a changed query."],
        ["Human-in-the-loop", "Dynamic interrupt after criticism and before a write-like plan."],
        ["Real workflow end to end", "Alert to evidence-backed plan, with no unapproved write."],
        ["Evaluation", "Independent labels, citations, multi-signal coverage, recovery, and unsafe-write checks."],
    ]
    story += [table(req_rows, [150, 365]), Spacer(1, 10), KeepTogether([p("Agent one-liner", "H2x"), p("IncidentLens helps on-call SREs investigate a multi-signal incident through a CLI and visual workbench, replacing manual switching among observability tools; it gathers and validates evidence from three tools, hands remediation to a human, and succeeds when it produces a cited diagnosis with bounded recovery and zero unapproved writes.", "Callout")])]

    story += heading("3. Architecture and data boundaries")
    story += [architecture_drawing(), Spacer(1, 4)]
    mode_rows = [
        ["Dimension", "Mode used by proof", "Other supported path"],
        ["Telemetry", "deterministic_replay", "live_local_capture"],
        ["Reasoning", "deterministic_rubric", "configured model"],
        ["Orchestration", "langgraph", "native_python"],
        ["Action", "simulation", "no autonomous production mode"],
    ]
    story += [table(mode_rows, [110, 180, 225]), h2("Answer-leakage prevention"), p("Operational JSON under incidentlens/scenarios contains the alert, metric points, log events, trace spans, and a proposed verification plan. Expected causes live separately under evaluation/labels. The investigator never reads those labels; only the evaluator does."), p("Replays are regression tests. Fresh telemetry is an integration test. The two lanes share an evidence contract but support different claims.", "Callout")]

    story += [PageBreak()]
    story += heading("4. Step-by-step local setup")
    story += [step(1, "Clone the repository", "Use a clean directory so the result proves that no hidden local files are required."), code("git clone https://github.com/sivalinb/incidentlens.git\ncd incidentlens")]
    story += [step(2, "Create an isolated Python environment", "Python 3.11 or newer is recommended. Install the optional LangGraph runtime because the strongest proof uses a real graph and SQLite checkpoint."), code("python3 -m venv .venv\nsource .venv/bin/activate\npip install -e '.[langgraph]'")]
    story += [step(3, "Run every automated gate", "Run both the Python behavior suite and the dependency-free website checks."), code("LANGGRAPH_STRICT_MSGPACK=true \\\n+  python -m unittest discover -s tests -p 'test*.py' -v\n\nnode --test website/tests/*.test.mjs\nincidentlens evaluate")]
    story += [p("Expected: 25 Python tests pass, five website checks pass, all three scenarios return top-1 and top-3 true, valid citation rate 1.0, three-signal evidence true, recovery true, and unsafe_write false.", "Callout")]

    story += heading("5. Step-by-step deterministic investigation")
    story += [step(1, "Start with an injected telemetry failure", "The injected first Jaeger attempt makes the non-happy path visible."), code("incidentlens investigate payment-unreachable --inject-failure")]
    story += [step(2, "Read the mode labels", "Confirm deterministic replay, deterministic rubric, native Python orchestration, and simulation action mode. These labels prevent the hosted experience from being mistaken for live model reasoning."), step(3, "Inspect the recovery ledger", "The first trace request times out. The second request adds operation and minimum-duration constraints, proving the retry is materially different."), step(4, "Inspect evidence and hypotheses", "M-01, L-01, and T-01 must exist. The leading cause cites all three. The critic weakens alternatives using counter-evidence."), step(5, "Stop at approval", "The expected status is awaiting_approval, approval is null, action is none, and no production write has occurred.")]

    story += [PageBreak()]
    story += heading("6. LangGraph interrupt and resume")
    story += [step(1, "Launch the real LangGraph engine", "This creates a SQLite graph checkpoint and pauses inside interrupt()."), code("incidentlens investigate payment-unreachable \\\n+  --engine langgraph \\\n+  --inject-failure")]
    story += [step(2, "Copy the incident ID", "The generated proof used a durable incident ID and reached awaiting_approval after collecting and criticizing evidence."), step(3, "Open a second process", "Resume the same graph thread from the SQLite checkpoint."), code("incidentlens resume IL-YOUR-ID \\\n+  --engine langgraph \\\n+  --approve \\\n+  --note 'Reviewed metric, log, and trace evidence'")]
    story += [step(4, "Verify the terminal state", "The only valid approved result is approved_pending_verification with final_action=verification_plan_only and Production write=none."), p(f"Checked-in proof state: incident {proof['incident_id']}; status {proof['status']}; recovered tool failures {len([x for x in proof['tool_failures'] if x['recovered']])}; approval {str(proof['approval']).lower()}; final action {proof['final_action']}.", "Callout"), PageBreak()]

    story += heading("7. Evidence and recovery walk-through")
    evidence_rows = [["ID", "Signal", "Finding", "Role in diagnosis"]]
    for item in proof["evidence"]:
        evidence_rows.append([item["id"], item["signal"], item["summary"], "Fact supplied to hypothesis engine and critic"])
    story += [table(evidence_rows, [38, 60, 270, 147], font_size=7.1), h2("Failure ledger"), p("Trace attempt 1 records a bounded Jaeger timeout. Attempt 2 changes from a broad service query to a narrower checkout operation with a 500 ms duration threshold and five-minute window. The failure remains in state with recovered=true."), h2("Critic result")]
    hypothesis_rows = [["Rank", "Cause", "Confidence", "Verdict", "Citations"]]
    for index, item in enumerate(proof["hypotheses"], start=1):
        hypothesis_rows.append([str(index), item["cause"], f"{item['confidence']:.0%}", item["verdict"], ", ".join(item["evidence_ids"])])
    story += [table(hypothesis_rows, [32, 220, 62, 70, 130], font_size=7.2), p("The successful payment health check is counter-evidence against a crashed payment process. The trace localizes the failed path, while the log explains the connection symptom and the metric establishes time and blast radius.", "Callout")]

    story += heading("8. Step-by-step real model path")
    story += [p("The model adapter is complete and contract-tested, but a genuine provider result cannot be created without a local credential. This guide intentionally refuses to relabel deterministic or mocked output as a real model run.", "Warning")]
    story += [step(1, "Configure credentials locally", "Do not paste keys into ChatGPT, source code, screenshots, the PDF, or GitHub."), code("export LLM_BASE_URL='https://YOUR_PROVIDER/v1'\nexport LLM_API_KEY='YOUR_LOCAL_SECRET'\nexport LLM_MODEL='YOUR_MODEL'")]
    story += [step(2, "Execute model reasoning through LangGraph", "Only the alert and collected evidence IDs/summaries are sent to the provider."), code("incidentlens investigate payment-unreachable \\\n+  --engine langgraph \\\n+  --use-llm \\\n+  --inject-failure")]
    story += [step(3, "Validate before claiming success", "Confirm exactly three hypotheses, confidence values from 0 to 1, valid evidence IDs, a critic pass, an interrupt payload, and no production write."), step(4, "Save the provenance artifact", "Record model name, execution timestamp, prompt evidence IDs, model JSON, validation result, approval event, and the explicit safety statement. Replace the pending manifest only after this genuine run.")]

    story += heading("9. Verification evidence")
    verification_rows = [
        ["Gate", "Verified result", "What it proves"],
        ["Python unittest", "25 passed", "Workflow, state, LangGraph, live client, LLM contract, safety"],
        ["Node test", "5 passed", "Website modes, units, flow, responsive layout"],
        ["Replay evaluation", "3/3 top-1 and top-3", "Independent-label deterministic regression"],
        ["Citation rate", "1.0", "Every hypothesis citation refers to collected evidence"],
        ["Tool recovery", "3/3", "Injected trace timeout recovered with changed query"],
        ["Unsafe writes", "0", "No action before or after approval exceeds verification planning"],
        ["LangGraph resume", "passed", "SQLite checkpoint restored in a second app instance"],
    ]
    story += [table(verification_rows, [105, 105, 305]), h2("Repeat the proof artifact"), code("LANGGRAPH_STRICT_MSGPACK=true python scripts/generate_proof.py"), p("Generated files: examples/output/langgraph-replay-run.md and examples/output/langgraph-replay-state.json.", "Callout")]

    story += heading("10. Public demo walk-through")
    demo_steps = [
        ("Guided demo", "Explain the healthy service path, telemetry clues, incident, agent investigation, critic, approval, and verification concepts one scene at a time."),
        ("Telemetry", "Show the metric chart, correlated log records, trace waterfall, and explicit replay disclosure."),
        ("IncidentLens analysis", "Run the investigation and show evidence objects, correlation, competing hypotheses, and critic review."),
        ("Agent flow", "Explain each handoff and shared-state update. Emphasize that read actions proceed automatically while write-like actions stop."),
        ("Data journey", "Contrast public OTel fault concepts, authored replay fixtures, live local capture, and evaluator-only labels."),
        ("Resources", "Use the code lab, architecture, and teaching sections for an interview or class explanation."),
    ]
    for index, (title, body) in enumerate(demo_steps, start=1):
        story += [step(index, title, body)]
    story += [p("Public URL: https://incidentlens-demo.siva-babu.chatgpt.site", "Callout")]

    story += heading("11. Five-minute presentation plan")
    video_rows = [
        ["Time", "Show", "Message"],
        ["0:00-0:35", "Problem", "SREs lose time switching tools; IncidentLens builds one evidence ledger."],
        ["0:35-1:15", "Telemetry", "Metrics show when/how much, logs show what, traces show where."],
        ["1:15-2:20", "LangGraph CLI", "Real graph, injected timeout, changed retry, cited alternatives."],
        ["2:20-3:05", "Second terminal", "SQLite checkpoint resumes the same human interrupt."],
        ["3:05-3:45", "Fixture and label files", "The agent does not see evaluator answers."],
        ["3:45-4:25", "Tests", "25 Python, five site checks, 3/3 deterministic regression."],
        ["4:25-4:50", "Limitations", "Replay is not live; deterministic reasoning is not a real model result."],
        ["4:50-5:00", "Close", "Observability + orchestration + state + safety + evaluation."],
    ]
    story += [table(video_rows, [65, 105, 345], font_size=7.3), p("Recommended sentence: 'The hosted experience uses deterministic replay data modeled on public OpenTelemetry Demo fault concepts. The local client can capture fresh telemetry, and the real provider path is explicitly pending until a credentialed run is produced.'", "Callout")]

    story += heading("12. GitHub and final submission sequence")
    story += [step(1, "Review repository status", "Confirm no credentials, databases, virtual environments, build output, or caches are staged."), code("git status\ngit add .\ngit status")]
    story += [step(2, "Commit and push", "Use the personal repository and main branch."), code("git commit -m 'feat: publish IncidentLens evidence-first agent'\ngit push -u origin main")]
    story += [PageBreak(), step(3, "Verify from a clean clone", "Install the optional graph runtime and rerun Python, Node, and replay evaluation gates."), code("git clone https://github.com/sivalinb/incidentlens.git clean-check\ncd clean-check\npython3 -m venv .venv && source .venv/bin/activate\npip install -e '.[langgraph]'\npython -m unittest discover -s tests -p 'test*.py' -v\nnode --test website/tests/*.test.mjs\nincidentlens evaluate")]
    story += [step(4, "Create the project document", "Upload this PDF or copy its content into a shared Google Doc. Add the final GitHub, public demo, and video URLs."), step(5, "Record and upload the video", "Use the five-minute plan on the prior page. Keep credentials and local secrets off screen."), step(6, "Submit the form", "Provide the documentation, video, and code-base links at https://forms.gle/HMgTU7zy6UJ8XkJX6."), p("Project award deadline: August 30, 2026. Final certification deadline: September 16, 2026.", "Warning")]

    story += [PageBreak()]
    story += heading("13. Final readiness verdict")
    story += [p("IncidentLens is technically complete as a defensible deterministic agentic observability project. The repository demonstrates real LangGraph control flow, durable interrupt/resume, bounded recovery, explicit data provenance, evidence criticism, and a meaningful human safety boundary."), p("Completed", "H2x")]
    complete_rows = [
        ["Code and repository documentation", "Complete"],
        ["Native and LangGraph engines", "Complete"],
        ["Evidence/label separation", "Complete"],
        ["Replay, live, model, and action disclosures", "Complete"],
        ["Automated tests and generated proof", "Complete"],
        ["Public guided demo", "Complete"],
    ]
    completed_table = table(complete_rows, [350, 165], header=False)
    story += [completed_table, p("Remaining human/account actions", "H2x")]
    remaining_rows = [
        ["Credentialed model invocation", "Configure provider locally and save genuine provenance"],
        ["Video recording", "Record and upload using the prepared five-minute script"],
        ["Google Doc / sharing", "Upload this PDF or copy it into a shared document"],
        ["Submission form", "Enter the final three URLs"],
    ]
    story += [table(remaining_rows, [180, 335], header=False), Spacer(1, 12), p("The correct final claim is: IncidentLens is a fully tested agentic workflow and portfolio demonstration with a deterministic replay benchmark, a real LangGraph persistence proof, a read-only live telemetry path, and a strict but not-yet-credentialed model path.", "Callout")]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
