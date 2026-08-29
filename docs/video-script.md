# Five-minute demo script

## 0:00-0:35 - Problem and promise

"SREs lose time switching between metric, log, and trace tools. IncidentLens creates one evidence ledger, challenges its own diagnosis, and pauses before any operational change."

## 0:35-1:15 - Telemetry story

Open the public demo. Select Payment service unreachable. Show the 28.2 percent error rate, the connection-refused log with trace ID, and the checkout-to-payment trace failure.

## 1:15-2:20 - Real LangGraph run

Run:

```bash
incidentlens investigate payment-unreachable --engine langgraph --inject-failure
```

Point out deterministic replay, LangGraph orchestration, the first Jaeger timeout, narrower retry, evidence IDs, ranked alternatives, and `awaiting_approval`.

## 2:20-3:05 - Persistence and human gate

Open a new terminal and run:

```bash
incidentlens resume IL-YOUR-ID --engine langgraph --approve --note "Evidence reviewed"
```

Explain that the second process resumes the same SQLite checkpoint. Emphasize `approved_pending_verification` and `Production write: none`.

## 3:05-3:45 - Critic and evaluator separation

Show `incidentlens/scenarios/payment-unreachable.json` and `evaluation/labels/payment-unreachable.json`. Explain that the agent sees telemetry but not the expected answer. Show the critic's citation validation.

## 3:45-4:25 - Automated proof

Run the Python and Node test commands. Mention LangGraph interrupt/resume, model-contract rejection, live-client request shapes, and site honesty labels.

## 4:25-4:50 - Provenance and limitations

Say: "The hosted experience uses deterministic replay data modeled on public OpenTelemetry Demo fault concepts. The local client can capture fresh Prometheus, OpenSearch, and Jaeger responses. This demonstration uses deterministic reasoning; a real provider-backed result is intentionally marked pending until credentials are configured locally."

## 4:50-5:00 - Close

Connect observability, agent control flow, durable state, failure recovery, evidence criticism, and human safety as the portfolio value.

