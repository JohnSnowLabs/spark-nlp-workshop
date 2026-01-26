# JSL Deidentification MCP Server v2

© John Snow Labs 2026

A lightweight MCP (Model Context Protocol) server for clinical text deidentification. This server connects to a separate `deid-service` API and requires no local pipeline loading.

## Features

- **Lightweight**: No Spark or heavy ML dependencies
- **Fast startup**: Instant startup (no pipeline loading)
- **Low memory**: ~100MB (vs 8GB+ for v1)
- **Simple deployment**: Single Python script, no Docker required
- **Multiple output modes**: `masked`, `obfuscated`, or `both`

## Prerequisites

- Python 3.10+
- Running `deid-service` instance (see [deid-service](../deid-service/README.md))

## Quick Start

### 1. Install dependencies

```bash
cd jsl-deid-mcp-server-v2
pip install -e .
```

### 2. Start deid-service (if not already running)

```bash
cd ../deid-service
docker compose up -d
```

### 3. Run MCP server

```bash
# Default: connects to http://localhost:9000
python -m src.server

# Or specify custom deid-service URL
DEID_SERVICE_URL=http://your-server:9000 python -m src.server
```

Server starts on `http://localhost:8001/mcp`

## Client Configuration

### Cursor IDE

**Config file location:**
- macOS/Linux: `~/.cursor/mcp.json`
- Windows: `%APPDATA%\Cursor\mcp.json`

```json
{
  "mcpServers": {
    "jsl-deid": {
      "url": "http://localhost:8001/mcp",
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
      "url": "http://localhost:8001/mcp",
      "type": "http"
    }
  }
}
```

Restart VS Code after updating.

### Claude Code CLI

```bash
claude mcp add jsl-deid --transport http --url http://localhost:8001/mcp
```

**Note:** Claude Desktop (GUI) only supports stdio transport. Use Claude Code CLI for HTTP servers.

### Custom Agents (Python)

```python
import requests
import json

class DeidMCPClient:
    """Simple MCP client for deidentification."""
    
    def __init__(self, url="http://localhost:8001/mcp"):
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

# Add to your agent
tools = [deidentify_tool]
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEID_SERVICE_URL` | `http://localhost:9000` | deid-service API endpoint |
| `SERVER_HOST` | `0.0.0.0` | MCP server bind address |
| `SERVER_PORT` | `8001` | MCP server port |
| `REQUEST_TIMEOUT` | `120` | API request timeout (seconds) |

## API Tool

### deidentify_text

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

## Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│  Client/Agent   │ ────────────► │  MCP Server v2  │
│  (Cursor, etc.) │               │  (port 8001)    │
└─────────────────┘               └────────┬────────┘
                                           │
                                           │ HTTP POST
                                           ▼
                                  ┌─────────────────┐
                                  │  deid-service   │
                                  │  (port 9000)    │
                                  │  [Pipeline]     │
                                  └─────────────────┘
```

## Comparison with v1

| Feature | v1 (jsl-deid-mcp-server-v1) | v2 (this) |
|---------|---------------------------|-----------|
| Pipeline loading | Yes (in MCP server) | No (uses deid-service) |
| Spark dependencies | Yes | No |
| Startup time | ~5 min | Instant |
| Memory usage | 8GB+ | ~100MB |
| Docker required | Yes | No |
| Architecture | Monolithic | Microservice |

## Troubleshooting

### "Cannot connect to deid-service"

1. Verify deid-service is running: `curl http://localhost:9000/health`
2. Check the URL: `echo $DEID_SERVICE_URL`
3. If using Docker, ensure network connectivity

### "Request timed out"

Increase timeout: `REQUEST_TIMEOUT=300 python -m src.server`

### MCP client not connecting

1. Check server is running on correct port
2. Verify URL in client config (should end with `/mcp`)
3. Restart IDE after config changes

## License

Requires John Snow Labs Healthcare NLP license for deid-service. Contact [John Snow Labs](https://www.johnsnowlabs.com/) for licensing.
