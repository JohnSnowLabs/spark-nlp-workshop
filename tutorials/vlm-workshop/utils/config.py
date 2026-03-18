"""Shared configuration for all JSON-OCR demo notebooks."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=False)

# ── Task Slots ───────────────────────────────────────────────────────────────
# Each task type has a fixed port. Only one model per slot is active at a time.
# Change ACTIVE_* to match whichever model you have running on that port.

# Structured extraction (VLM) — port 9462 (JSL-7B), 9465 (JSL-30B)
JSL7B_BASE_URL  = "http://127.0.0.1:9462/v1"
JSL7B_MODEL     = "jsl-medical-vl-7b"    # port 9462 on ocr-gpu
JSL30B_BASE_URL = "http://127.0.0.1:9465/v1"
JSL30B_MODEL    = "jsl-medical-vl-30b"   # port 9465 on jsl-gpu (H100)

# Default VLM (points to JSL-30B by default)
VLLM_BASE_URL = JSL30B_BASE_URL
VLLM_MODEL    = JSL30B_MODEL

# JSL Vision VLM — cloud-backed via OpenRouter
JSL_VISION_MODEL    = "jsl_vision_ocr_1.0"
JSL_VISION_BASE_URL = "http://127.0.0.1:9466/v1"   # demo display URL
JSL_VISION_BACKEND  = os.environ.get("JSL_VISION_BACKEND", "jsl_vision_ocr_1.0")

# OpenRouter (cloud VLMs) — for benching
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY  = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL    = JSL_VISION_BACKEND

# OCR — port 9461
OCR_BASE_URL = "http://127.0.0.1:9461/v1"
OCR_MODEL    = "jsl_vision_ocr_parsing_1_0"

# Spark NLP for Healthcare — port 9470
# NER (6 models): deid, jsl, clinical, posology, radiology, anatomy
# Resolvers (6): icd10, snomed, umls, loinc, rxnorm, icdo
# Also: /deid, /classify/sections, /relation
SPARKNLP_BASE_URL = "http://127.0.0.1:9470"

# Medical image embeddings — port 9464
# jsl_vision_embed_crossmodal_1.0: 1024-dim, L2-normalized, all modalities
EMBED_BASE_URL = "http://127.0.0.1:9464"
EMBED_MODEL    = "jsl_vision_embed_crossmodal_1.0"

# Clinical text embeddings (sbiobert) — via Spark NLP on port 9470
CLINICAL_EMBED_BASE_URL = SPARKNLP_BASE_URL  # /embed/text endpoint

# ── Paths ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR = Path("./outputs")
