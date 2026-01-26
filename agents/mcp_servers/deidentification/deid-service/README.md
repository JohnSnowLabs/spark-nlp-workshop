# JSL Deidentification REST API Service

© John Snow Labs 2026

A Docker-based REST API service for clinical text deidentification using Spark NLP Healthcare.

## Overview

This service loads the deidentification pipeline once at startup and exposes a simple REST API endpoint. It is designed to be used by:

- MCP servers (like `jsl-deid-mcp-server-v2`)
- Custom agents and applications
- Any HTTP client

## API Endpoint

### POST /deidentify

Deidentify Protected Health Information (PHI) from clinical text.

**Request:**

```json
{
  "text": "Dr. John Lee treated patient Emma Wilson, age 50, on 11/05/2024.",
  "mode": "both"
}
```

**Response:**

```json
{
  "masked": "Dr. <DOCTOR> treated patient <PATIENT>, age <AGE>, on <DATE>.",
  "obfuscated": "Dr. Jane Smith treated patient Maria Garcia, age 45, on 03/22/2023."
}
```

**Modes:**

| Mode | Description |
|------|-------------|
| `masked` | Replace PHI with entity labels (e.g., `<PATIENT>`, `<DATE>`) |
| `obfuscated` | Replace PHI with realistic fake values |
| `both` | Return both masked and obfuscated versions |

### GET /health

Health check endpoint.

```json
{
  "status": "healthy",
  "pipeline_loaded": true
}
```

## Supported PHI Entities

The pipeline detects and deidentifies 30+ PHI entity types:

- **Names**: PATIENT, DOCTOR, USERNAME
- **Locations**: HOSPITAL, CITY, STATE, COUNTRY, STREET, ZIP
- **Dates/Times**: DATE, AGE
- **Contact**: PHONE, FAX, EMAIL, URL
- **IDs**: MEDICALRECORD, SSN, IDNUM, ACCOUNT, LICENSE, DLN, PLATE, VIN
- **Other**: ORGANIZATION, HEALTHPLAN, PROFESSION, DEVICE, BIOID

## Quick Start

### 1. Set up your license file

Copy the example file and fill in your credentials:

```bash
cp spark_jsl.json.example spark_jsl.json
# Edit spark_jsl.json with your actual JSL license credentials
```

Or if you already have a license file:

```bash
cp /path/to/your/spark_jsl.json ./spark_jsl.json
```

### 2. Set environment variable

```bash
export JSL_SECRET=$(jq -r '.SECRET' spark_jsl.json)
```

### 3. Build and run

```bash
docker compose up --build
```

First run will:
1. Build the container (~5-10 min)
2. Download the deidentification pipeline (~1.5 GB)
3. Warm up the pipeline

### 4. Test the API

```bash
curl -X POST http://localhost:9000/deidentify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Dr. John Lee treated patient Emma Wilson, age 50.",
    "mode": "both"
  }'
```

## Python Client Example

```python
import requests

def deidentify(text: str, mode: str = "both") -> dict:
    response = requests.post(
        "http://localhost:9000/deidentify",
        json={"text": text, "mode": mode}
    )
    response.raise_for_status()
    return response.json()

# Usage
result = deidentify("Dr. John Lee treated patient Emma Wilson, age 50.")
print(result["masked"])
print(result["obfuscated"])
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_PATH` | `/run/secrets/spark_jsl.json` | Path to license file |
| `CACHE_PRETRAINED` | `/data/cache_pretrained` | Model cache directory |
| `PIPELINE_NAME` | `clinical_deidentification` | Pipeline to load |
| `SPARK_DRIVER_MEMORY` | `8G` | Spark driver memory |
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `9000` | Server port |

## Docker Requirements

- **Build-time**: `JSL_SECRET` environment variable for private PyPI access
- **Runtime**: `spark_jsl.json` license file mounted as Docker secret
- **Platform**: `linux/amd64` (Rosetta 2 on Apple Silicon)
- **Memory**: 8G reserved, 12G limit recommended

## License

Requires John Snow Labs Healthcare NLP license. Contact [John Snow Labs](https://www.johnsnowlabs.com/) for licensing.
