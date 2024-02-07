# Use a specific Miniconda version
FROM continuumio/miniconda3:4.10.3

# Copy requirements.txt and license.json
COPY requirements.txt .
COPY license.json .

# Set environment variables
ENV CONDA_DIR=/opt/conda \
    PATH=/opt/conda/bin:$PATH \
    JAVA_HOME=/usr/lib/jvm/temurin-8-jdk-amd64/

# Update APT package repositories and install required packages
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        build-essential \
        git \
        make \
        clang \
        libboost-dev \
        postgresql-client \
        ca-certificates \
        software-properties-common \
        gnupg \
        jq \
        wget \
        apt-transport-https && \
    mkdir -p /etc/apt/keyrings && \
    wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | tee /etc/apt/keyrings/adoptium.asc && \
    echo "deb [signed-by=/etc/apt/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list && \
    apt-get update -qq && \
    apt-get install -y temurin-8-jdk

# Activate Miniconda, create environment, and install Python packages
RUN conda init bash && \
    . ~/.bashrc && \
    conda create -n myenv python=3.9 -y && \
    conda activate myenv && \
    pip install -r requirements.txt && \
    PUBLIC_VERSION=$(jq -r '.PUBLIC_VERSION' license.json) && \
    SECRET=$(jq -r '.SECRET' license.json) && \
    pip install spark-nlp==$PUBLIC_VERSION findspark && \
    pip install spark-nlp-jsl==$PUBLIC_VERSION --extra-index-url https://pypi.johnsnowlabs.com/$SECRET

# Set the default CMD command
CMD ["java", "-version"]
