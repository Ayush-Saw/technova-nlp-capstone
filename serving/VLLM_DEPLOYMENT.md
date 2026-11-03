# Optional vLLM serving

Run a compatible open-weight instruct model on a GPU host, for example:

```bash
vllm serve <approved-model-id> --host 0.0.0.0 --port 8001 --api-key "$VLLM_API_KEY"
```

Pin model revision and licence. Add a gateway adapter that calls the OpenAI-compatible `/v1/chat/completions` endpoint, passes only ACL-filtered context, validates output and records model version. This repository's extractive RAG and rule-based triage are development fallbacks, not substitutes for a measured vLLM deployment.
