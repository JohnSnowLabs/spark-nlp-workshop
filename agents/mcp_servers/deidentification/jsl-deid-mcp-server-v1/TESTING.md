# Testing Guide - JSL Deidentification MCP Server

© John Snow Labs 2026

Bu dokümanda servisi test etmek için adım adım talimatlar bulunmaktadır.

## 1. Manuel Testler

### 1.1. Basit curl Testi

```bash
# 1. MCP session başlat
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
  }')

# Session ID'yi çıkar
SESSION_ID=$(curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -D - -o /dev/null \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' 2>/dev/null | grep -i mcp-session-id | cut -d: -f2 | tr -d ' \r')

echo "Session ID: $SESSION_ID"

# 2. deidentify_text tool'unu çağır
curl -s -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "deidentify_text",
      "arguments": {
        "text": "Dr. John Lee from Royal Medical Clinic in Chicago treated patient Emma Wilson, age 50, on 11/05/2024. Her MRN is 56467890 and contact number is 444-456-7890.",
        "mode": "both"
      }
    }
  }' | python3 -c "import sys,json;d=json.loads(sys.stdin.read().split('data: ')[1]);print(json.dumps(json.loads(d['result']['content'][0]['text']),indent=2))"
```

### 1.2. MCP Inspector ile Test

MCP Inspector, MCP server'ları test etmek için resmi bir araçtır:

```bash
# MCP Inspector'ı yükle (eğer yoksa)
npm install -g @modelcontextprotocol/inspector

# Server'ı test et
npx @modelcontextprotocol/inspector python -m src.server
```

**Not:** MCP Inspector stdio transport bekler, bizim server HTTP transport kullanıyor. HTTP için alternatif:

```bash
# HTTP endpoint'i test et
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jq .
```

### 1.3. Python Client ile Test

```python
#!/usr/bin/env python3
"""Test script for JSL Deidentification MCP Server"""

import requests
import json

MCP_URL = "http://localhost:8000/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

# 1. Initialize session
init_response = requests.post(
    MCP_URL,
    headers=HEADERS,
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "python-test", "version": "1.0.0"}
        }
    }
)

# Extract session ID from response headers
session_id = init_response.headers.get("mcp-session-id")
print(f"Session ID: {session_id}")

# 2. List available tools
tools_response = requests.post(
    MCP_URL,
    headers={**HEADERS, "mcp-session-id": session_id},
    json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
)
print("\nAvailable tools:")
print(json.dumps(tools_response.json(), indent=2))

# 3. Call deidentify_text
test_text = """
Dr. Sarah Johnson from Memorial Hospital in Boston treated patient 
Michael Chen, age 45, on 12/15/2024. Patient's MRN is 12345678 
and phone number is 617-555-1234.
"""

deid_response = requests.post(
    MCP_URL,
    headers={**HEADERS, "mcp-session-id": session_id},
    json={
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "deidentify_text",
            "arguments": {
                "text": test_text,
                "mode": "both"
            }
        }
    }
)

# Parse SSE response
response_text = deid_response.text
if "data: " in response_text:
    data_line = [line for line in response_text.split("\n") if line.startswith("data: ")][0]
    data_json = json.loads(data_line[6:])  # Remove "data: " prefix
    result = json.loads(data_json["result"]["content"][0]["text"])
    print("\n=== Deidentification Result ===")
    print(f"Masked:\n{result['masked']}\n")
    print(f"Obfuscated:\n{result['obfuscated']}\n")
```

## 2. Cursor IDE ile Test

### 2.1. MCP Konfigürasyonu

Cursor'da MCP server'ı eklemek için:

1. Cursor ayarlarını açın: `Cmd/Ctrl + ,`
2. "MCP" veya "Model Context Protocol" arayın
3. Veya doğrudan config dosyasını düzenleyin:

**macOS/Linux:**
```bash
mkdir -p ~/.cursor
cat >> ~/.cursor/mcp.json << 'EOF'
{
  "mcpServers": {
    "jsl-deid": {
      "url": "http://localhost:8000/mcp",
      "transport": "streamable-http"
    }
  }
}
EOF
```

**Windows:**
`%APPDATA%\Cursor\mcp.json` dosyasını oluşturun:

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

### 2.2. Cursor'da Test

1. Cursor'ı yeniden başlatın
2. Chat panelinde MCP server'ın bağlandığını kontrol edin
3. Şu şekilde test edin:

