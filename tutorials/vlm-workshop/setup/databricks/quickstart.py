# Databricks notebook source
# MAGIC %md
# MAGIC # JSL Medical VLM — Quickstart
# MAGIC
# MAGIC **Cluster requirements:**
# MAGIC - DBR: `14.3.x-scala2.12` (NOT gpu-ml)
# MAGIC - Node: `g5.2xlarge` (1x A10G 24GB, models up to 8B) or `g5.12xlarge` (4x A10G 96GB, 30B+ models)
# MAGIC - Docker image: `189352970232.dkr.ecr.us-east-1.amazonaws.com/jsl-marketplace/jsl-llm-lib:v1`
# MAGIC - Docker auth: user `AWS`, password from `aws ecr get-login-password --region us-east-1`
# MAGIC - Workers: 1
# MAGIC - Env vars: `SPARK_NLP_LICENSE`, `SECRET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `_LAUNCHER_STARTED=1`, `VLLM_WORKER_MULTIPROC_METHOD=fork`
# MAGIC - Init script: `fix_pyspark.sh` (removes incompatible pyspark 4.1.1)
# MAGIC
# MAGIC See `README.md` for full setup instructions and verified model configurations.

# COMMAND ----------

# Cell 1: Initialize environment
import sys, os, gc, torch

os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"
sys.path.extend(["/", "/usr/local/lib/python3.10/site-packages"])

gc.collect()
torch.cuda.empty_cache()
free, total = torch.cuda.mem_get_info()
print(f"GPU: {free/1e9:.1f} GB free / {total/1e9:.1f} GB total")

# COMMAND ----------

# Cell 2: Initialize library + load model
from jsl_llm_lib.jsl_llm import JslLlm
import os, gc, torch

os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"
gc.collect()
torch.cuda.empty_cache()

llm = JslLlm()
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"

# Print available models
print("Available models:", llm.friendly_names)

# COMMAND ----------

# Cell 3: Load model
# Change model name and settings to match your needs.
# See README.md verified configs table for gpu_util and tensor_parallel_size per model.
os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"

llm.load_model(
    llm_name="jsl_meds_vl_8b",       # ← change this
    gpu_memory_utilization=0.75,       # 0.75 for g5.2xlarge, 0.95 for g5.12xlarge
    max_model_len=8192,
    tensor_parallel_size=1,            # 1 for g5.2xlarge, 4 for g5.12xlarge (30B+ models)
)
print("Model loaded!")

# COMMAND ----------

# Cell 4: Text inference
result = llm.get_prediction(
    prompt="""Extract all medications, dosages, and frequencies from this clinical note:

Patient is currently on metformin 1000mg twice daily, lisinopril 20mg daily,
and atorvastatin 40mg at bedtime. Aspirin 81mg daily was added today.

Return as JSON with keys: medication, dosage, frequency.""",
    max_new_tokens=2048,
    temperature=0.1,
)
print(result)

# COMMAND ----------

# Cell 5: Vision inference (with image)
# Upload image to DBFS first:
#   dbutils.fs.cp("file:/tmp/doc.png", "dbfs:/tmp/doc.png")

result = llm.get_prediction(
    prompt="Extract all text from this medical document as structured JSON.",
    image_path="/dbfs/tmp/doc.png",
    max_new_tokens=2048,
    temperature=0.1,
)
print(result)

# COMMAND ----------

# Cell 6: Model swap example
# Release current model, load a different one
llm.release_model()
gc.collect()
torch.cuda.empty_cache()

free, total = torch.cuda.mem_get_info()
print(f"GPU free after release: {free/1e9:.1f}/{total/1e9:.1f} GB")

os.environ["VLLM_WORKER_MULTIPROC_METHOD"] = "fork"
llm.load_model(
    llm_name="jsl_vision_ocr_parsing_1_0",   # OCR model (~2GB)
    gpu_memory_utilization=0.75,
    max_model_len=8192,
    tensor_parallel_size=1,
)
print("Swapped to OCR model!")

# COMMAND ----------

# Cell 7: OCR inference
result = llm.get_prediction(
    prompt="Read the text in this image exactly as written.",
    image_path="/dbfs/tmp/cell_crop.png",
    max_new_tokens=256,
)
print(result)
