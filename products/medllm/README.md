<div align="center">
  <img src="assets/logo.png" alt="JohnSnowLabs Logo" width="300" height="300">
</div>
<div align="center">
  <h1> JohnSnowLabs Medical LLM Inference Server</h1>
</div>

## Overview

This Docker image provides a deployable inference server for medical large language models (LLMs) developed by JohnSnowLabs. Designed for healthcare and medical research applications, this service enables advanced medical AI capabilities with flexible deployment options.

## 🔬 Supported Medical LLM Models

| Model Name                   | Parameters | Total Memory | Max Sequence Length | Model Size | Max KV-Cache | Tensor Parallel Sizes |
|------------------------------|------------|--------------|---------------------|------------|--------------|----------------------|
| Medical-Visual-LLM-8B       | 8B          | ~25 GB       | 262K                | 17 GB      | 8 GB         | 1, 2, 4, 8           |
| Medical-LLM-14B              | 14B        | ~40 GB       | 16K                 | 27 GB      | 13 GB        | 1, 2                 |
| Medical-LLM-Small            | 8B         | ~25 GB       | 262K                | 17 GB      | 8 GB         | 1, 2, 4, 8           |
| Medical-LLM-Medium           | 27B        | ~67 GB       | 262K                | 51 GB      | 16 GB        | 1, 2, 4, 8           |
| Medical-LLM-Medium-Onco      | 27B        | ~67 GB       | 262K                | 51 GB      | 16 GB        | 1, 2, 4, 8           |
| Medical-DM-Small             | 4B         | ~9 GB        | 16K                 | 8 GB       | 1 GB         | 1, 2, 4              |
| Medical-Reasoning-LLM-32B    | 27B        | ~66 GB       | 262K                | 50 GB      | 16 GB        | 2, 4, 8              |
| Medical-Spanish-LLM-24B      | 24B        | ~145 GB      | 128K                | 45 GB      | 100 GB       | 2, 4, 8              |
| Medical-Visual-LLM-30B       | 30B        | ~150 GB      | 262K                | 58 GB      | 92 GB        | 2, 4, 8              |
| Vision-OCR-LLM               | 1B         | ~5 GB     | 32K                | 2 GB    | 3 GB      | 1, 2, 4               |
| Vision-OCR-Structured-LLM    | 8B         | ~23 GB    | 128K               | 16 GB      | 7 GB     | 1, 2, 4               |