```
@jsl-deid deidentify_text tool'unu kullanarak şu metni deidentify et:
"Dr. John Smith from General Hospital treated patient Jane Doe, age 35, on 01/15/2024. 
Contact: 555-123-4567. MRN: 98765432."
Mode: both
```

## 3. VS Code (GitHub Copilot) ile Test

### 3.1. MCP Extension Kurulumu

1. VS Code'da Extensions panelini açın (`Cmd/Ctrl + Shift + X`)
2. "MCP" veya "Model Context Protocol" arayın
3. Resmi MCP extension'ı yükleyin

### 3.2. Konfigürasyon

VS Code settings.json'a ekleyin (`Cmd/Ctrl + Shift + P` → "Preferences: Open User Settings (JSON)"):

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

**Not:** VS Code'da `type: "http"` kullanılır (Cursor'da `transport: "streamable-http"`).

### 3.3. Test

1. VS Code'u yeniden başlatın
2. Copilot Chat'te MCP server'ın bağlandığını kontrol edin
3. Test prompt'u:

```
Use the jsl-deid server to deidentify this text:
"Patient Mary Johnson, DOB 05/20/1980, was seen at City Hospital on 12/01/2024. 
SSN: 123-45-6789, Phone: 555-987-6543."
Return both masked and obfuscated versions.
```

## 4. Claude Code CLI ile Test

### 4.1. Konfigürasyon

Claude Code CLI HTTP transport'u destekler:

```bash
claude mcp add jsl-deid --transport http --url http://localhost:8000/mcp
```

### 4.2. Test

```bash
# Claude Code ile test
claude "Use the jsl-deid MCP server to deidentify this clinical text: 'Dr. Robert Williams from Mayo Clinic in Rochester, MN treated patient Emily Davis, age 42, on 11/20/2024. Patient ID: 45678901, Email: emily.davis@email.com, Phone: 507-555-7890.' Mode: both"
```

**Not:** Claude Desktop (GUI) yalnızca stdio transport destekler ve bu HTTP-based server ile uyumlu değildir. CLI veya Cursor/VS Code kullanın.

## 5. Test Senaryoları

### Senaryo 1: Masked Mode

```bash
# Sadece masked çıktı
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "deidentify_text",
      "arguments": {
        "text": "Dr. Smith treated patient John Doe.",
        "mode": "masked"
      }
    }
  }'
```

**Beklenen:** `{"masked": "Dr. <DOCTOR> treated patient <PATIENT>."}`

### Senaryo 2: Obfuscated Mode

```bash
# Sadece obfuscated çıktı
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "deidentify_text",
      "arguments": {
        "text": "Dr. Smith treated patient John Doe.",
        "mode": "obfuscated"
      }
    }
  }'
```

**Beklenen:** `{"obfuscated": "Dr. [fake name] treated patient [fake name]."}`

### Senaryo 3: Uzun Metin

```bash
# Uzun klinik notu
LONG_TEXT="Patient presented with chest pain. Dr. Anderson from 
Memorial Hospital in New York City examined the patient on 10/15/2024. 
Patient name: Sarah Johnson, age 55, SSN: 123-45-6789, 
Phone: 212-555-1234, Email: sarah.j@email.com. 
Medical Record Number: 987654321. Address: 123 Main St, New York, NY 10001."

curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"deidentify_text\",
      \"arguments\": {
        \"text\": \"$LONG_TEXT\",
        \"mode\": \"both\"
      }
    }
  }"
```

## 6. Troubleshooting

### Server'a bağlanamıyorum

```bash
# Container'ın çalıştığını kontrol et
docker ps | grep jsl-deid

# Port'un açık olduğunu kontrol et
curl -v http://localhost:8000/mcp

# Logları kontrol et
docker compose logs -f
```

### MCP client bağlanamıyor

1. Server'ın çalıştığını doğrulayın: `curl http://localhost:8000/mcp`
2. Firewall/port erişimini kontrol edin
3. Config dosyasındaki URL'yi kontrol edin: `http://localhost:8000/mcp`
4. IDE/agent'ı yeniden başlatın

### Tool çağrısı hata veriyor

```bash
# Detaylı logları kontrol et
docker compose logs --tail 50

# Session ID'nin doğru olduğundan emin ol
# Her initialize çağrısı yeni bir session ID döner
```

## 7. Performans Testi

```bash
# Latency testi
time curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "deidentify_text",
      "arguments": {
        "text": "Dr. Smith treated patient John Doe, age 50.",
        "mode": "both"
      }
    }
  }' > /dev/null
```

**Beklenen:** İlk çağrı ~1-2 saniye, sonraki çağrılar ~500ms-1s
