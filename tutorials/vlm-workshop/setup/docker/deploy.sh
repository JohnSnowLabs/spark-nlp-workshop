#!/usr/bin/env bash
# Deploy a JSL VLM model via Docker
#
# Usage:
#   ./deploy.sh                                          # default: jsl_vision_ocr_parsing_1_0 on port 9461
#   ./deploy.sh jsl_meds_vl_8b 9460                      # 8B medical VLM on port 9460
#   ./deploy.sh jsl_vision_ocr_structured_fp8_1_0 9462   # 32B FP8 structured extraction
#
# Prerequisites:
#   - .env file with JSL license credentials (see .env.example)
#   - Docker with NVIDIA Container Toolkit
#   - GPU with sufficient VRAM (see ../README.md for model sizes)
set -euo pipefail

MODEL_NAME="${1:-jsl_vision_ocr_parsing_1_0}"
PORT="${2:-9461}"

if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example and fill in your JSL credentials."
    exit 1
fi

echo "Deploying ${MODEL_NAME} on port ${PORT}..."
MODEL_NAME="${MODEL_NAME}" PORT="${PORT}" docker compose up -d

echo ""
echo "Waiting for model to be ready..."
for i in $(seq 1 60); do
    if curl -s --max-time 2 "http://localhost:${PORT}/v1/models" 2>/dev/null | grep -q "${MODEL_NAME}"; then
        echo "Ready! Model ${MODEL_NAME} is serving on http://localhost:${PORT}/v1"
        echo ""
        echo "Test it:"
        echo "  curl http://localhost:${PORT}/v1/models"
        echo "  curl http://localhost:${PORT}/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"${MODEL_NAME}\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"max_tokens\":20}'"
        exit 0
    fi
    sleep 10
done

echo "WARNING: Model not ready after 10 minutes."
echo "Check logs: docker logs jsl-vlm"
