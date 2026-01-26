#!/bin/bash
# © John Snow Labs 2025
# Test script for JSL Deidentification MCP Server

set -e

MCP_URL="http://localhost:8000/mcp"
HEADERS=(
  -H "Content-Type: application/json"
  -H "Accept: application/json, text/event-stream"
)

echo "=========================================="
echo "JSL Deidentification MCP Server Test"
echo "=========================================="
echo ""

# Check if server is running (use POST since MCP requires POST)
echo "1. Checking server status..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$MCP_URL" \
  "${HEADERS[@]}" \
  -d '{"jsonrpc":"2.0","id":0,"method":"ping"}' 2>/dev/null)

# 200 = success, 400 = server running but invalid request (acceptable)
if [ "$HEALTH_CHECK" != "200" ] && [ "$HEALTH_CHECK" != "400" ] && [ "$HEALTH_CHECK" != "000" ]; then
  # Try direct connection test
  if ! curl -s --connect-timeout 2 "$MCP_URL" > /dev/null 2>&1; then
    echo "❌ Server is not responding at $MCP_URL"
    echo "   Make sure the server is running: docker compose up -d"
    exit 1
  fi
fi
echo "✅ Server is running"
echo ""

# Initialize session
echo "2. Initializing MCP session..."
INIT_RESPONSE=$(curl -s -X POST "$MCP_URL" \
  "${HEADERS[@]}" \
  -D - \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-script", "version": "1.0.0"}
    }
  }' 2>&1)

SESSION_ID=$(echo "$INIT_RESPONSE" | grep -i "mcp-session-id" | cut -d: -f2 | tr -d ' \r')

if [ -z "$SESSION_ID" ]; then
  echo "❌ Failed to get session ID"
  echo "Response: $INIT_RESPONSE"
  exit 1
fi

echo "✅ Session initialized: $SESSION_ID"
echo ""

# List tools
echo "3. Listing available tools..."
TOOLS_RESPONSE=$(curl -s -X POST "$MCP_URL" \
  "${HEADERS[@]}" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }')

if echo "$TOOLS_RESPONSE" | grep -q "deidentify_text"; then
  echo "✅ Tool 'deidentify_text' is available"
else
  echo "❌ Tool 'deidentify_text' not found"
  echo "Response: $TOOLS_RESPONSE"
  exit 1
fi
echo ""

# Test deidentify_text with masked mode
echo "4. Testing deidentify_text (mode: masked)..."
TEST_TEXT="Dr. John Smith from General Hospital in Boston treated patient Jane Doe, age 35, on 01/15/2024. Contact: 555-123-4567."

MASKED_RESPONSE=$(curl -s -X POST "$MCP_URL" \
  "${HEADERS[@]}" \
  -H "mcp-session-id: $SESSION_ID" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 3,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"deidentify_text\",
      \"arguments\": {
        \"text\": \"$TEST_TEXT\",
        \"mode\": \"masked\"
      }
    }
  }")

# Parse SSE response
if echo "$MASKED_RESPONSE" | grep -q "data:"; then
  DATA_LINE=$(echo "$MASKED_RESPONSE" | grep "^data:" | head -1)
  JSON_DATA=$(echo "$DATA_LINE" | sed 's/^data: //')
  
  if command -v jq > /dev/null 2>&1; then
    MASKED_RESULT=$(echo "$JSON_DATA" | jq -r '.result.content[0].text' | jq -r '.masked')
  else
    # Fallback: simple extraction
    MASKED_RESULT=$(echo "$JSON_DATA" | python3 -c "import sys,json;d=json.load(sys.stdin);print(json.loads(d['result']['content'][0]['text'])['masked'])" 2>/dev/null || echo "Parse error")
  fi
  
  if echo "$MASKED_RESULT" | grep -q "<DOCTOR>"; then
    echo "✅ Masked mode working correctly"
    echo "   Result: $MASKED_RESULT"
  else
    echo "❌ Masked mode failed"
    echo "   Result: $MASKED_RESULT"
    exit 1
  fi
else
  echo "❌ Invalid response format"
  echo "Response: $MASKED_RESPONSE"
  exit 1
fi
echo ""

# Test deidentify_text with both mode
echo "5. Testing deidentify_text (mode: both)..."
BOTH_RESPONSE=$(curl -s -X POST "$MCP_URL" \
  "${HEADERS[@]}" \
  -H "mcp-session-id: $SESSION_ID" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 4,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"deidentify_text\",
      \"arguments\": {
        \"text\": \"$TEST_TEXT\",
        \"mode\": \"both\"
      }
    }
  }")

if echo "$BOTH_RESPONSE" | grep -q "data:"; then
  DATA_LINE=$(echo "$BOTH_RESPONSE" | grep "^data:" | head -1)
  JSON_DATA=$(echo "$DATA_LINE" | sed 's/^data: //')
  
  if command -v jq > /dev/null 2>&1; then
    BOTH_RESULT=$(echo "$JSON_DATA" | jq -r '.result.content[0].text' | jq -r '.')
    HAS_MASKED=$(echo "$BOTH_RESULT" | jq -r 'has("masked")')
    HAS_OBFUSCATED=$(echo "$BOTH_RESULT" | jq -r 'has("obfuscated")')
    
    if [ "$HAS_MASKED" = "true" ] && [ "$HAS_OBFUSCATED" = "true" ]; then
      echo "✅ Both mode working correctly"
      echo ""
      echo "   Masked:"
      echo "$BOTH_RESULT" | jq -r '.masked' | sed 's/^/     /'
      echo ""
      echo "   Obfuscated:"
      echo "$BOTH_RESULT" | jq -r '.obfuscated' | sed 's/^/     /'
    else
      echo "❌ Both mode failed - missing fields"
      echo "   Has masked: $HAS_MASKED"
      echo "   Has obfuscated: $HAS_OBFUSCATED"
      exit 1
    fi
  else
    # Fallback
    if echo "$BOTH_RESPONSE" | grep -q "masked" && echo "$BOTH_RESPONSE" | grep -q "obfuscated"; then
      echo "✅ Both mode working (basic check)"
    else
      echo "❌ Both mode failed"
      exit 1
    fi
  fi
else
  echo "❌ Invalid response format"
  exit 1
fi
echo ""

echo "=========================================="
echo "✅ All tests passed!"
echo "=========================================="
echo ""
echo "Server is ready for use with:"
echo "  - Cursor IDE"
echo "  - VS Code (GitHub Copilot)"
echo "  - Claude Code CLI"
echo "  - Custom MCP clients (see examples/)"
echo ""
echo "See README.md for client configuration details."
