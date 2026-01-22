# © John Snow Labs 2025
"""Configuration and secret loading for JSL Deidentification MCP Server."""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Logging setup - no PHI in logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("jsl-deid-mcp")

# Secret file path (Docker secrets mount standard path)
SECRET_PATH = Path(os.getenv("SECRET_PATH", "/run/secrets/spark_jsl.json"))

# Cache directories for model persistence
CACHE_PRETRAINED = Path(os.getenv("CACHE_PRETRAINED", "/data/cache_pretrained"))
JSL_HOME = Path(os.getenv("JOHNSNOWLABS_HOME", os.path.expanduser("~/.johnsnowlabs")))

# Pipeline configuration
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "clinical_deidentification")
PIPELINE_LANG = os.getenv("PIPELINE_LANG", "en")

# Spark configuration
SPARK_DRIVER_MEMORY = os.getenv("SPARK_DRIVER_MEMORY", "8G")
SPARK_KRYO_BUFFER_MAX = os.getenv("SPARK_KRYO_BUFFER_MAX", "2000M")

# Server configuration
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))


def load_secret() -> dict[str, Any]:
    """
    Load JSL credentials from secret file.
    
    Reads /run/secrets/spark_jsl.json (Docker secrets mount).
    Fails fast with clear error if file missing or invalid.
    
    Returns:
        dict with at minimum 'SECRET' key for JSL license
        
    Raises:
        SystemExit: If secret file missing or invalid
    """
    if not SECRET_PATH.exists():
        logger.error(
            f"Secret file not found: {SECRET_PATH}\n"
            "Mount secret via Docker Compose:\n"
            "  secrets:\n"
            "    spark_jsl:\n"
            "      file: ./spark_jsl.json\n"
            "  services:\n"
            "    deid-mcp:\n"
            "      secrets:\n"
            "        - spark_jsl"
        )
        sys.exit(1)
    
    try:
        with open(SECRET_PATH, "r") as f:
            credentials = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in secret file: {e}")
        sys.exit(1)
    
    # Validate required keys
    if "SECRET" not in credentials:
        logger.error(
            "Secret file missing required 'SECRET' key.\n"
            "Expected format: {\"SECRET\": \"x.x.x-xxxxxxxxx\", ...}"
        )
        sys.exit(1)
    
    logger.info("Secret file loaded successfully")
    return credentials
