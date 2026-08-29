# Real provider-backed model run - pending local credential

This file intentionally does not contain fabricated model evidence.

The repository includes a strict OpenAI-compatible hypothesis adapter and mocked contract tests. To create a genuine result, configure the provider locally, run the command below, and save the returned model name, timestamp, evidence IDs, model JSON, validation result, approval event, and safety statement.

```bash
export LLM_BASE_URL="https://YOUR_PROVIDER/v1"
export LLM_API_KEY="YOUR_LOCAL_SECRET"
export LLM_MODEL="YOUR_MODEL"

incidentlens investigate payment-unreachable \
  --engine langgraph \
  --use-llm \
  --inject-failure
```

Never commit the API key. A deterministic or mocked response must not be labeled as a real model run.

