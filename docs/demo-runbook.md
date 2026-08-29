# IncidentLens demo runbook

This is the operator flow for a reliable five-minute submission demo. The spoken narration is in `docs/video-script.md`.

## 1. Preflight

Open these before recording:

1. GitHub: `https://github.com/sivalinb/incidentlens`
2. Guided demo: `https://incidentlens-demo.siva-babu.chatgpt.site`
3. Terminal A at the repository root
4. Terminal B at the repository root

Activate the installed environment in both terminals:

```bash
cd /path/to/incidentlens
source .venv/bin/activate
```

Confirm the commands are ready:

```bash
incidentlens --help
python --version
node --version
```

## 2. Generate the paused investigation

In Terminal A:

```bash
incidentlens --db .incidentlens/demo.db investigate payment-unreachable \
  --engine langgraph --inject-failure
```

Visible checkpoints to call out:

- `Orchestrator         langgraph`
- `Recovery             narrow query; retry succeeded`
- `Evidence             M-01, L-01, T-01`
- `State                awaiting_approval`
- `Action               none`
- `Production write     none`

Copy the `IL-...` incident ID.

## 3. Walk through the visual evidence

On the guided demo:

1. **Telemetry:** show metric, log, and trace agreement.
2. **Analysis:** show the leading hypothesis and counter-evidence.
3. **Agent flow:** show each tool and the critic-to-human handoff.
4. **Human gate:** emphasize that approval prepares a verification plan only.

## 4. Resume the durable checkpoint

In Terminal B, replace `IL-YOUR-ID` with the copied ID:

```bash
incidentlens --db .incidentlens/demo.db resume IL-YOUR-ID \
  --engine langgraph --approve \
  --note "Reviewed metric, log, and trace evidence"
```

Visible checkpoints:

- The incident ID matches Terminal A.
- `State` becomes `approved_pending_verification`.
- `Action` becomes `verification_plan_only`.
- `Production write` remains `none`.

## 5. Show evaluator independence and automated proof

Open the evidence fixture and evaluator label side by side:

- `incidentlens/scenarios/payment-unreachable.json`
- `evaluation/labels/payment-unreachable.json`

Then show the final summaries from:

```bash
LANGGRAPH_STRICT_MSGPACK=true \
  python -m unittest discover -s tests -p 'test*.py' -v
node --test website/tests/*.test.mjs
incidentlens evaluate
```

Expected totals: 29 Python tests, 6 website tests, and 3/3 passing replay evaluations.

## 6. Fallbacks

### Hosted demo unavailable

```bash
python -m http.server 8080 --directory website
```

Open `http://127.0.0.1:8080`.

### Terminal run unavailable

Show these checked-in artifacts:

- `examples/output/langgraph-replay-run.md`
- `examples/output/langgraph-replay-state.json`

### Time is running short

Keep the proof sequence: three signals -> changed retry -> ranked alternatives -> human interrupt -> second-process resume -> no production write. Skip the longer code tour.

## 7. Final claim boundary

Say:

> IncidentLens is a fully tested agentic workflow and portfolio demonstration with a deterministic replay benchmark, real LangGraph persistence, a read-only live telemetry path, and a strict but not-yet-credentialed model path.

Do not claim autonomous remediation, a fixed production incident, broad model accuracy, or fresh telemetry in the hosted replay.
