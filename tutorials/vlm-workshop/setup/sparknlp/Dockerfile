FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

LABEL description="Spark NLP for Healthcare FastAPI server (GPU-enabled)"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get install -y \
    openjdk-8-jdk-headless \
    python3-pip \
    python3.10-dev \
    && rm -rf /var/lib/apt/lists/*

ENV HOME=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/ \
    PATH=/usr/lib/jvm/java-8-openjdk-amd64/bin:/app/.local/bin:$PATH \
    TF_CPP_MIN_LOG_LEVEL=2 \
    PYTHONIOENCODING=utf-8 \
    PYSPARK_PYTHON=python3 \
    PYSPARK_DRIVER_PYTHON=python3

# Public dependencies
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# JSL licensed package — requires SECRET from license JSON
ARG JSL_SECRET
ARG JSL_VERSION=6.3.0
RUN pip3 install --no-cache-dir \
    --extra-index-url "https://pypi.johnsnowlabs.com/${JSL_SECRET}" \
    "spark-nlp-jsl==${JSL_VERSION}" \
    && rm -rf /tmp/*

WORKDIR /app
COPY app/ /app/

EXPOSE 5000
ENTRYPOINT ["uvicorn", "main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "5000"]
