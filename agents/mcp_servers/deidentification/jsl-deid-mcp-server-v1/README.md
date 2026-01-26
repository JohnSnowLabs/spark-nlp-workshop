# JSL Deidentification MCP Server

© John Snow Labs 2026

A Docker-based MCP (Model Context Protocol) server for clinical text deidentification using Spark NLP Healthcare.

## Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────────────┐
│  Client/Agent   │ ────────────► │     MCP Server v1       │
│  (Cursor, etc.) │   port 8000   │  ┌───────────────────┐  │
└─────────────────┘               │  │  Embedded Pipeline │  │
                                  │  │  (Spark NLP)       │  │
                                  │  └───────────────────┘  │
                                  │      [Docker Container] │
                                  └─────────────────────────┘
```

This is the **monolithic** version with the Spark NLP pipeline embedded directly in the MCP server. For a lightweight alternative, see [jsl-deid-mcp-server-v2](../jsl-deid-mcp-server-v2/README.md) which separates the MCP server from the pipeline service.

## Features

- **Single-load pipeline**: Loads the `clinical_deidentification` pipeline once at startup
- **Warmup**: Pre-warms the pipeline to minimize first-request latency
- **Persistent cache**: Model cache survives container restarts via Docker volumes
- **Multiple output modes**: `masked`, `obfuscated`, or `both`
- **Streamable HTTP transport**: Compatible with Cursor, VS Code Copilot, Claude Code CLI

## Supported PHI Entities

The pipeline detects and deidentifies 30+ PHI entity types:

- **Names**: PATIENT, DOCTOR, USERNAME
- **Locations**: HOSPITAL, CITY, STATE, COUNTRY, STREET, ZIP
- **Dates/Times**: DATE, AGE
- **Contact**: PHONE, FAX, EMAIL, URL
- **IDs**: MEDICALRECORD, SSN, IDNUM, ACCOUNT, LICENSE, DLN, PLATE, VIN
- **Other**: ORGANIZATION, HEALTHPLAN, PROFESSION, DEVICE, BIOID

## Prerequisites

- Docker & Docker Compose
- John Snow Labs Healthcare license (`spark_jsl.json`)
- 12GB+ RAM recommended

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
# Extract SECRET from your license file for Docker build
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

Subsequent runs use cached models and start faster.

### 4. Test the service

```bash
# Run the test script
python3 test_server.py

# Or use the bash version
./test_server.sh
```

## Client Configuration

### Cursor IDE

**Config file location:**
- macOS/Linux: `~/.cursor/mcp.json`
- Windows: `%APPDATA%\Cursor\mcp.json`

```json
{
  "mcpServers": {
    "jsl-deid": {
      "url": "http://localhost:8000/mcp",
      "transport": "streamable-http"
    }
  }
}
```

Restart Cursor after updating the config.

### VS Code (GitHub Copilot)

Add to VS Code `settings.json` (`Cmd/Ctrl + Shift + P` → "Preferences: Open User Settings (JSON)"):

```json
{
  "mcp.servers": {
    "jsl-deid": {
      "url": "http://localhost:8000/mcp",
      "type": "http"
    }
  }
}
```

Restart VS Code after updating.

### Claude Code CLI

```bash
claude mcp add jsl-deid --transport http --url http://localhost:8000/mcp
```

**Note:** Claude Desktop (GUI) only supports stdio transport and is not compatible with this HTTP-based server. Use the CLI instead.

## Custom MCP Clients & Agents

For custom agents and MCP clients, use the HTTP API directly.

### Simple Python Client

```python
import requests
import json

