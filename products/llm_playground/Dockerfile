# app/Dockerfile
FROM python:3.10-slim AS builder
RUN apt-get update && apt-get install -y build-essential git
RUN pip3 install -U pip &&  pip3 install boto3 requests black isort
WORKDIR /app

COPY requirements.txt start.sh /tmp/
ARG OO
ARG EO
ARG BO
ENV OO=${OO}
ENV EO=${EO}
ENV BO=${BO}
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip3 install -r /tmp/requirements.txt
COPY app .

RUN pip3 install --upgrade awscli

# Configure pip to use AWS CodeArtifact
ARG CODEARTIFACT_TOKEN

RUN --mount=type=secret,id=catoken \
    sh -c ' \
        export CODEARTIFACT_AUTH_TOKEN="$(cat /run/secrets/catoken)" \
        && pip install --no-cache-dir --no-deps "encryptor-obfuscator==0.1" "jsl-i==1.1" \
        --extra-index-url "https://aws:${CODEARTIFACT_TOKEN}:@johnsnowlabs-175460536396.d.codeartifact.us-east-2.amazonaws.com/pypi/protecto/simple/" \
    '

RUN sh /tmp/start.sh

FROM nvidia/cuda:12.0.1-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y                                      \
    && apt-get install -y                                  \
    git                                                    \
    openjdk-8-jdk-headless                                 \
    python3-pip                                            \
    python3.10-dev

ARG EO
ARG BO
ENV HOME=/app                                                         \
    EO=${EO}                                                          \
    BO=${BO}                                                          \
    PYTHONDONTWRITEBYTECODE=1                                         \
    JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/                      \
    PATH=/usr/lib/jvm/java-8-openjdk-amd64/bin:/app/.local/bin:$PATH  \
    TF_CPP_MIN_LOG_LEVEL=2                                            \
    PYTHONIOENCODING=utf-8                                            \
    CUDA_HOME=/usr/local/cuda                                         \
    PYTHONPATH=${PYTHONPATH}:/                                        \
    PYSPARK_PYTHON=python3                                            \
    HF_HOME=/opt/.prop                                                \
    PYSPARK_DRIVER_PYTHON=python3

COPY requirements-with-cli.txt /tmp/
# python package installation
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/dist-packages
RUN pip3 install --no-cache-dir -r /tmp/requirements-with-cli.txt

# Cleanup
RUN rm -f /usr/bin/python3                                                               \
    && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* /usr/share/man/* /usr/share/doc/*   \
    && ln -s /usr/bin/python3.10 /usr/bin/python3                                        \
    && apt-get purge --remove linux-libc-dev git -y                                          \
    && apt-get autoremove -y                                                             \
    && apt-get clean


RUN chown -R nobody:nogroup /app
COPY --from=builder /app /app
COPY --from=builder /opt/ /opt/
#CMD ["sleep", "infinity"]
CMD ["python3", "-m", "uvicorn", "main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "5000"]
# python3 -m uvicorn main:app --workers 1 --host 0.0.0.0 --port 5000 --reload