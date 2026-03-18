# Databricks Deployment

Run JSL VLM models directly in Databricks notebooks using the Python API.

## Prerequisites

- Databricks workspace with GPU cluster access
- JSL license (`SPARK_NLP_LICENSE` + `SECRET`)
- AWS credentials for model download (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)

## Verified Model Configurations

All tested and working on Databricks as of 2026-03-09:

| Model | Size | Instance | gpu_util | tp | Use Case |
|-------|------|----------|----------|----|----------|
| `jsl_vision_ocr_1_0_light` | 1B | g5.2xlarge | 0.75 | 1 | Lightweight OCR |
| `jsl_vision_ocr_parsing_1_0` | 1B | g5.2xlarge | 0.75 | 1 | Handwriting / printed text OCR |
| `jsl_meds_vl_8b` | 8B | g5.2xlarge | 0.75 | 1 | Medical document understanding |
| `jsl_vision_ocr_1_0` | 30B | g5.12xlarge | 0.95 | 4 | High-accuracy OCR |
| `jsl_vision_ocr_structured_1_0_light` | 30B | g5.12xlarge | 0.95 | 4 | Structured extraction (tables, forms) |
| `jsl_vision_ocr_structured_1_0` | 32B | g5.12xlarge | 0.95 | 4 | Structured extraction (dense) |
| `jsl_vision_ocr_structured_fp8_1_0` | 32B FP8 | g5.12xlarge | 0.95 | 4 | Structured extraction (quantized, ~34GB) |

Instance GPU specs:
- `g5.2xlarge` = 1x NVIDIA A10G (24 GB VRAM)
- `g5.12xlarge` = 4x NVIDIA A10G (96 GB VRAM total), 3.8 TB NVMe at `/local_disk0`

## 1. Create Cluster

### Cluster Configuration

