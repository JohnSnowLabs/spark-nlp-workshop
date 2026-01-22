#!/usr/bin/env python3
"""
© John Snow Labs 2025
Example using official MCP Python SDK.

This script demonstrates async MCP client usage with the official SDK.

Usage:
    python mcp_sdk_example.py

Requirements:
    pip install mcp httpx
"""

import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    """Demonstrate MCP SDK usage for deidentification."""
    
    server_url = "http://localhost:8000/mcp"
    
    print("=" * 60)
    print("JSL Deidentification - MCP SDK Example")
    print("=" * 60)
    
    # Connect to server using streamable HTTP transport
    async with streamablehttp_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("✅ Connected to MCP server")
            
            # List available tools
            tools = await session.list_tools()
            print(f"\n📋 Available tools: {[t.name for t in tools.tools]}")
            
            # Example clinical text
            clinical_text = """
            Dr. John Lee from Royal Medical Clinic in Chicago treated patient 
            Emma Wilson, age 50, on 11/05/2024. Contact: 444-456-7890.
            """
            
            print("\n" + "=" * 60)
            print("Original Text:")
            print("=" * 60)
            print(clinical_text.strip())
            
            # Call deidentify_text tool
            print("\n" + "=" * 60)
            print("Deidentified (mode=both):")
            print("=" * 60)
            
            result = await session.call_tool(
                "deidentify_text",
                arguments={
                    "text": clinical_text,
                    "mode": "both"
                }
            )
            
            # Parse result
            if result.content and result.content[0].type == "text":
                output = json.loads(result.content[0].text)
                print("\n🔒 Masked:")
                print(output.get("masked", "N/A"))
                print("\n🎭 Obfuscated:")
                print(output.get("obfuscated", "N/A"))
            
            print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())