> **Important Notes**
>
> **Memory Calculations:** All memory calculations are based on half-precision (fp16/bf16) weights. Recommended GPU Memory considers the model size and the maximum key-value cache at the model's maximum sequence length. These calculations follow the guidelines from [DJL's LMI Deployment Guide.](https://docs.djl.ai/master/docs/serving/serving/docs/lmi/deployment_guide/instance-type-selection.html)

## 🚀 Quick Start

### 🔄 Pull the Docker Image

You can pull the image from 👉 [Docker Hub](https://hub.docker.com/r/johnsnowlabs/jsl-llms):

```bash
docker pull johnsnowlabs/jsl-llms:latest
```

> **GPU driver:** the image uses CUDA 13, so the host needs NVIDIA driver 580 or newer.

### 🐳 Run the Container

#### Basic Docker Run Command

```bash
docker run -d \
    --gpus all \
    --env "SPARK_NLP_LICENSE=your_license_key" \
    -p 8080:8080 \
    --ipc=host \
    johnsnowlabs/jsl-llms \
    --model Medical-LLM-Small \
    --port 8080
```

#### Using License File

Mount a `license.json` file for more secure license management:

```bash
docker run -d \
    --gpus all \
    -v "$(pwd)/license.json:/app/license.json" \
    -p 8080:8080 \
    --ipc=host \
    johnsnowlabs/jsl-llms \
    --model Medical-LLM-Small \
    --port 8080
```

## ⚙️ Advanced Configuration

For detailed information about available parameters and configuration options, please refer to the official VLLM documentation:
📚 [VLLM Server Parameters Documentation](https://docs.vllm.ai/en/stable/serving/openai_compatible_server.html#cli-reference)

### Key Parameters to Customize

- `--tensor-parallel-size`: Set number of GPUs for tensor parallelism
- `--max-model-len`: Maximum sequence length
- `--gpu-memory-utilization`: Fraction of GPU memory to be used

### Memory Optimization Tips

- Use smaller sequence lengths to reduce KV-cache memory
- Leverage tensor parallelism for large models
- Select an appropriate model based on your GPU resources

## 🌐 API Endpoints

### Health and Monitoring

- `GET /health`: Check service health status
- `GET /ping`: Quick server ping
- `GET /version`: Retrieve server version information

### Model Management

#### List Available Models
- **Endpoint**: `/v1/models`
- **Method**: GET
- **Description**: Retrieve a list of available models on the server

### Model Interactions

#### Chat Completions
- **Endpoint**: `/v1/chat/completions`
- **Method**: POST
- **Example Request**:
```python
payload = {
    "model": "Medical-LLM-Small",
    "messages": [
        {"role": "system", "content": "You are a professional medical assistant"},
        {"role": "user", "content": "Explain symptoms of chronic fatigue syndrome"}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
}
```

#### Text Completions
- **Endpoint**: `/v1/completions`
- **Method**: POST
- **Example Request**:
```python
payload = {
    "model": "Medical-LLM-Small",
    "prompt": "Provide a detailed explanation of rheumatoid arthritis treatment",
    "temperature": 0.7,
    "max_tokens": 4096
}
```

## 🧮 Decision Models

Decision models do not write text. They score a fixed set of options for each typed question about a record and return a probability for every option. Use them to classify, grade and screen at volume.

`Medical-DM-Small` is not a chat model: it does not serve `/v1/chat/completions`. Call it through `POST /v1/decisions`. `GET /v1/models` lists it, and `GET /health` tells you when it is ready.

```bash
docker run -d \
    --gpus all \
    --env "SPARK_NLP_LICENSE=your_license_key" \
    -p 8080:8080 \
    --ipc=host \
    johnsnowlabs/jsl-llms:0.33.0 \
    --model Medical-DM-Small \
    --port 8080
```

### Request and response

Send one `state` (the record) and up to 64 `questions`. Every question has a `type` and `instructions` in plain language.

| Question type | Answer | `criteria` |
|---------------|--------|------------|
| `choice` | Pick one option. Returns `choice`, `confidence` and `probabilities`. | Object of option key to description, 1 to 255 options. |
| `score` | Ordinal level. Returns the expected `score` and a probability per level. | Array of level descriptions, in order, 1 to 255 levels. |
| `noul` | Yes or no. Returns `noul`, the probability that the answer is yes. | Optional `{"true": "...", "false": "..."}` definitions. |

`state` can be a string, an object, a list, a number or a boolean. Write the instruction as you would ask a colleague, and describe each option so the model can tell them apart.

Request:

```bash
curl -s http://localhost:8080/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Medical-DM-Small",
    "state": "Discharge summary. Patient Alder Quill was admitted with chest pain. Troponin normal; discharged home on aspirin.",
    "questions": {
      "leak": {
        "type": "noul",
        "instructions": "Is any real identifying detail left in this de-identified note?",
        "criteria": {
          "true": "A real name, phone number, address, date or record number appears in the text",
          "false": "Every identifier is a tag such as [NAME] or [DATE], or has been removed"
        }
      },
      "kind": {
        "type": "choice",
        "instructions": "Which kind of real identifier is left in the note?",
        "criteria": {
          "person_name": "A real person name (a tag like [NAME] does not count)",
          "phone_number": "A real telephone number",
          "none": "No real identifier: only tags such as [NAME] or [DATE]"
        }
      }
    }
  }'
```

Response (illustrative values):

```json
{
  "model": "Medical-DM-Small",
  "answers": {
    "leak": {"type": "noul", "noul": 1.0},
    "kind": {"type": "choice", "choice": "person_name", "confidence": 0.99,
             "probabilities": {"person_name": 0.998, "phone_number": 0.0, "none": 0.002}}
  },
  "usage": {"input_tokens": 142, "output_tokens": 2}
}
```

- Choice `confidence` rescales the top probability against chance: `(max p - 1/k) / (1 - 1/k)`, where `k` is the number of options. Route low-confidence answers to a human reviewer.
- The response `model` is always the id you sent.
- The record, one question and its options must fit in 16,384 tokens. Longer input returns `422` instead of being cut short.
- Errors: `400` unknown model, `422` invalid request, `502` and `503` model unavailable, `504` timeout after 60 seconds.

### Model

| Model id | Built on | Input | Use it for |
|----------|----------|-------|------------|
| `Medical-DM-Small` | Kev 4B fine-tuned for PHI leak detection (Qwen3.5-4B-Base) | Text, 16,384 tokens | Deciding whether text still contains PHI. |

### How it works

`Medical-DM-Small` is a purpose-built classifier. It scores all the options of a question together in one pass, and the questions of a request are scored in parallel, so a short note takes about 0.1 seconds on an NVIDIA A10G. Every question is answered on its own: questions about the same record do not influence each other.

## 🛡️ Guard Models (experimental)

Guard models check text for protected health information (PHI). They read whole documents and return scores. They do not write or change text. Use them to find PHI that a de-identification step missed, to measure how much PHI a note shows, and to find raw notes that hold PHI.

Guards are small models that run on the CPU, next to the decision model `Medical-DM-Small`. The image turns off the built-in telemetry of onnxruntime, the library that runs them. They are not chat models and do not appear in `GET /v1/models`. Start `Medical-DM-Small` with `--guards`:

```bash
docker run -d \
    --gpus all \
    --env "SPARK_NLP_LICENSE=your_license_key" \
    -p 8080:8080 \
    --ipc=host \
    johnsnowlabs/jsl-llms:0.33.0 \
    --model Medical-DM-Small \
    --guards all \
    --port 8080
```

`--guards` takes `all`, or guard ids separated by commas, for example `--guards phi-guard-v7-fast`. Without the flag the guard endpoints are not active.

These are PHI guards v0.7 (experimental, still under test):

| Guard id | Use it for |
|----------|------------|
| `phi-guard-v7-final` | Best accuracy. |
| `phi-guard-v7-fast` | The same outputs, about 5 times faster, a little less accurate. |

### What a guard returns

Every document gets these outputs. Cut-off for every label is 0.5.

| Output | Fields | Meaning |
|--------|--------|---------|
| Leak | `score`, `logit`, `label` | Probability that PHI is still readable in a de-identified note. |
| Harmful leak | `harmful_score`, `harmful_logit`, `harmful_label` | Probability that the leak is harmful. Never above `score`. A name, ID, contact detail, date of birth, street address, an age over 89, or three or more harmless kinds together are harmful. A clinician name, city or state, hospital, organisation, another date, or an age up to 89 alone are not. |
| Exposure level | `level`, `expected_level`, `level_scores`, `level_logits` | How much PHI a note shows, from 0 to 6: none, trace, low, moderate, high, very high, saturated. `level_scores[k-1]` is the probability that the level is at least `k`. |
| Raw note | `raw_score`, `raw_logit`, `raw_label` | Probability that a raw note, before de-identification, holds PHI at all. |

Use leak and harmful leak on de-identified text, raw note on raw text, and exposure level on either. Very confident scores all round to 1.0: rank documents with the `logit` fields.

Send masked or raw documents. Do not send an obfuscated copy (real PHI replaced by realistic fake names, dates and numbers): it looks like real PHI to the guard and raises false flags.

### List the guards

```
GET /v1/guards
```

Returns the guards loaded in this container, with their outputs and cut-off. The list is empty when the container was started without `--guards`.

```json
{"object": "list", "data": [
  {"id": "phi-guard-v7-final", "task": "harm+richness+raw",
   "question": "Did PHI survive masking? score = P(PHI left), harmful_score = P(a harmful leak), level 0-6 = PHI exposed, raw_score = P(PHI in a raw note)",
   "outputs": ["score", "logit", "label", "cutoffs", "harmful_score", "...", "raw_logit", "raw_label"],
   "default_cutoff": 0.5, "cutoffs": {"default": 0.5}},
  {"id": "phi-guard-v7-fast", "...": "..."}
]}
```

The first guard in the list is the default guard of the ensemble below.

### Score documents

```bash
curl -s http://localhost:8080/v1/guards \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-guard-v7-final",
    "docs": [
      {"id": "note-001", "text": "Pt [NAME] seen on [DATE] for chest pain. Troponin negative x2, ECG normal sinus rhythm. Discharged home on aspirin 81 mg daily."},
      {"id": "note-002", "text": "Pt Maria Delgado, DOB 03/14/1956, MRN 4471923, seen on [DATE] for chest pain. Discharged home on aspirin 81 mg daily."}
    ]
  }'
```

Response (the second result is shown in full):

```json
{
  "model": "phi-guard-v7-final",
  "default_cutoff": 0.5,
  "results": [
    {"id": "note-001", "score": 0.0101, "logit": -4.5816, "label": false, "cutoffs": {"0.5": false}, "...": "..."},
    {"id": "note-002", "score": 1.0, "logit": 15.9447, "label": true, "cutoffs": {"0.5": true},
     "harmful_score": 1.0, "harmful_logit": 11.105, "harmful_label": true,
     "level": 3, "expected_level": 3.4924,
     "level_scores": [1.0, 1.0, 1.0, 0.4923, 0.0001, 0.0],
     "level_logits": [23.6157, 20.1183, 12.1113, -0.0306, -9.1865, -15.1122],
     "raw_score": 1.0, "raw_logit": 31.8373, "raw_label": true}
  ],
  "usage": {"docs": 2, "windows": 2, "ms": 12}
}
```

- Send up to 16,384 documents and 50 MiB per request. Every document needs a unique `id` and a string `text`. Results come back in the order you sent them.
- Long documents are read in 1,024-byte windows. An empty `text` scores 0.
- Errors: `400` invalid body, empty list, missing `text` or duplicate ids, `404` unknown guard, `413` too many documents or too large.

### Ensemble: a guard and the decision model together

`POST /v1/guards/ensemble` checks each document with a guard and with `Medical-DM-Small`, combines the two scores into one, and routes the document. The combined score ranks leaks better than either model alone, and the route sends only the disagreements to a person.

| Field | |
|-------|---|
| `model` | `phi-guard-ensemble`. |
| `guard` (optional) | A loaded guard that has a harmful output. Default: the first such guard in `GET /v1/guards`, which is `phi-guard-v7-final` when it is loaded. The response names the guard that was used. |
| `decision` (optional) | `Medical-DM-Small`. The container has one decision model, so any other name returns `400`. |
| `aggregation` (optional) | `mean_logit` (default, best ranking), `mean`, `min` or `max`. |
| `docs` | Up to 64 documents: `id`, `text` and an optional `decision_score` (a probability from 0 to 1). A document with a `decision_score` is not sent to the decision model. |

```bash
curl -s http://localhost:8080/v1/guards/ensemble \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-guard-ensemble",
    "guard": "phi-guard-v7-final",
    "aggregation": "mean_logit",
    "docs": [
      {"id": "note-001", "text": "Pt [NAME] seen on [DATE] for chest pain. Troponin negative x2, ECG normal sinus rhythm. Discharged home on aspirin 81 mg daily."},
      {"id": "note-002", "text": "Pt Maria Delgado, DOB 03/14/1956, MRN 4471923, seen on [DATE] for chest pain. Discharged home on aspirin 81 mg daily."}
    ]
  }'
```

Response (illustrative values):

```json
{
  "model": "phi-guard-ensemble",
  "guard": "phi-guard-v7-final",
  "aggregation": "mean_logit",
  "results": [
    {"id": "note-001", "score": 0.0036, "logit": -5.6128, "label": false,
     "harmful_score": 0.0019, "harmful_logit": -6.2646, "harmful_label": false,
     "decision": "clean", "agreement": true,
     "members": {"guard_score": 0.0101, "guard_harmful_score": 0.0028, "decision_score": 0.0013},
     "level": 0, "level_scores": ["..."], "raw_score": 0.0},
    {"id": "note-002", "score": 1.0, "logit": 10.4218, "label": true,
     "harmful_score": 0.9997, "harmful_logit": 8.0019, "harmful_label": true,
     "decision": "leak", "agreement": true,
     "members": {"guard_score": 1.0, "guard_harmful_score": 1.0, "decision_score": 0.9926},
     "level": 3, "level_scores": ["..."], "raw_score": 1.0}
  ],
  "usage": {"docs": 2, "windows": 2, "decision_calls": 2, "ms": 520}
}
```

- `guard` is the guard that was used: the one you sent, or the default.
- `decision` is `leak` when both models flag the document, `review` when only one does, and `clean` when neither does. `agreement` is true for `leak` and `clean`.
- `score`, `logit` and `label` are the combined leak result. `harmful_*` combines the guard's harmful output with the decision score, because the decision model has no harmful output. With `max`, the decision model therefore dominates the harmful score: use `mean_logit` if you rely on `harmful_label`.
- `members` gives the score of each model. `level`, `level_scores` and `raw_score` come from the guard.
- A document must fit the decision model (16,384 tokens), otherwise the request returns `422`.
- Errors: `400` for an unknown guard, decision model or aggregation, a bad `decision_score`, an invalid list or duplicate ids, `404` unknown model, `413` more than 64 documents, `422` a document that is too long, `502`, `503` and `504` when the decision model fails. If the decision model fails, the request fails. It never returns one model's score alone.

## 📘 API Reference

A container started with a decision model serves an interactive API reference of its endpoints (`/v1/decisions`, `/v1/guards`, `/v1/guards/ensemble`, `/health`, `/v1/models`):

```
http://localhost:8080/openapi-doc
```

The page is built from `GET /openapi.json`, which you can also use with your own tools. The page loads its viewer and fonts from the internet in your browser (`cdn.jsdelivr.net` and Google Fonts). Without internet access in the browser, read `/openapi.json` instead.

## 🤝 Support

For technical support, inquiries, or enterprise solutions, contact:
- **Email**: support@johnsnowlabs.com
- **Live Chat**: Available on our [website](https://www.johnsnowlabs.com/) during business hours

## 📝 Licensing

A valid Spark NLP license is required to use this inference server. Licenses can be obtained through JohnSnowLabs.
