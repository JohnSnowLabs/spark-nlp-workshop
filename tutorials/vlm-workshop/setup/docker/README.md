# Docker Deployment

Deploy JSL VLM models on any machine with an NVIDIA GPU and Docker — local workstation or cloud (EC2, GCP, etc.).

## Prerequisites

- NVIDIA GPU with sufficient VRAM (see [GPU Memory Guide](#gpu-memory-guide) below)
- Docker with NVIDIA Container Toolkit (`nvidia-docker`)
- JSL license file (`license.json`)

## 1. Set Up Credentials

Copy your license values into `.env`:

```bash
cp .env.example .env
# Edit .env with your license values
```

Or extract them automatically from your license JSON:

```bash
python3 -c "
import json
lic = json.load(open('path/to/your/license.json'))
print(f\"SPARK_NLP_LICENSE={lic['LICENSE']}\")
print(f\"SECRET={lic['SECRET']}\")
print(f\"AWS_ACCESS_KEY_ID={lic['AWS_ACCESS_KEY_ID']}\")
print(f\"AWS_SECRET_ACCESS_KEY={lic['AWS_SECRET_ACCESS_KEY']}\")
" > .env
```

## 2. Deploy a Model

### Option A: docker-compose (recommended)

```bash
# Default: jsl_vision_ocr_parsing_1_0 on port 9461
docker compose up -d

# Or pick a different model + port:
MODEL_NAME=jsl_meds_vl_8b PORT=9460 docker compose up -d
```

### Option B: deploy script

```bash
./deploy.sh jsl_vision_ocr_parsing_1_0 9461
./deploy.sh jsl_meds_vl_8b 9460
```

The script waits for the model to be ready and prints test commands.

First startup downloads the model from JSL S3 (~1-10 min depending on size). Subsequent starts use cached models.

## 3. Verify

```bash
curl -s http://localhost:9461/v1/models

curl -s http://localhost:9461/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "jsl_vision_ocr_parsing_1_0",
    "messages": [{"role":"user","content":"Hello, what can you do?"}],
    "max_tokens": 100
  }'
```

## 4. Use From Notebooks

```python
import openai

client = openai.OpenAI(base_url="http://localhost:9461/v1", api_key="none")
resp = client.chat.completions.create(
    model="jsl_vision_ocr_parsing_1_0",
    messages=[{"role": "user", "content": "Extract text from this image."}],
    max_tokens=2048,
)
print(resp.choices[0].message.content)
```

## Multiple Models

Run multiple models on the same GPU, each on a different port:

```bash
./deploy.sh jsl_vision_ocr_parsing_1_0 9461   # ~3 GB VRAM
./deploy.sh jsl_meds_vl_8b 9460               # ~18 GB VRAM
```

Ensure total VRAM fits your GPU. Start models sequentially — wait for each to be ready before starting the next.

---

## Deploy on AWS EC2

Don't have a local GPU? Launch an EC2 instance and deploy with the same Docker setup.

### Recommended Instances

| Instance | GPU | VRAM | Best for | Cost |
|----------|-----|------|----------|------|
| `g5.xlarge` | 1x A10G | 24 GB | Single model up to 8B | ~$1.01/hr |
| `g6e.2xlarge` | 1x L40S | 48 GB | Multiple models or 32B FP8 | ~$1.86/hr |
| `g5.12xlarge` | 4x A10G | 96 GB | All models, tensor parallel | ~$5.67/hr |

**AMI**: Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04) — comes with NVIDIA drivers + Docker + nvidia-container-toolkit.

**Disk**: 200 GB gp3 (models are ~5-50 GB each).

### Option A: One-Click Launch

```bash
# Creates security group + launches instance + prints SSH command
bash 0_deploy_ec2.sh <your-key-pair-name>
```

### Option B: AWS Console

1. **EC2 > Launch Instance**
2. AMI: search **"Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)"**
3. Instance type: **g6e.2xlarge** (or see table above)
4. Key pair: create or select existing
5. Storage: **200 GB gp3**
6. Security group: allow inbound **TCP 22** (SSH)

### Deploy on the Instance

```bash
# SSH in
ssh -i ~/.ssh/your-key.pem ubuntu@<instance-ip>

# Create working directory
mkdir -p ~/jsl-vlm && cd ~/jsl-vlm

# Copy files from this folder to the instance (docker-compose.yaml, serve.py, .env)
# Or scp them: scp docker-compose.yaml serve.py .env ubuntu@<ip>:~/jsl-vlm/

# Deploy
docker compose up -d
curl http://localhost:9461/v1/models   # verify
```

### Connect From Your Machine

**SSH tunnel** (recommended — no need to open extra ports):

```bash
ssh -N -L 9460:localhost:9460 -L 9461:localhost:9461 -i ~/.ssh/your-key.pem ubuntu@<instance-ip>
```

Then use `http://localhost:9461/v1` from notebooks on your laptop as if the model were local.

### Stop When Not In Use

GPU instances are expensive. Stop when done:

```bash
aws ec2 stop-instances --instance-ids <instance-id>
```

Model cache persists on the EBS volume — restart is fast (no re-download).

---

## GPU Memory Guide

| GPU | VRAM | Max Model |
|-----|------|-----------|
| T4 | 16 GB | `jsl_vision_ocr_parsing_1_0` (1B) |
| A10G / L4 | 24 GB | `jsl_meds_vl_8b` (8B) |
| L40S | 48 GB | Multiple models or `jsl_vision_ocr_structured_fp8_1_0` (32B FP8) |
| A100 / H100 | 80 GB | Any model, any size |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| OOM on startup | Lower `GPU_MEMORY_UTILIZATION` in `.env` or use a smaller model |
| Model not found after start | Wait 1-10 min for first-time model download from S3 |
| Connection refused | Check `docker logs jsl-vlm` for startup errors |
| Slow first request | vLLM compiles CUDA graphs on first inference — subsequent requests are fast |
| Docker GPU not detected | Ensure `nvidia-container-toolkit` is installed and Docker restarted |
