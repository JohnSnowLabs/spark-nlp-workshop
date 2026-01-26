#!/usr/bin/env python3
"""
© John Snow Labs 2025
LangChain/LangGraph integration example.

This script demonstrates how to integrate the MCP deidentification server
with LangChain agents and LangGraph workflows.

Usage:
    python langchain_example.py

Requirements:
    pip install requests langchain langchain-openai
"""

import json
import requests
from typing import Optional
from langchain.tools import Tool, StructuredTool
from langchain.pydantic_v1 import BaseModel, Field


# ============================================================================
# MCP Client (reusable)
# ============================================================================

class DeidMCPClient:
    """Lightweight MCP client for deidentification."""
    
    def __init__(self, url: str = "http://localhost:8000/mcp"):
        self.url = url
        self.session_id: Optional[str] = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        self._request_id = 0
    
    def _request(self, method: str, params: dict = None) -> dict:
        headers = self.headers.copy()
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        self._request_id += 1
        payload = {"jsonrpc": "2.0", "id": self._request_id, "method": method}
        if params:
            payload["params"] = params
        
        response = requests.post(self.url, headers=headers, json=payload, timeout=120)
        
        if "mcp-session-id" in response.headers:
            self.session_id = response.headers["mcp-session-id"]
        
        text = response.text
        if text.startswith("event:"):
            for line in text.split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:])
        return response.json()
    
    def initialize(self):
        if not self.session_id:
            self._request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "langchain-agent", "version": "1.0"}
            })
    
    def deidentify(self, text: str, mode: str = "both") -> dict:
        self.initialize()
        result = self._request("tools/call", {
            "name": "deidentify_text",
            "arguments": {"text": text, "mode": mode}
        })
        content = result.get("result", {}).get("content", [])
        if content and content[0].get("type") == "text":
            return json.loads(content[0]["text"])
        return {"error": "Unexpected response"}


# ============================================================================
# LangChain Tool Definitions
# ============================================================================

# Initialize global client
_mcp_client = DeidMCPClient()


def deidentify_text_func(text: str) -> str:
    """
    Deidentify PHI from clinical text.
    Returns both masked and obfuscated versions.
    """
    result = _mcp_client.deidentify(text, mode="both")
    return json.dumps(result, indent=2)


def mask_phi_func(text: str) -> str:
    """
    Replace PHI with entity labels (e.g., <PATIENT>, <DOCTOR>).
    Use this when you need to see what types of PHI are in the text.
    """
    result = _mcp_client.deidentify(text, mode="masked")
    return result.get("masked", "Error processing text")


def obfuscate_phi_func(text: str) -> str:
    """
    Replace PHI with realistic fake values.
    Use this when you need realistic-looking but fake clinical text.
    """
    result = _mcp_client.deidentify(text, mode="obfuscated")
    return result.get("obfuscated", "Error processing text")


# Simple Tool (single string input)
deidentify_tool = Tool(
    name="deidentify_clinical_text",
    description=(
        "Deidentify Protected Health Information (PHI) from clinical text. "
        "Detects and replaces patient names, doctor names, dates, phone numbers, "
        "email addresses, medical record numbers, SSNs, and 30+ other PHI types. "
        "Returns both masked (with labels like <PATIENT>) and obfuscated (with fake values) versions."
    ),
    func=deidentify_text_func
)

mask_tool = Tool(
    name="mask_phi",
    description=(
        "Replace PHI in clinical text with entity labels like <PATIENT>, <DOCTOR>, <DATE>. "
        "Useful for analyzing what PHI is present in the text."
    ),
    func=mask_phi_func
)

obfuscate_tool = Tool(
    name="obfuscate_phi",
    description=(
        "Replace PHI in clinical text with realistic fake values. "
        "Useful for creating realistic test data or sharing clinical text safely."
    ),
    func=obfuscate_phi_func
)


# ============================================================================
# Structured Tool (with mode parameter)
# ============================================================================

class DeidentifyInput(BaseModel):
    """Input schema for deidentify tool."""
    text: str = Field(description="Clinical text containing PHI to deidentify")
    mode: str = Field(
        default="both",
        description="Output mode: 'masked' (labels), 'obfuscated' (fake values), or 'both'"
    )


def structured_deidentify(text: str, mode: str = "both") -> str:
    """Deidentify with mode selection."""
    result = _mcp_client.deidentify(text, mode=mode)
    if mode == "masked":
        return result.get("masked", "Error")
    elif mode == "obfuscated":
        return result.get("obfuscated", "Error")
    return json.dumps(result, indent=2)


structured_deidentify_tool = StructuredTool.from_function(
    func=structured_deidentify,
    name="deidentify_phi",
    description=(
        "Deidentify Protected Health Information (PHI) from clinical text. "
        "Supports three modes: 'masked' (replace with labels), "
        "'obfuscated' (replace with fake values), or 'both'."
    ),
    args_schema=DeidentifyInput
)


# ============================================================================
# Export all tools for easy import
# ============================================================================

# For simple agents that need one tool
DEID_TOOL = deidentify_tool

# For agents that need more control
DEID_TOOLS = [mask_tool, obfuscate_tool]

# For agents that support structured tools
DEID_STRUCTURED_TOOL = structured_deidentify_tool


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LangChain Integration Example")
    print("=" * 60)
    
    # Test text
    test_text = """
    Dr. John Lee from Royal Medical Clinic in Chicago treated patient 
    Emma Wilson, age 50, on 11/05/2024. Contact: 444-456-7890.
    """
    
    print("\n📋 Original Text:")
    print(test_text.strip())
    
    # Test simple tool
    print("\n" + "=" * 60)
    print("Using deidentify_tool:")
    print("=" * 60)
    result = deidentify_tool.run(test_text)
    print(result)
    
    # Test mask tool
    print("\n" + "=" * 60)
    print("Using mask_tool:")
    print("=" * 60)
    result = mask_tool.run(test_text)
    print(result)
    
    # Test obfuscate tool
    print("\n" + "=" * 60)
    print("Using obfuscate_tool:")
    print("=" * 60)
    result = obfuscate_tool.run(test_text)
    print(result)
    
    # Test structured tool
    print("\n" + "=" * 60)
    print("Using structured_deidentify_tool (mode=masked):")
    print("=" * 60)
    result = structured_deidentify_tool.run({"text": test_text, "mode": "masked"})
    print(result)
    
    print("\n✅ All examples completed!")
    
    # Show how to use in an agent
    print("\n" + "=" * 60)
    print("Usage in LangChain Agent:")
    print("=" * 60)
    print("""
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate

# Import tools from this module
from langchain_example import DEID_TOOLS  # or DEID_TOOL, DEID_STRUCTURED_TOOL

# Create agent
llm = ChatOpenAI(model="gpt-4", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can deidentify clinical text."),
    ("human", "{input}"),
])

agent = create_openai_functions_agent(llm, DEID_TOOLS, prompt)
agent_executor = AgentExecutor(agent=agent, tools=DEID_TOOLS, verbose=True)

# Run
result = agent_executor.invoke({
    "input": "Please mask the PHI in this text: Dr. Smith treated John Doe."
})
""")
