# IncidentLens five-minute submission video script

Target length: 4:40-4:55. Record at 1080p with the terminal font large enough to read. Keep the GitHub repository, guided demo, and two terminal windows open before recording.

## 0:00-0:25 - Hook and project definition

**Screen:** GitHub README, with the one-line agent definition visible.

**Say:**

> On-call engineers lose time switching among metrics, logs, and traces, and an early guess can turn into a risky production change. IncidentLens is an evidence-first investigation agent. It gathers three telemetry signals, ranks and criticizes competing causes, survives a tool failure, persists the case, and interrupts for human approval before any write-like action.

## 0:25-1:05 - Show the incident evidence

**Screen:** Open the guided demo and select **Payment service unreachable**. Stay on **Telemetry**.

**Say:**

> This hosted experience is explicitly a deterministic replay, not live production data. The checkout error rate rises from point six percent to twenty-eight point two percent. Correlated logs show a refused payment connection while the payment health check is still successful. The trace localizes the failed path from checkout to payment. Each signal receives a stable evidence ID: M-01, L-01, and T-01.

## 1:05-1:50 - Run the real LangGraph workflow

**Screen:** Terminal A. Run:

```bash
incidentlens --db .incidentlens/demo.db investigate payment-unreachable \
  --engine langgraph --inject-failure
```

**Say while the output is visible:**

> This is the real LangGraph path with a durable SQLite checkpointer. I deliberately inject a timeout into the first Jaeger query. The agent records the failure, narrows the query to the checkout operation and a shorter time window, retries once, and succeeds. It then ranks three alternatives. The leading cause is an invalid payment-service address, supported by all three evidence IDs.

Copy the displayed incident ID for the next step.

## 1:50-2:35 - Explain criticism and the safety boundary

**Screen:** Guided demo **Analysis**, then **Agent flow**, then **Human gate**.

**Say:**

> The critic rejects unknown citations and requires counter-evidence. Here, a successful payment health check weakens the theory that the payment process crashed. The workflow reaches awaiting approval with action set to none. The recommendation says what could be restored and how to verify it, but its production-write flag is false. IncidentLens approves a verification plan, not an autonomous change.

## 2:35-3:15 - Resume from another process

**Screen:** Terminal B. Replace the incident ID and run:

```bash
incidentlens --db .incidentlens/demo.db resume IL-YOUR-ID \
  --engine langgraph --approve \
  --note "Reviewed metric, log, and trace evidence"
```

**Say:**

> This is a second process resuming the same persisted checkpoint. The final state is approved pending verification, the only action is verification-plan-only, and production write remains none. A rejection path also stops safely, and a second decision is rejected as an invalid state transition.

## 3:15-3:50 - Prove evaluation separation

**Screen:** Show `incidentlens/scenarios/payment-unreachable.json`, then `evaluation/labels/payment-unreachable.json`.

**Say:**

> Operational fixtures contain only alerts and telemetry. Expected causes live in a separate evaluator-only directory. The investigator cannot read those labels. Across all three curated regressions, the independent evaluator reports top-one and top-three correct, one hundred percent valid citations, multi-signal evidence, recovered tool failure, and no unsafe write.

## 3:50-4:25 - Show automated verification

**Screen:** Terminal with the final test summary. Run these before recording so the results are already available:

```bash
LANGGRAPH_STRICT_MSGPACK=true \
  python -m unittest discover -s tests -p 'test*.py' -v
node --test website/tests/*.test.mjs
incidentlens evaluate
```

**Say:**

> Twenty-nine Python tests and six website tests pass. They include subprocess CLI runs, cross-process LangGraph resume, persistence, approval and rejection, failure recovery, the strict model-response contract, read-only live-client request shapes, and interactive website behavior. All three replay evaluations also pass.

## 4:25-4:45 - State the limitations honestly

**Screen:** README **Honest execution modes** table.

**Say:**

> The checked-in proof uses deterministic replay and deterministic reasoning. A read-only client can capture local Prometheus, OpenSearch, and Jaeger responses. The OpenAI-compatible reasoning adapter is contract-tested, but a provider-backed run remains explicitly pending until a real credential is configured locally.

## 4:45-4:55 - Close

**Screen:** GitHub repository header or guided demo title.

**Say:**

> IncidentLens demonstrates the complete agent loop: tool use, durable state, bounded recovery, evidence criticism, measurable evaluation, and a meaningful human safety gate. The repository, demo, tests, and submission documentation are linked with this project.

## Recording notes

- Never show API keys, tokens, local credential files, or browser credential screens.
- Do not say the incident was fixed or closed; say the plan is **approved pending verification**.
- Do not describe replay data as fresh production telemetry.
- If the live CLI stalls, switch to `examples/output/langgraph-replay-run.md` and narrate the checked-in proof.
- If the hosted demo is unavailable, serve `website/` locally using the fallback in `docs/demo-runbook.md`.
