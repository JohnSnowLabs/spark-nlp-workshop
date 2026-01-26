# © John Snow Labs 2025
# Dockerfile for JSL Deidentification REST API Service

# Use Bookworm (Debian 12) which has OpenJDK 17 available
FROM python:3.11-slim-bookworm

# Install system dependencies
# - Java 17: Required for Spark NLP (PySpark 3.4.x compatible)
# - curl: For uv installation and health checks
# - procps: For ps command required by Spark scripts
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set JAVA_HOME - create symlink for architecture independence
RUN ln -s /usr/lib/jvm/java-17-openjdk-* /usr/lib/jvm/java-17-openjdk || true
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk
ENV JOHNSNOWLABS_HOME=/root/.johnsnowlabs
ENV PYTHONUNBUFFERED=1

# Create cache directories
RUN mkdir -p /data/cache_pretrained /root/.johnsnowlabs

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Build argument for JSL secret (used during pip install)
ARG JSL_SECRET

# Install Python dependencies
# 1. Install base packages from PyPI
RUN uv pip install --system fastapi uvicorn pydantic pyspark==3.4.1 spark-nlp==6.2.0 cloudpickle numpy pandas

# 2. Install spark-nlp-jsl from JSL PyPI (requires secret token)
RUN pip install --no-cache-dir spark-nlp-jsl==6.2.0 \
    --extra-index-url https://pypi.johnsnowlabs.com/${JSL_SECRET}

# Expose API server port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=60s --timeout=30s --start-period=600s --retries=5 \
    CMD curl -sf http://localhost:9000/health || exit 1

# Run server
CMD ["python", "-m", "src.server"]
