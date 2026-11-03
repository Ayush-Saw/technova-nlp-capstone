# Triage model card
- Model name/version: fill after training and registry registration.
- Base model: choose an open-weight model; record exact revision and licence.
- Method: QLoRA supervised fine-tuning followed by DPO preference alignment.
- Training data: synthetic starter examples only in this repository; replace with consented, PII-scrubbed and licensed ticket data.
- Intended use: assist support agents with routing and prioritisation, not make irreversible customer decisions.
- Evaluation: populate macro-F1, JSON validity, confidence intervals and baseline comparisons from actual runs.
- Limitations: domain shift, label ambiguity, hallucinated summaries, language coverage and class imbalance.
- Human oversight: required for critical/security/privacy tickets.
