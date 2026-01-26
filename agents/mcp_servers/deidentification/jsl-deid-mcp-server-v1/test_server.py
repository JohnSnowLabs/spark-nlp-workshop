#!/usr/bin/env python3
"""
© John Snow Labs 2025
Test script for JSL Deidentification MCP Server
"""

import json
import sys
import requests
from typing import Dict, Any

MCP_URL = "http://localhost:8000/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}


def parse_sse_response(response_text: str) -> Dict[str, Any]:
    """Parse Server-Sent Events (SSE) response from MCP server."""
    for line in response_text.split("\n"):
        if line.startswith("data: "):
            return json.loads(line[6:])  # Remove "data: " prefix
    raise ValueError("No data line found in SSE response")


def initialize_session() -> str:
    """Initialize MCP session and return session ID."""
    print("1. Initializing MCP session...")
    response = requests.post(
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
    
    session_id = response.headers.get("mcp-session-id")
    if not session_id:
        raise RuntimeError(f"Failed to get session ID. Response: {response.text}")
    
    print(f"   ✅ Session initialized: {session_id}")
    return session_id


def list_tools(session_id: str) -> None:
    """List available MCP tools."""
    print("\n2. Listing available tools...")
    response = requests.post(
        MCP_URL,
        headers={**HEADERS, "mcp-session-id": session_id},
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
    )
    
    data = parse_sse_response(response.text)
    tools = data.get("result", {}).get("tools", [])
    
    tool_names = [tool["name"] for tool in tools]
    if "deidentify_text" in tool_names:
        print(f"   ✅ Found {len(tools)} tool(s): {', '.join(tool_names)}")
    else:
        print(f"   ❌ Tool 'deidentify_text' not found. Available: {tool_names}")
        sys.exit(1)


def test_deidentify(session_id: str, mode: str, expected_keys: list) -> Dict[str, str]:
    """Test deidentify_text tool with specified mode."""
    test_text = (
        "Dr. John Smith from General Hospital in Boston treated patient "
        "Jane Doe, age 35, on 01/15/2024. Contact: 555-123-4567. "
        "MRN: 98765432."
    )
    
    print(f"\n3. Testing deidentify_text (mode: {mode})...")
    print(f"   Input: {test_text[:60]}...")
    
    response = requests.post(
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
                    "mode": mode
                }
            }
        }
    )
    
    data = parse_sse_response(response.text)
    
    if data.get("result", {}).get("isError"):
        error = data["result"]["content"][0]["text"]
        print(f"   ❌ Error: {error}")
        sys.exit(1)
    
    result_text = data["result"]["content"][0]["text"]
    result = json.loads(result_text)
    
    # Validate expected keys
    missing_keys = [key for key in expected_keys if key not in result]
    if missing_keys:
        print(f"   ❌ Missing keys: {missing_keys}")
        print(f"   Result: {json.dumps(result, indent=2)}")
        sys.exit(1)
    
    print(f"   ✅ Success! Got keys: {list(result.keys())}")
    
    # Display results
    for key in expected_keys:
        value = result[key]
        preview = value[:80] + "..." if len(value) > 80 else value
        print(f"   {key}: {preview}")
    
    return result


def main():
    """Run all tests."""
    print("=" * 50)
    print("JSL Deidentification MCP Server Test")
    print("=" * 50)
    print()
    
    # Check server is running (use POST since MCP requires POST)
    print("0. Checking server status...")
    try:
        response = requests.post(
            MCP_URL,
            headers=HEADERS,
            json={"jsonrpc": "2.0", "id": 0, "method": "ping"},
            timeout=5
        )
        # 200 or 400 means server is running (400 = invalid method but server responds)
    except requests.exceptions.ConnectionError:
        print("   ❌ Server is not running at", MCP_URL)
        print("   Start it with: docker compose up -d")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Error connecting to server: {e}")
        sys.exit(1)
    
    print("   ✅ Server is reachable")
    
    # Initialize session
    try:
        session_id = initialize_session()
    except Exception as e:
        print(f"❌ Failed to initialize session: {e}")
        sys.exit(1)
    
    # List tools
    try:
        list_tools(session_id)
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        sys.exit(1)
    
    # Test masked mode
    try:
        masked_result = test_deidentify(session_id, "masked", ["masked"])
        if "<DOCTOR>" not in masked_result["masked"]:
            print("   ⚠️  Warning: Masked result doesn't contain expected entity labels")
    except Exception as e:
        print(f"❌ Masked mode test failed: {e}")
        sys.exit(1)
    
    # Test obfuscated mode
    try:
        obfuscated_result = test_deidentify(session_id, "obfuscated", ["obfuscated"])
    except Exception as e:
        print(f"❌ Obfuscated mode test failed: {e}")
        sys.exit(1)
    
    # Test both mode
    try:
        both_result = test_deidentify(session_id, "both", ["masked", "obfuscated"])
    except Exception as e:
        print(f"❌ Both mode test failed: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("=" * 50)
    print("\nServer is ready for use with:")
    print("  - Cursor IDE")
    print("  - VS Code (GitHub Copilot)")
    print("  - Claude Code CLI")
    print("  - Custom MCP clients (see examples/)")
    print("\nSee README.md for client configuration details.")


if __name__ == "__main__":
    main()
