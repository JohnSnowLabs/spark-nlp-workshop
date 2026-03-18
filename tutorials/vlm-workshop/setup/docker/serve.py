#!/usr/bin/env python3
"""
JSL VLM HTTP Server
Downloads model from JSL S3 (via jsl-llm-lib) and serves via vLLM OpenAI-compatible API.

Environment variables:
    SPARK_NLP_LICENSE  - JSL license key (required)
    SECRET             - JSL PyPI secret (required for first download)
    AWS_ACCESS_KEY_ID  - AWS key for model download from JSL S3
    AWS_SECRET_ACCESS_KEY - AWS secret for model download from JSL S3
    MODEL_NAME         - Model to serve (default: jsl_vision_ocr_parsing_1_0)
    PORT               - Port to listen on (default: 9461)
    GPU_MEMORY_UTILIZATION - Fraction of GPU VRAM to use (default: 0.85)
    MAX_MODEL_LEN      - Max context length (default: 8192)
    MAX_NUM_SEQS       - Max concurrent sequences (default: 8)

Usage:
    python3 serve.py
"""
import gc
import glob
import os
import subprocess
import sys

sys.path.extend(["/", "/usr/local/lib/python3.10/site-packages"])

MODEL_NAME = os.environ.get("MODEL_NAME", "jsl_vision_ocr_parsing_1_0")
PORT = os.environ.get("PORT", "9461")
GPU_UTIL = os.environ.get("GPU_MEMORY_UTILIZATION", "0.85")
MAX_MODEL_LEN = os.environ.get("MAX_MODEL_LEN", "8192")
MAX_NUM_SEQS = os.environ.get("MAX_NUM_SEQS", "8")
CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "/opt/.prop")


def find_cached_model():
    """Check if model is already downloaded in cache."""
    for d in glob.glob(os.path.join(CACHE_DIR, "*")):
        config = os.path.join(d, "config.json")
        if os.path.isfile(config):
            return d
    return None


def download_model():
    """Use JslLlm to download model from JSL S3. Returns local model path."""
    print(f"[serve] Downloading {MODEL_NAME} from JSL model registry...")
    from jsl_llm_lib.jsl_llm import JslLlm

    llm = JslLlm()
    # load_model_from_s3 downloads the tar, extracts, and loads into offline engine
    llm.load_model_from_s3(MODEL_NAME)

    # Find the extracted model path
    model_path = find_cached_model()
    if not model_path:
        print("[serve] ERROR: Model download succeeded but can't find extracted files")
        sys.exit(1)

    # Release the offline engine (we'll start HTTP server instead)
    del llm
    gc.collect()

    try:
        import torch
        torch.cuda.empty_cache()
    except Exception:
        pass

    return model_path


def main():
    print(f"[serve] Model: {MODEL_NAME}")
    print(f"[serve] Port: {PORT}")
    print(f"[serve] GPU util: {GPU_UTIL}, max_model_len: {MAX_MODEL_LEN}")

    # Check cache first
    model_path = find_cached_model()
    if model_path:
        print(f"[serve] Found cached model at {model_path}")
    else:
        model_path = download_model()
        print(f"[serve] Model downloaded to {model_path}")

    # Start vLLM OpenAI-compatible HTTP server
    print(f"[serve] Starting vLLM server on port {PORT}...")
    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_path,
        "--served-model-name", MODEL_NAME,
        "--port", PORT,
        "--trust-remote-code",
        "--gpu-memory-utilization", GPU_UTIL,
        "--max-model-len", MAX_MODEL_LEN,
        "--max-num-seqs", MAX_NUM_SEQS,
        "--host", "0.0.0.0",
    ]

    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
