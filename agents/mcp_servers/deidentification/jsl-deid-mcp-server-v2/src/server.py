# © John Snow Labs 2025
"""FastMCP server for clinical text deidentification via deid-service API."""

import time
from typing import Literal

import requests
from mcp.server.fastmcp import FastMCP

from .config import DEID_SERVICE_URL, REQUEST_TIMEOUT, SERVER_HOST, SERVER_PORT, logger

# Create MCP server instance
mcp = FastMCP(name="jsl-deid-server-v2")


def call_deid_service(text: str, mode: str) -> dict:
    """
    Call the deid-service API to deidentify text.
    
    Args:
        text: Clinical text containing PHI
        mode: Output format (masked, obfuscated, both)
        
    Returns:
        dict with masked and/or obfuscated text
        
    Raises:
        Exception: If API call fails
    """
    url = f"{DEID_SERVICE_URL}/deidentify"
    
    try:
        response = requests.post(
            url,
            json={"text": text, "mode": mode},
            timeout=REQUEST_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to deid-service at {DEID_SERVICE_URL}")
        return {"error": f"Cannot connect to deid-service at {DEID_SERVICE_URL}. Make sure deid-service is running."}
        
    except requests.exceptions.Timeout:
        logger.error(f"Request to deid-service timed out after {REQUEST_TIMEOUT}s")
        return {"error": f"Request timed out after {REQUEST_TIMEOUT}s"}
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"deid-service returned error: {e}")
        return {"error": f"API error: {str(e)}"}


@mcp.tool()
def deidentify_text(
    text: str,
    mode: Literal["masked", "obfuscated", "both"] = "both",
) -> dict:
    """
    Deidentify Protected Health Information (PHI) from clinical text.
    
    Detects and removes/masks PHI entities including:
    - PATIENT, DOCTOR names
    - HOSPITAL, CITY, STREET locations  
    - DATE, AGE
    - PHONE, EMAIL, SSN, ID numbers
    - And 20+ other PHI types
    
    Args:
        text: Clinical text containing PHI to deidentify
        mode: Output format
            - "masked": Replace PHI with entity labels like <PATIENT>
            - "obfuscated": Replace PHI with realistic fake values
            - "both": Return both masked and obfuscated versions
            
    Returns:
        dict with requested output:
        - mode="masked": {"masked": "..."}
        - mode="obfuscated": {"obfuscated": "..."}  
        - mode="both": {"masked": "...", "obfuscated": "..."}
        
    Example:
        Input: "Dr. John Lee treated patient Emma Wilson, age 50."
        Output (mode="both"):
        {
            "masked": "Dr. <DOCTOR> treated patient <PATIENT>, age <AGE>.",
            "obfuscated": "Dr. Jane Smith treated patient Maria Garcia, age 45."
        }
    """
    start_time = time.time()
    
    # Log request (size only, no PHI)
    text_size = len(text)
    logger.info(f"Deidentify request: {text_size} chars, mode={mode}")
    
    # Call deid-service API
    result = call_deid_service(text, mode)
    
    # Log metrics (no PHI)
    elapsed_ms = (time.time() - start_time) * 1000
    logger.info(f"Deidentify completed: {elapsed_ms:.0f}ms")
    
    return result


def main():
    """Run the MCP server with Streamable HTTP transport."""
    import uvicorn
    
    logger.info("=" * 50)
    logger.info("JSL Deidentification MCP Server v2 starting...")
    logger.info(f"Deid Service URL: {DEID_SERVICE_URL}")
    logger.info("=" * 50)
    
    logger.info(f"Starting MCP server on {SERVER_HOST}:{SERVER_PORT}")
    
    # Get the ASGI app from FastMCP and run with uvicorn
    app = mcp.streamable_http_app()
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level="info")


if __name__ == "__main__":
    main()
