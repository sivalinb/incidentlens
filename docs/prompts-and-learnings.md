# Prompts, iterations, and learnings

## Representative build prompts

1. Design an evidence-first incident investigator that correlates metrics, logs, and traces and challenges its leading cause.
2. Add bounded recovery so a telemetry timeout changes the query and records the failed attempt.
3. Separate operational evidence from evaluator-only labels to prevent answer leakage.
4. Use LangGraph with durable SQLite checkpointing and interrupt/resume for human approval.
5. Make every screen disclose telemetry, reasoning, orchestration, and action modes.
6. Build tests that can reject unsafe-write, citation, persistence, and model-contract claims.

## Major iterations

- Began with deterministic scenarios so evaluation remained stable and credential-free.
- Replaced normalized chart coordinates with timestamped values and real units.
- Moved expected causes out of the operational fixtures.
- Converted vague error handling into two explicit failure classes and a bounded changed-query retry.
- Changed "incident closed" semantics to "approved pending verification."
- Added a strict optional model boundary instead of treating deterministic hypotheses as model output.
- Added durable LangGraph checkpoints and verified resume from a separate application instance.

## Learnings

- State and transitions matter more than prompt cleverness in an operational agent.
- An error should become auditable run evidence, not disappear behind an automatic retry.
- Facts, hypotheses, and evaluator labels require separate data boundaries.
- Human approval is meaningful only when the system can prove nothing was written beforehand.
- Replays are regression tests; live telemetry is an integration test. Both are valuable, but they support different claims.

