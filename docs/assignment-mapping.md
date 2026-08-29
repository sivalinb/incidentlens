# Week 3 assignment mapping

## Agent framework

| Field | IncidentLens answer |
|---|---|
| Agent goal | Produce an evidence-cited diagnosis and a safe verification plan. |
| Surface | CLI, public guided demo, and repository-local static workbench. |
| Ordered steps | Scope, metrics, logs, traces, hypotheses, critic, human gate, verification plan. |
| Tools | Replay evidence tools plus read-only Prometheus, OpenSearch, and Jaeger clients. |
| Memory | Incident identity, alert, evidence, retries, hypotheses, recommendation, approval, and timeline in SQLite. |
| Never do | Invent evidence, retry indefinitely, expose credentials, or execute production changes autonomously. |
| Human-in-the-loop | After evidence and criticism, before any write-like remediation. |
| Failure behavior | Retry a recoverable timeout once with a different query; persist and stop after bounded exhaustion. |
| Success measure | Valid cited diagnosis, all three signal types, successful bounded recovery, and zero unsafe writes. |

## Deliverable status

| Deliverable | Status |
|---|---|
| Working code | Complete in this repository |
| Tests and proof | Complete; generated replay proof included |
| Public visual demo | Available at https://incidentlens-demo.siva-babu.chatgpt.site |
| GitHub repository | Created/published during final handoff if authentication permits |
| Five-minute video | Script prepared; recording remains an account/user action |
| Google Doc | This documentation and final PDF are ready to copy/upload |
| Real provider-backed model result | Pending a locally configured provider credential; never fabricated |
| Submission form | Requires the final GitHub, document, and video URLs |

## Evidence boundary

The deterministic evaluation is a workflow regression test. It validates state, failure recovery, citation hygiene, and safety. It must not be described as generalized AI root-cause accuracy.

