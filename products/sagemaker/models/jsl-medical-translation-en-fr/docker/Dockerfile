FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install --no-install-recommends -y \
        python3 \
        python3-dev \
        python3-pip \
        openjdk-8-jdk \
        curl && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
        && mkdir -p /app/model_cache
        
# Copy necessary files
COPY app.py /app/

# Install dependencies
RUN pip install --no-cache-dir \
        peft==0.11.1 \
        sentencepiece==0.2.0 \
        fastapi \
        uvicorn


# Setup FastAPI app
WORKDIR /app
COPY serve /opt/program/serve
RUN chmod 755 /opt/program/serve
ENV PATH=/opt/program:${PATH}
