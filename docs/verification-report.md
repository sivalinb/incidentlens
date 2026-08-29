# End-to-end verification report

Verification date: 2026-08-29

## Environment

- Clean repository-local virtual environment
- Python 3.12.13
- Node.js 25.1.0 for local verification; CI targets Node.js 20
- Latest compatible `langgraph>=1.0,<2` and `langgraph-checkpoint-sqlite>=3.0,<4`
- `LANGGRAPH_STRICT_MSGPACK=true` for the Python suite

## Automated results

| Gate | Result | Coverage |
|---|---:|---|
| Python unittest | 29 passed | Domain workflow, persistence, LangGraph, CLI subprocesses, live clients, LLM contract, safety |
| Node test | 6 passed | Labels, units, layout contract, scenario rendering, tabs, safe approval interaction |
| Replay evaluation | 3/3 passed | Top-1, top-3, citation rate, multi-signal evidence, recovery, unsafe-write check |
| Python compile | Passed | `incidentlens/`, `scripts/`, and `tests/` |
| Static HTTP smoke | Passed | `/`, `app.js`, and `styles.css` returned HTTP 200 with correct content types |

## Manual end-to-end results

### Native workflow

The packaged `incidentlens` command investigated `payment-unreachable` with an injected trace failure, persisted `awaiting_approval`, recorded the recovered timeout, and resumed by incident ID to `approved_pending_verification`. The final action was `verification_plan_only`; no production write occurred.

### LangGraph workflow

Invocation one created a SQLite checkpoint, recovered from the first Jaeger timeout with a changed query, and interrupted at the human gate. Invocation two ran as a separate command process, resumed the same incident ID, stored the reviewer note, and finalized the verification-only plan.

### All scenarios

`email-memory-leak`, `kafka-queue-lag`, and `payment-unreachable` each returned:

- top-1 correct: true
- top-3 correct: true
- valid citation rate: 1.0
- multi-signal evidence: true
- tool recovery: true
- unsafe write: false

## Defect fixed during verification

The inline command `investigate --engine langgraph --approve` previously updated the incident store through the native decision path instead of resuming the LangGraph checkpoint. It now resumes and finalizes the actual checkpoint. A subprocess regression test protects the corrected behavior.

The evaluator command now treats any citation rate below 1.0 as a failing exit condition.

## Honest limitations

- Replay evidence is curated and deterministic.
- The live telemetry client is read-only and was contract-tested with controlled transports; no local OpenTelemetry stack was supplied for this run.
- A real provider-backed model call was not attempted because no model credential was in scope.
- Three scenarios are regression fixtures, not a representative production benchmark.
