#!/usr/bin/env python3
"""
© John Snow Labs 2025
Example MCP client for JSL Deidentification Server.

This script demonstrates how to integrate the MCP server with custom agents.

Usage:
    python mcp_client_example.py

Requirements:
    pip install requests
"""

import json
import requests
from typing import Optional


class DeidMCPClient:
    """
    Lightweight MCP client for clinical text deidentification.
    
    Compatible with custom agents, LangChain, LangGraph, and other frameworks.
    
    Example:
        client = DeidMCPClient()
        result = client.deidentify("Dr. Smith treated patient John Doe.")
        print(result["masked"])  # Dr. <DOCTOR> treated patient <PATIENT>.
    """
    
    def __init__(self, url: str = "http://localhost:8000/mcp"):
        """
        Initialize MCP client.
        
        Args:
            url: MCP server endpoint URL
        """
        self.url = url
        self.session_id: Optional[str] = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        self._request_id = 0
    
    def _next_id(self) -> int:
        """Generate next request ID."""
        self._request_id += 1
        return self._request_id
    
    def _request(self, method: str, params: dict = None) -> dict:
        """
        Send JSON-RPC request to MCP server.
        
        Args:
            method: MCP method name (e.g., "initialize", "tools/call")
            params: Method parameters
            
        Returns:
            Parsed JSON response
        """
        headers = self.headers.copy()
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method
        }
        if params:
            payload["params"] = params
        
        response = requests.post(self.url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        # Extract session ID from response headers
        if "mcp-session-id" in response.headers:
            self.session_id = response.headers["mcp-session-id"]
        
        # Parse SSE (Server-Sent Events) response format
        text = response.text
        if text.startswith("event:"):
            for line in text.split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:])
        
        # Fallback to direct JSON
        return response.json()
    
    def initialize(self) -> dict:
        """
        Initialize MCP session.
        
        Must be called before other methods (automatically called by deidentify).
        
        Returns:
            Server capabilities and info
        """
        result = self._request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "custom-mcp-client", "version": "1.0.0"}
        })
        return result.get("result", {})
    
    def list_tools(self) -> list:
        """
        List available tools on the server.
        
        Returns:
            List of tool definitions
        """
        if not self.session_id:
            self.initialize()
        
        result = self._request("tools/list")
        return result.get("result", {}).get("tools", [])
    
    def deidentify(self, text: str, mode: str = "both") -> dict:
        """
        Deidentify Protected Health Information (PHI) from clinical text.
        
        Args:
            text: Clinical text containing PHI
            mode: Output format - "masked", "obfuscated", or "both"
                  - masked: Replace PHI with entity labels (e.g., <PATIENT>)
                  - obfuscated: Replace PHI with realistic fake values
                  - both: Return both versions
        
        Returns:
            Dict with "masked" and/or "obfuscated" keys based on mode
            
        Example:
            >>> client.deidentify("Dr. Smith treated John Doe on 01/15/2024.")
            {
                "masked": "Dr. <DOCTOR> treated <PATIENT> on <DATE>.",
                "obfuscated": "Dr. Brown treated Jane Wilson on 03/22/2023."
            }
        """
        if not self.session_id:
            self.initialize()
        
        result = self._request("tools/call", {
            "name": "deidentify_text",
            "arguments": {"text": text, "mode": mode}
        })
        
        # Extract text content from MCP response
        content = result.get("result", {}).get("content", [])
        if content and content[0].get("type") == "text":
            return json.loads(content[0]["text"])
        
        return {"error": "Unexpected response format", "raw": result}
    
    def close(self):
        """Close the MCP session (optional cleanup)."""
        self.session_id = None
        self._request_id = 0


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Initialize client
    client = DeidMCPClient()
    
    # Example clinical text with PHI
    clinical_text = """
    Dr. John Lee from Royal Medical Clinic in Chicago treated patient Emma Wilson, 
    age 50, on 11/05/2024. Her medical record number is MRN-56467890 and she can be 
    reached at 444-456-7890 or emma.wilson@email.com. She was diagnosed with 
    Type 2 Diabetes and prescribed Metformin 500mg twice daily.
    """
    
    print("=" * 60)
    print("JSL Deidentification MCP Client Example")
    print("=" * 60)
    
    # List available tools
    print("\n📋 Available Tools:")
    tools = client.list_tools()
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description'][:60]}...")
    
    # Test different modes
    print("\n" + "=" * 60)
    print("Original Text:")
    print("=" * 60)
    print(clinical_text.strip())
    
    # Mode: both
    print("\n" + "=" * 60)
    print("Mode: both")
    print("=" * 60)
    result = client.deidentify(clinical_text, mode="both")
    print("\n🔒 Masked:")
    print(result.get("masked", "N/A"))
    print("\n🎭 Obfuscated:")
    print(result.get("obfuscated", "N/A"))
    
    # Mode: masked only
    print("\n" + "=" * 60)
    print("Mode: masked")
    print("=" * 60)
    result = client.deidentify(clinical_text, mode="masked")
    print(result.get("masked", "N/A"))
    
    # Mode: obfuscated only
    print("\n" + "=" * 60)
    print("Mode: obfuscated")
    print("=" * 60)
    result = client.deidentify(clinical_text, mode="obfuscated")
    print(result.get("obfuscated", "N/A"))
    
    print("\n✅ All tests completed successfully!")
