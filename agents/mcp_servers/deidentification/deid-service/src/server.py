# © John Snow Labs 2025
"""FastAPI REST API server for clinical text deidentification."""

import time
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

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


class DeidentifyRequest(BaseModel):
    """Request body for deidentification endpoint."""
    text: str = Field(..., description="Clinical text containing PHI to deidentify")
    mode: Literal["masked", "obfuscated", "both"] = Field(
        default="both",
        description="Output format: masked, obfuscated, or both"
    )


class DeidentifyResponse(BaseModel):
    """Response body for deidentification endpoint."""
    masked: str | None = Field(None, description="Text with PHI replaced by entity labels")
    obfuscated: str | None = Field(None, description="Text with PHI replaced by fake values")
    error: str | None = Field(None, description="Error message if processing failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize pipeline on startup, cleanup on shutdown."""
    global _pipeline, _spark
    
    logger.info("=" * 50)
    logger.info("JSL Deidentification API Service starting...")
    logger.info("=" * 50)
    
    # Load credentials
    credentials = load_secret()
    
    # Initialize Spark and pipeline
    _spark = create_spark_session(credentials)
    _pipeline = load_pipeline()
    warmup_pipeline(_pipeline)
    
    logger.info("Service ready to accept requests")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Service shutting down...")
    if _spark:
        _spark.stop()


# Create FastAPI app with lifespan handler
app = FastAPI(
    title="JSL Deidentification API",
    description="REST API for clinical text deidentification using Spark NLP Healthcare",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Verifies:
    - Pipeline is loaded
    - Spark session is alive (lightweight check without heavy operations)
    
    This is a lightweight check that doesn't perform actual inference
    to avoid impacting pipeline stability. It only verifies that
    Spark session objects exist and SparkContext is accessible.
    """
    if _pipeline is None or _spark is None:
        return {"status": "unhealthy", "pipeline_loaded": False, "spark_alive": False}
    
    # Lightweight check: verify SparkContext exists and is accessible
    # This doesn't perform any heavy operations, just checks object state
    spark_alive = False
    try:
        # Check if SparkContext exists and is not None
        if _spark.sparkContext is not None:
            # Try to access SparkContext version (lightweight operation)
            # This will fail if Spark session is dead
            _ = _spark.version
            spark_alive = True
    except (AttributeError, Exception) as e:
        # Spark session is dead or inaccessible
        logger.warning(f"Spark session health check failed: {e}")
        spark_alive = False
    
    status = "healthy" if spark_alive else "degraded"
    return {
        "status": status,
        "pipeline_loaded": _pipeline is not None,
        "spark_alive": spark_alive
    }


@app.post("/deidentify", response_model=DeidentifyResponse)
async def deidentify(request: DeidentifyRequest):
    """
    Deidentify Protected Health Information (PHI) from clinical text.
    
    Detects and removes/masks PHI entities including:
    - PATIENT, DOCTOR names
    - HOSPITAL, CITY, STREET locations
    - DATE, AGE
    - PHONE, EMAIL, SSN, ID numbers
    - And 20+ other PHI types
    
    **Modes:**
    - `masked`: Replace PHI with entity labels like `<PATIENT>`, `<DATE>`
    - `obfuscated`: Replace PHI with realistic fake values
    - `both`: Return both masked and obfuscated versions
    
    **Example:**
    ```json
    {
      "text": "Dr. John Lee treated patient Emma Wilson, age 50.",
      "mode": "both"
    }
    ```
    
    **Response:**
    ```json
    {
      "masked": "Dr. <DOCTOR> treated patient <PATIENT>, age <AGE>.",
      "obfuscated": "Dr. Jane Smith treated patient Maria Garcia, age 45."
    }
    ```
    """
    if _pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not loaded")
    
    # Check Spark session is alive before processing
    if _spark is None:
        raise HTTPException(status_code=503, detail="Spark session not initialized")
    
    try:
        # Lightweight check: verify SparkContext is accessible
        _ = _spark.version
    except (AttributeError, Exception) as e:
        logger.error(f"Spark session is dead: {e}")
        raise HTTPException(
            status_code=503,
            detail="Spark session is not available. Service may need restart."
        )
    
    start_time = time.time()
    
    # Log request (size only, no PHI)
    text_size = len(request.text)
    logger.info(f"Deidentify request: {text_size} chars, mode={request.mode}")
    
    try:
        # Run pipeline
        result = _pipeline.fullAnnotate(request.text)
        
        # Extract output based on mode
        output = extract_deidentified_text(result, request.mode)
        
        # Log metrics (no PHI)
        elapsed_ms = (time.time() - start_time) * 1000
        logger.info(f"Deidentify completed: {elapsed_ms:.0f}ms")
        
        return DeidentifyResponse(**output)
        
    except Exception as e:
        logger.error(f"Deidentification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Run the API server with uvicorn."""
    import uvicorn
    
    logger.info(f"Starting API server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(
        "src.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
