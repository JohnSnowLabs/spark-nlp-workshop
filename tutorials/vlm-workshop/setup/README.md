# JSL Medical Document Understanding — Deployment Guide

Deploy the models and services used in the JSL Medical Document Understanding demo notebooks.

## What You Need

| Credential | Where to get it | Used for |
|-----------|----------------|----------|
| `SPARK_NLP_LICENSE` | Your JSL license JSON (`LICENSE` field) | VLM + Spark NLP license validation |
| `SECRET` | Your JSL license JSON (`SECRET` field) | PyPI access for JSL packages |
| `AWS_ACCESS_KEY_ID` | Your JSL license JSON | Model downloads from JSL S3 |
| `AWS_SECRET_ACCESS_KEY` | Your JSL license JSON | Model downloads from JSL S3 |

All four values come from your **John Snow Labs license file** (`license.json`).

## Models

### VLM Models (Vision Language Models)

Served via vLLM with OpenAI-compatible API (`/v1/chat/completions`).

| Model Name | Parameters | VRAM | Use Case | GPU |
|-----------|-----------|------|----------|-----|
| `jsl_vision_ocr_parsing_1_0` | 1B | ~3 GB | OCR (handwriting, printed text) | Any |
| `jsl_meds_vl_8b` | 8B | ~18 GB | Medical document understanding | A10G / L4 / L40S |
| `jsl_medm_vl_30b` | 30B (3B active, MoE) | ~20 GB | High-accuracy medical VLM | A10G / L4 / L40S |
| `jsl_vision_ocr_structured_fp8_1_0` | 32B (FP8) | ~34 GB | Structured extraction (tables, forms) | A100 / H100 / L40S |

### Text LLM Models

| Model Name | Parameters | VRAM | Use Case | GPU |
|-----------|-----------|------|----------|-----|
| `jsl_meds_8b` | 8B | ~18 GB | Medical text generation/reasoning | A10G / L4 / L40S |
| `jsl_medm_14b` | 14B | ~30 GB | Higher-accuracy medical text | A100 / H100 / L40S |
| `jsl_meds_reasoning_8b` | 8B | ~18 GB | Chain-of-thought medical reasoning | A10G / L4 / L40S |

### Spark NLP for Healthcare

NER, entity resolution (ICD-10, SNOMED, RxNorm, etc.), de-identification, relation extraction, clinical embeddings. Runs on CPU+GPU, requires ~30 GB RAM + ~500 MB VRAM.

## Choose Your Platform

| Platform | Best for | Guide |
|---------|---------|-------|
| **Docker** (local GPU or EC2) | Any GPU machine — local, EC2, GCP, etc. Includes EC2 launch script | [docker/](docker/) |
| **Databricks** | Notebook-based workflows, team collaboration | [databricks/](databricks/) |
| **Spark NLP** (Docker) | NLP post-processing (NER, coding, DEID) | [sparknlp/](sparknlp/) |

## Architecture

The demo notebooks call models via HTTP APIs on localhost:

```
Notebook (Python)
  │
  ├── localhost:9460  →  VLM (structured extraction)     ── jsl-vlm-containerized-lib
  ├── localhost:9461  →  OCR (handwriting/printed text)   ── jsl-vlm-containerized-lib
  ├── localhost:9462  →  Medical VLM (7B)                 ── jsl-vlm-containerized-lib
  ├── localhost:9464  →  Image Embeddings (1024-dim, medical)
  ├── localhost:9465  →  Medical VLM (30B)                ── jsl-vlm-containerized-lib
  ├── localhost:9466  →  jsl_vision_ocr_1.0 (high-accuracy structured extraction)
  └── localhost:9470  →  Spark NLP HC (NER, codes, DEID)  ── sparknlp Docker container
```

Each port runs a single model. You can deploy as many or as few as your notebooks need.

## Quick Verification

After deploying any VLM model, test it:

```bash
# Check model is loaded
curl -s http://localhost:9461/v1/models | python3 -m json.tool

# Send a test prompt
curl -s http://localhost:9461/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "jsl_vision_ocr_parsing_1_0",
    "messages": [{"role":"user","content":"Say hello in 5 words."}],
    "max_tokens": 20
  }'
```

For Spark NLP:

```bash
curl -s http://localhost:9470/health | python3 -m json.tool

curl -s http://localhost:9470/ner/clinical \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient diagnosed with diabetes mellitus type 2, prescribed metformin 500mg."}'
```