| Setting | Value |
|---------|-------|
| **Databricks Runtime** | `14.3.x-scala2.12` (NOT gpu-ml — doesn't support custom containers) |
| **Node Type** | `g5.2xlarge` (models up to 8B) or `g5.12xlarge` (30B+ models, tp=4) |
| **Workers** | 1 (minimum — 0 workers causes REPL warnings) |
| **Docker Image** | `189352970232.dkr.ecr.us-east-1.amazonaws.com/jsl-marketplace/jsl-llm-lib:v1` |
| **Docker Auth** | Basic auth — user: `AWS`, password: ECR token (see below) |
| **EBS Storage** | 200 GB SSD per node |
| **Auto-terminate** | 60 min (recommended — GPU instances are expensive) |

### Get ECR Auth Token

```bash
aws ecr get-login-password --region us-east-1
```

This token expires after 12 hours. Paste it as the Docker password in cluster config (Advanced Options > Docker > Authentication).

### Environment Variables

Set these in **Advanced Options > Spark > Environment Variables**:

```
SPARK_NLP_LICENSE=<your license key>
SECRET=<your secret>
AWS_ACCESS_KEY_ID=<your aws key>
AWS_SECRET_ACCESS_KEY=<your aws secret>
_LAUNCHER_STARTED=1
VLLM_WORKER_MULTIPROC_METHOD=fork
```

### Init Script

Upload `fix_pyspark.sh` (included in this folder) to your Databricks workspace and configure it as a cluster init script:

```bash
#!/bin/bash
# Removes incompatible pyspark 4.1.1 that ships with DBR 14.3
pip uninstall -y pyspark 2>/dev/null || true
```

## 2. Timing Expectations

| Phase | Time |
|-------|------|
| Cluster starting → RUNNING | 5-10 min |
| Docker image pull (first time) | up to 15 min |
| Model download from S3 (first time) | 1-10 min (depends on model size) |
| Model load (cached) | 1-3 min |
| **Total per model (cold start)** | **~20-40 min** |
| **Total per model (warm, cached)** | **~5-10 min** |

Models are cached after first download. Subsequent loads on the same cluster are fast.

## 3. Use in Notebook

### Cell 1: Initialize Environment

```python
import sys, os, gc, torch

os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"
sys.path.extend(["/", "/usr/local/lib/python3.10/site-packages"])

gc.collect()
torch.cuda.empty_cache()
free, total = torch.cuda.mem_get_info()
print(f"GPU: {free/1e9:.1f} GB free / {total/1e9:.1f} GB total")
```

### Cell 2: Initialize Library

```python
from jsl_llm_lib.jsl_llm import JslLlm
import os

# Critical: re-set after import (module-level code may override)
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"

llm = JslLlm()

# Re-set again after init
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"

# List available models
print("Available models:", llm.friendly_names)
```

### Cell 3: Load Model

```python
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"

llm.load_model(
    llm_name="jsl_meds_vl_8b",
    gpu_memory_utilization=0.75,     # use values from verified configs table above
    max_model_len=8192,
    tensor_parallel_size=1,          # 1 for g5.2xlarge, 4 for g5.12xlarge
)
print("Model loaded!")
```

### Cell 4: Run Inference (Text Only)

```python
result = llm.get_prediction(
    prompt="""Extract all medications, dosages, and frequencies from this clinical note:

Patient is currently on metformin 1000mg twice daily, lisinopril 20mg daily,
and atorvastatin 40mg at bedtime. Aspirin 81mg daily was added today.

Return as JSON with keys: medication, dosage, frequency.""",
    max_new_tokens=2048,
    temperature=0.1,
)
print(result)
```

### Cell 5: Run Inference (With Image)

```python
# Upload image to DBFS first:
#   dbutils.fs.cp("file:/tmp/doc.png", "dbfs:/tmp/doc.png")

result = llm.get_prediction(
    prompt="Extract all text from this medical document as structured JSON.",
    image_path="/dbfs/tmp/doc.png",
    max_new_tokens=2048,
    temperature=0.1,
)
print(result)
```

### Cell 6: Chain-of-Thought Reasoning

```python
# For reasoning models: jsl_meds_reasoning_8b, jsl_medm_reasoning_32b
result = llm.get_prediction(
    prompt="A patient presents with chest pain, elevated troponin, and ST elevation in leads II, III, aVF. What is the diagnosis and recommended treatment?",
    thinking=True,
    max_new_tokens=4096,
)
print(result)
```

## 4. Model Swapping

Load different models on the same GPU by releasing the current one first. This is the recommended pattern for pipelines that use multiple models:

### Release Current Model

```python
llm.release_model()
gc.collect()
torch.cuda.empty_cache()

# Verify GPU is free
free, total = torch.cuda.mem_get_info()
print(f"GPU free: {free/1e9:.1f}/{total/1e9:.1f} GB")
```

### Load a Different Model

```python
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"

llm.load_model(
    llm_name="jsl_vision_ocr_structured_fp8_1_0",
    gpu_memory_utilization=0.95,
    max_model_len=8192,
    tensor_parallel_size=4,    # 32B needs 4x A10G (g5.12xlarge)
)
print("Model swapped!")
```

### Full Swap Example (Pipeline)

```python
# Stage 1: Classify pages with 8B model
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"
llm.load_model("jsl_meds_vl_8b", gpu_memory_utilization=0.75, max_model_len=8192, tensor_parallel_size=1)

for page in pages:
    result = llm.get_prediction(prompt="Is this a medical form? Reply YES or NO.", image_path=page, max_new_tokens=10)
    # ... process result

# Stage 2: Extract data with 32B model
llm.release_model()
gc.collect(); torch.cuda.empty_cache()

os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"
llm.load_model("jsl_vision_ocr_structured_fp8_1_0", gpu_memory_utilization=0.95, max_model_len=8192, tensor_parallel_size=4)

for page in medical_pages:
    result = llm.get_prediction(prompt="Extract all fields as JSON.", image_path=page, max_new_tokens=2048)
    # ... process result

# Stage 3: OCR
llm.release_model()
gc.collect(); torch.cuda.empty_cache()

os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"
llm.load_model("jsl_vision_ocr_parsing_1_0", gpu_memory_utilization=0.75, max_model_len=8192, tensor_parallel_size=1)

for cell in cell_crops:
    result = llm.get_prediction(prompt="Read the text in this image exactly as written.", image_path=cell, max_new_tokens=256)
    # ... process result
```

## 5. Large Model Disk Storage

On `g5.12xlarge`, models are large (up to 60GB+ for 32B). The root disk may not have enough space. The NVMe at `/local_disk0` has 3.8 TB:

```python
import os
# Redirect model cache to NVMe (do this BEFORE loading any model)
os.environ["JSL_HOME"] = "/local_disk0/jsl_cache"
os.makedirs("/local_disk0/jsl_cache", exist_ok=True)
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `CUDA out of memory` on load | Lower `gpu_memory_utilization`, or use `enforce_eager=True` in `load_model()`, or use larger instance |
| OOM during CUDA graph capture | Add `enforce_eager=True` to `load_model()` — saves ~2GB but slightly slower first inference |
| `spawn` / multiprocessing errors | Ensure `VLLM_WORKER_MULTIPROC_METHOD=fork` is set BEFORE and AFTER every import/load |
| Ghost GPU memory (nvidia-smi shows used, no processes) | Restart cluster — dead subprocess leaked CUDA allocations. Never retry on same cluster after EngineCore crash |
| `pyspark` import errors | Make sure `fix_pyspark.sh` init script ran. Check cluster init script logs |
| License validation timeout | Check `SPARK_NLP_LICENSE` env var is set correctly in cluster config |
| Model download fails | Check `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` are from your JSL license JSON |
| Root disk full during download | Redirect cache to NVMe: set `JSL_HOME=/local_disk0/jsl_cache` (see section 5) |
| 32B model OOM on g5.2xlarge | Must use `g5.12xlarge` with `tensor_parallel_size=4` for 30B+ models |
| Docker image pull slow | First boot pulls ~15GB image. Subsequent cluster starts use cached image |