class DeidMCPClient:
    """Lightweight MCP client for deidentification."""
    
    def __init__(self, url="http://localhost:8000/mcp"):
        self.url = url
        self.session_id = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
    
    def _request(self, method, params=None, req_id=1):
        headers = self.headers.copy()
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        payload = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params:
            payload["params"] = params
        
        resp = requests.post(self.url, headers=headers, json=payload, timeout=120)
        
        if "mcp-session-id" in resp.headers:
            self.session_id = resp.headers["mcp-session-id"]
        
        # Parse SSE response
        text = resp.text
        if text.startswith("event:"):
            for line in text.split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:])
        return resp.json()
    
    def initialize(self):
        return self._request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "custom-agent", "version": "1.0"}
        })
    
    def deidentify(self, text, mode="both"):
        if not self.session_id:
            self.initialize()
        
        result = self._request("tools/call", {
            "name": "deidentify_text",
            "arguments": {"text": text, "mode": mode}
        }, req_id=2)
        
        return json.loads(result["result"]["content"][0]["text"])

# Usage
client = DeidMCPClient()
result = client.deidentify("Dr. John Smith treated patient Jane Doe on 01/15/2024.")
print(result["masked"])      # Dr. <DOCTOR> treated patient <PATIENT> on <DATE>.
print(result["obfuscated"])  # Dr. Michael Brown treated patient Sarah Wilson on 03/22/2023.
```

### LangChain Integration

```python
from langchain.tools import Tool

client = DeidMCPClient()

deidentify_tool = Tool(
    name="deidentify_text",
    description="Deidentify PHI from clinical text. Returns masked and obfuscated versions.",
    func=lambda text: client.deidentify(text, mode="both")
)

# Use in your LangChain/LangGraph agent
tools = [deidentify_tool]
```

### Example Scripts

Full working examples are available in the `examples/` directory:

```bash
# Simple HTTP client (no dependencies except requests)
python3 examples/mcp_client_example.py

# MCP SDK async client (requires: pip install mcp httpx)
python3 examples/mcp_sdk_example.py

# LangChain integration (requires: pip install langchain requests)
python3 examples/langchain_example.py
```

## API Reference

### Tool: `deidentify_text`

Deidentify Protected Health Information (PHI) from clinical text.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | - | Clinical text containing PHI |
| `mode` | string | No | `"both"` | Output format: `"masked"`, `"obfuscated"`, or `"both"` |

**Output Modes:**

- `"masked"`: Replace PHI with entity labels (e.g., `<PATIENT>`, `<DATE>`)
- `"obfuscated"`: Replace PHI with realistic fake values
- `"both"`: Return both versions

**Example Response:**

```json
{
  "masked": "Dr. <DOCTOR> treated <PATIENT> on <DATE>.",
  "obfuscated": "Dr. Jane Smith treated Maria Garcia on 03/22/2023."
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_PATH` | `/run/secrets/spark_jsl.json` | Path to license file |
| `CACHE_PRETRAINED` | `/data/cache_pretrained` | Model cache directory |
| `PIPELINE_NAME` | `clinical_deidentification` | Pipeline to load |
| `SPARK_DRIVER_MEMORY` | `8G` | Spark driver memory |
| `SERVER_HOST` | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | `8000` | Server port |

## Volume Mounts

| Volume | Container Path | Purpose |
|--------|---------------|---------|
| `cache_pretrained` | `/data/cache_pretrained` | Pretrained model cache |
| `jsl_home` | `/root/.johnsnowlabs` | JSL licenses, jars, wheels |

## Security Notes

- **Secret file**: Never baked into image; mounted at runtime via Docker secrets
- **PHI logging**: Disabled; only request size and latency are logged
- **TLS**: Use a reverse proxy (nginx, Traefik) for HTTPS in production

## Troubleshooting

### Container fails to start

1. Check secret file exists: `ls -la spark_jsl.json`
2. Verify JSON is valid: `jq . spark_jsl.json`
3. Check logs: `docker compose logs -f`

### Out of memory

Increase memory limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 16G
```

### Slow first request

The pipeline needs warmup. If warmup is skipped or fails, first request will be slow (~30s).

## License

Requires John Snow Labs Healthcare NLP license. Contact [John Snow Labs](https://www.johnsnowlabs.com/) for licensing.
