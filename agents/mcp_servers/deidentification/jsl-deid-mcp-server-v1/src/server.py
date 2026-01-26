# © John Snow Labs 2025
"""FastMCP server for clinical text deidentification."""

import time
from typing import Literal

from mcp.server.fastmcp import FastMCP

from .config import SERVER_HOST, SERVER_PORT, load_secret, logger
from .pipeline import (
    create_spark_session,
    extract_deidentified_text,
    load_pipeline,
    warmup_pipeline,
)

# Global state for pipeline (initialized once at startup)
_pipeline = None
_spark = None


def initialize():
    """Initialize Spark session and pipeline (called once at module load)."""
    global _pipeline, _spark
    
    logger.info("=" * 50)
    logger.info("JSL Deidentification MCP Server initializing...")
    logger.info("=" * 50)
    
    # Load credentials (contains SECRET, SPARK_NLP_LICENSE, AWS creds, etc.)
    credentials = load_secret()
    
    # Initialize Spark and pipeline (pass full credentials for license setup)
    _spark = create_spark_session(credentials)
    _pipeline = load_pipeline()
    warmup_pipeline(_pipeline)
    
    logger.info("Server ready to accept requests")


# Initialize on module load
initialize()


# Create MCP server instance
mcp = FastMCP(name="jsl-deid-server")


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
    
    # Run pipeline
    result = _pipeline.fullAnnotate(text)
    
    # Extract output based on mode
    output = extract_deidentified_text(result, mode)
    
    # Log metrics (no PHI)
    elapsed_ms = (time.time() - start_time) * 1000
    logger.info(f"Deidentify completed: {elapsed_ms:.0f}ms")
    
    return output


def main():
    """Run the MCP server with Streamable HTTP transport."""
    import uvicorn
    
    logger.info(f"Starting MCP server on {SERVER_HOST}:{SERVER_PORT}")
    
    # Get the ASGI app from FastMCP and run with uvicorn for explicit host binding
    app = mcp.streamable_http_app()
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT, log_level="info")


if __name__ == "__main__":
    main()
