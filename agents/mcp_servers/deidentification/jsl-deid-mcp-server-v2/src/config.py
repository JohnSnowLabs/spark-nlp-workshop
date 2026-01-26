# © John Snow Labs 2025
"""Configuration for JSL Deidentification MCP Server v2."""

import logging
import os

# Logging setup - no PHI in logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("jsl-deid-mcp-v2")

# Deid Service API endpoint
DEID_SERVICE_URL = os.getenv("DEID_SERVICE_URL", "http://localhost:9000")

# MCP Server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8001"))

# Request timeout (seconds)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))
