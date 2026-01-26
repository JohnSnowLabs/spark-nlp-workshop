# © John Snow Labs 2025
"""Spark NLP pipeline loader and warmup for deidentification."""

import os
import time
from typing import Any

from pyspark.sql import SparkSession

from .config import (
    CACHE_PRETRAINED,
    PIPELINE_LANG,
    PIPELINE_NAME,
    SPARK_DRIVER_MEMORY,
    SPARK_KRYO_BUFFER_MAX,
    logger,
)


def create_spark_session(credentials: dict) -> SparkSession:
    """
    Initialize Spark session with JSL Healthcare license.
    
    Args:
        credentials: Dict containing SECRET (PyPI token) and SPARK_NLP_LICENSE (license key)
        
    Returns:
        Configured SparkSession with Spark NLP Healthcare
    """
    import sparknlp_jsl
    
    # Set license environment variables from credentials
    # These are required by sparknlp_jsl.start()
    if "SPARK_NLP_LICENSE" in credentials:
        os.environ["SPARK_NLP_LICENSE"] = credentials["SPARK_NLP_LICENSE"]
        logger.info("SPARK_NLP_LICENSE environment variable set")
    
    if "SPARK_OCR_LICENSE" in credentials:
        os.environ["SPARK_OCR_LICENSE"] = credentials["SPARK_OCR_LICENSE"]
    
    # Also set AWS credentials if present (for model downloads)
    for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]:
        if key in credentials:
            os.environ[key] = credentials[key]
    
    # PyPI secret for package downloads
    secret = credentials.get("SECRET", "")
    
    params = {
        "spark.driver.memory": SPARK_DRIVER_MEMORY,
        "spark.kryoserializer.buffer.max": SPARK_KRYO_BUFFER_MAX,
        "spark.driver.maxResultSize": SPARK_KRYO_BUFFER_MAX,
        "spark.jsl.settings.pretrained.cache_folder": str(CACHE_PRETRAINED),
    }
    
    logger.info(f"Starting Spark session (driver memory: {SPARK_DRIVER_MEMORY})")
    start_time = time.time()
    
    spark = sparknlp_jsl.start(secret=secret, params=params)
    
    elapsed = time.time() - start_time
    logger.info(f"Spark session started in {elapsed:.2f}s")
    
    return spark


def load_pipeline(pipeline_name: str = PIPELINE_NAME, lang: str = PIPELINE_LANG) -> Any:
    """
    Load pretrained deidentification pipeline.
    
    Args:
        pipeline_name: Name of the pretrained pipeline
        lang: Language code (default: "en")
        
    Returns:
        Loaded PretrainedPipeline instance
    """
    from sparknlp.pretrained import PretrainedPipeline
    
    logger.info(f"Loading pipeline: {pipeline_name}")
    start_time = time.time()
    
    pipeline = PretrainedPipeline(pipeline_name, lang, "clinical/models")
    
    elapsed = time.time() - start_time
    logger.info(f"Pipeline loaded in {elapsed:.2f}s")
    
    return pipeline


def warmup_pipeline(pipeline: Any) -> None:
    """
    Warm up pipeline with sample text to reduce first-request latency.
    
    JVM JIT compilation and lazy initialization happen on first inference.
    Running warmup at startup ensures fast response for actual requests.
    
    Args:
        pipeline: Loaded PretrainedPipeline instance
    """
    sample_text = (
        "Dr. John Smith from General Hospital examined patient Jane Doe, "
        "age 45, on 01/15/2024. Contact: 555-123-4567."
    )
    
    logger.info("Warming up pipeline...")
    start_time = time.time()
    
    # Run inference to trigger JIT and cache
    _ = pipeline.fullAnnotate(sample_text)
    
    elapsed = time.time() - start_time
    logger.info(f"Warmup completed in {elapsed:.2f}s")


def extract_deidentified_text(result: list, mode: str) -> dict[str, str]:
    """
    Extract masked and/or obfuscated text from pipeline result.
    
    Based on notebook pattern:
    - Masked: result[0]['obfuscated'][i].metadata['masked']
    - Obfuscated: result[0]['obfuscated'][i].result
    
    Args:
        result: Pipeline fullAnnotate output
        mode: One of "masked", "obfuscated", "both"
        
    Returns:
        dict with requested output fields
    """
    output = {}
    
    # Log all result keys to understand structure
    if result:
        logger.info(f"Result keys available: {list(result[0].keys())}")
    
    if not result or not result[0].get("obfuscated"):
        # Try alternative key names
        logger.warning(f"Result keys: {result[0].keys() if result else 'empty'}")
        return {"error": "No deidentification result"}
    
    obfuscated_annotations = result[0]["obfuscated"]
    
    # Debug: Log first annotation structure
    if obfuscated_annotations:
        first_ann = obfuscated_annotations[0]
        logger.info(f"Annotation keys: result={first_ann.result[:50] if first_ann.result else None}...")
        logger.info(f"Annotation metadata type: {type(first_ann.metadata)}")
        if first_ann.metadata:
            logger.info(f"Metadata keys: {list(first_ann.metadata.keys()) if hasattr(first_ann.metadata, 'keys') else 'not a dict'}")
    
    if mode in ("masked", "both"):
        # Join masked sentences from metadata
        masked_parts = []
        for ann in obfuscated_annotations:
            # Try different ways to access metadata
            metadata = ann.metadata
            masked_value = None
            
            if metadata:
                if isinstance(metadata, dict):
                    masked_value = metadata.get("masked")
                elif hasattr(metadata, "__getitem__"):
                    try:
                        masked_value = metadata["masked"]
                    except (KeyError, TypeError):
                        pass
            
            if masked_value:
                masked_parts.append(str(masked_value))
            elif ann.result:
                # Fallback: use result if no masked version available
                masked_parts.append(str(ann.result))
        
        output["masked"] = "\n".join(masked_parts) if masked_parts else ""
    
    if mode in ("obfuscated", "both"):
        # Join obfuscated sentences from result
        obfuscated_parts = [str(ann.result) for ann in obfuscated_annotations if ann.result]
        output["obfuscated"] = "\n".join(obfuscated_parts) if obfuscated_parts else ""
    
    return output
