# IncidentLens submission checklist

## Required links

- Code: `https://github.com/sivalinb/incidentlens`
- Guided demo: `https://incidentlens-demo.siva-babu.chatgpt.site`
- Documentation: upload `IncidentLens_Final_Step_by_Step_Guide.pdf` or place it in the shared project document
- Video: add the final unlisted or public recording URL

## Suggested submission title

**IncidentLens - Evidence-first incident investigation with durable human approval**

## Suggested short description

IncidentLens is a multi-step SRE investigation agent that correlates Prometheus metrics, OpenSearch logs, and Jaeger traces; ranks and criticizes competing root-cause hypotheses; recovers from a bounded telemetry timeout; persists state through LangGraph and SQLite; and interrupts for human approval before any write-like action. Its deterministic benchmark separates operational evidence from evaluator labels and verifies citations, multi-signal coverage, recovery, and zero unsafe writes.

## Evidence to include

- Screenshot or clip showing `awaiting_approval`
- The injected Jaeger timeout followed by the changed narrower query
- Evidence IDs M-01, L-01, and T-01 on the leading hypothesis
- A second terminal resuming the same incident ID
- Final state `approved_pending_verification`
- `Production write     none`
- Test totals: 29 Python, 6 website, and 3/3 deterministic regressions

## Final checks before submitting

- [ ] GitHub repository opens without authentication.
- [ ] README quick-start commands work in a clean Python 3.11+ environment.
- [ ] GitHub Actions is green on `main`.
- [ ] Guided demo loads and all four tabs work.
- [ ] Video is no longer than five minutes.
- [ ] Terminal text is readable at normal playback size.
- [ ] No API key, personal access token, email, or credential screen appears.
- [ ] Video says replay, simulation, and approved pending verification.
- [ ] Documentation, video, demo, and code URLs have view access.
- [ ] The form entry uses the suggested accurate claim boundary.

## Claims to avoid

- Do not call the hosted replay live production telemetry.
- Do not claim a provider-backed model run until one is performed with a real local credential.
- Do not say approval executed remediation or closed the incident.
- Do not generalize three curated regressions into broad production accuracy.
