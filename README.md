# TechNova NLP Production Pipeline

End-to-end capstone: RAG documentation assistant + structured support-ticket triage.

## Quick start (CPU-friendly development mode)
1. Install Docker Desktop and Python 3.11+.
2. Copy `.env.example` to `.env` and set `API_KEY`.
3. Run `docker compose up --build`.
4. Open API docs at http://localhost:8000/docs and Grafana at http://localhost:3000.

The local development profile uses Qdrant, MLflow and the FastAPI gateway. The default triage backend is a deterministic schema-safe baseline so the stack can be tested without downloading a multi-GB model. Set `TRIAGE_BACKEND=transformers` and configure a permitted model to use a local Hugging Face model. vLLM deployment is provided as an optional profile because it generally requires a compatible GPU.

## API
- `POST /v1/qa` JSON: `{"question":"How do I reset my password?","user_role":"public"}`
- `POST /v1/triage` JSON: `{"ticket":"Login fails after password reset"}`
- `GET /health`
- `GET /metrics`

Send `X-API-Key: <API_KEY>`. Roles: `public`, `staff`, `admin`. Document ACL is filtered before context reaches the model.

## Ingest documentation
Put `.md` and `.txt` files under `data/docs/`. Each file may begin with YAML front matter:
```yaml
---
title: Password reset
access_level: public
product_area: Identity
---
```
Then run:
`docker compose exec api python -m ingest.run --source data/docs`

For real-world ingestion, add licensed documentation sources and preserve their original licence/terms. The included sample docs are synthetic.

## Training workflow
- Prepare labelled ticket JSONL at `data/training/triage_sft.jsonl`.
- Prepare preference pairs at `data/training/triage_preferences.jsonl`.
- Run scripts in `training/` on a CUDA machine with sufficient VRAM.
- QLoRA and DPO are resource-intensive. The scripts are templates; validate model compatibility, GPU memory, quantization support and TRL API version before a full run.
- Do not claim the 500-pair or quality acceptance thresholds until your actual dataset and runs establish them.

## Evaluation
`python -m evals.run --data evals/data/qa_eval.jsonl`
`pytest -q`
Metrics include retrieval recall@k, answer faithfulness proxy, triage macro-F1, JSON validity and paired bootstrap confidence intervals for judge comparisons. A real LLM judge must be configured for semantic pairwise judging; the included harness supports a deterministic baseline.

## MLOps
- DVC: `dvc init`, then `dvc add data/docs data/training`.
- MLflow: http://localhost:5000
- Registry aliases: `champion` and `challenger` are managed through MLflow Model Registry APIs in `training/registry.py`.
- GitHub Actions runs tests and evaluation regression checks. Promotion is blocked when thresholds regress.
- Prometheus metrics endpoint: `/metrics`; Grafana: http://localhost:3000.

## Security notes
Use HTTPS and a real identity provider in production. Rotate secrets. Scrub PII before training and logging. Run containers non-root. Do not expose Qdrant or MLflow publicly. Retrieved text and user prompts are untrusted. ACL filtering is enforced in retrieval, not delegated to the LLM.

## Model/data licences
This repository ships synthetic example documentation and tiny synthetic evaluation examples only. No pretrained weights are bundled. Select an open-weight model whose licence permits your use, record its exact revision, licence and usage restrictions in `MODEL_CARD.md`, and separately record dataset provenance/licences in `DATA_CARD.md`.

## Limitations
The baseline implementation is a runnable engineering scaffold, not proof of the acceptance metrics. The 500+ page ingestion, 500+ preference pairs, QLoRA/DPO training, GPU serving, load test, red-team report and demo recording must be completed and measured on your target environment.
