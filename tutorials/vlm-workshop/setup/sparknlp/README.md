# Spark NLP for Healthcare — Backend API

GPU-accelerated FastAPI server wrapping Spark NLP for Healthcare. Provides NER, entity resolution, de-identification, relation extraction, and clinical sentence embeddings via a single Docker container.

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ner/{model}` | POST | Named entity recognition. Models: `deid`, `jsl`, `clinical`, `posology`, `radiology`, `anatomy` |
| `/resolve/{system}` | POST | Entity resolution. Systems: `icd10`, `snomed`, `umls`, `loinc`, `rxnorm`, `icdo` |
| `/deid` | POST | De-identify clinical text (obfuscation) |
| `/classify/sections` | POST | Classify text into clinical section types |
| `/relation/{model}` | POST | Relation extraction. Models: `clinical` (Treatment↔Problem), `posology` (Drug↔Dosage/Freq/Route) |
| `/enrich` | POST | Combined NER + resolvers + relations in one call |
| `/enrich/batch` | POST | Batch version of `/enrich` |
| `/embed/text` | POST | Clinical sentence embeddings (sbiobert, 768-dim, L2-normalized) |
| `/health` | GET | Health check with loaded model list |
| `/docs` | GET | Swagger UI |

## Quick Start

### 1. Get a JSL license

You need a [John Snow Labs](https://www.johnsnowlabs.com/) Healthcare NLP license. Place your license JSON at `license.json` (see `license.json.example` for the format).

### 2. Build

```bash
# Extract the SECRET from your license
JSL_SECRET=$(python3 -c "import json; print(json.load(open('license.json'))['SECRET'])")

docker compose build --build-arg JSL_SECRET="$JSL_SECRET"
```

### 3. Run

```bash
docker compose up -d
```

First startup takes ~20 min (downloads all models from S3). Subsequent starts take ~5 min (cached in Docker volumes).

### 4. Test

```bash
# Health check
curl http://localhost:9470/health

# NER
curl -s http://localhost:9470/ner/clinical \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient diagnosed with diabetes mellitus type 2, prescribed metformin 500mg."}'

# Combined /enrich (NER + resolvers + relations in one call)
curl -s http://localhost:9470/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Prescribed amoxicillin 250mg three times daily for 7 days.",
    "ner_models": ["posology"],
    "resolve_systems": ["rxnorm"],
    "relation_models": ["posology"]
  }'

# Clinical text embeddings (768-dim, L2-normalized)
curl -s http://localhost:9470/embed/text \
  -H "Content-Type: application/json" \
  -d '{"texts": ["patient with diabetes mellitus type 2"]}'
```

## What's Loaded

### At Startup
- **6 NER pipelines**: deid, jsl, clinical, posology, radiology, anatomy (all GPU-accelerated via ONNX Runtime)
- **6 Resolver pipelines**: ICD-10, SNOMED, UMLS, LOINC, RxNorm, ICD-O
- **DEID**: `clinical_deidentification` pipeline (obfuscation)
- **Sections**: clinical section classifier
- **Relations**: `re_clinical` (Treatment↔Problem, Test↔Problem)
- **Embeddings**: `sbiobert_base_cased_mli` (768-dim clinical sentence embeddings)

### Lazy-Loaded (on first request)
- **Relations**: `posology_re` (Drug↔Dosage/Frequency/Route/Form/Strength/Duration) — built-in rule-based model, loads in ~10s on first `/relation/posology` or `/enrich` with `relation_models: ["posology"]`

## Requirements

- NVIDIA GPU with CUDA 12.2+ drivers
- Docker with NVIDIA Container Toolkit (`nvidia-docker`)
- ~30 GB RAM (JVM + model caches)
- ~500 MB VRAM (small BERT-base DL models)
- JSL Healthcare NLP license

## Files

```
sparknlp/
├── app/
│   └── main.py              # FastAPI application (all endpoints)
├── Dockerfile                # CUDA 12.2 + Java 8 + Spark NLP
├── docker-compose.yaml       # GPU-enabled compose config
├── requirements.txt          # Public Python deps
├── license.json.example      # License template
├── .gitignore                # Excludes license.json
└── README.md                 # This file
```

## Configuration

Environment variables in `docker-compose.yaml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SPARK_DRIVER_MEMORY` | `24g` | JVM heap for Spark driver |
| `SPARK_EXECUTOR_MEMORY` | `12g` | JVM heap for Spark executors |

Build args in `Dockerfile`:

| Arg | Description |
|-----|-------------|
| `JSL_SECRET` | PyPI token from license JSON (`SECRET` field) |
| `JSL_VERSION` | Spark NLP JSL version (default: `6.3.0`) |
