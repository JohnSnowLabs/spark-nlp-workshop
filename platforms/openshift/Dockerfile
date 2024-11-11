FROM continuumio/miniconda3:4.9.2

COPY environment.yml .

COPY test.py .

COPY main.py .

ENV CONDA_DIR $HOME/miniconda3

ENV PATH=$CONDA_DIR/bin:$PATH

RUN apt-get --allow-releaseinfo-change update \
    && apt-get -qq update -y \
    && apt-get install -y iputils-ping \
    && apt-get -qq install -y --no-install-recommends \
    build-essential git make clang libboost-dev postgresql-client ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get --allow-releaseinfo-change update \
    && apt-get update -y \
    && apt-get -y upgrade \
    && apt-get install -y build-essential \
    && apt-get install -y software-properties-common \
    && apt-get -y install gnupg jq \
    && wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add - \
    && apt-get -y update \
    && apt-get -y upgrade \
    && add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/ \
    && apt-get install --fix-broken \
    && apt-get update -y && apt-get install -y adoptopenjdk-8-hotspot

ENV JAVA_HOME /usr/lib/jvm/adoptopenjdk-8-hotspot-amd64/
RUN export JAVA_HOME

RUN update-java-alternatives --set adoptopenjdk-8-hotspot-amd64
RUN java -version

COPY license.json .

RUN conda init bash \
    && . ~/.bashrc \
    && conda env create -f environment.yml \
    && conda activate myenv \
    && PUBLIC_VERSION=$(jq -r '.PUBLIC_VERSION' license.json) \
    && OCR_VERSION=$(jq -r '.OCR_VERSION' license.json) \
    && SPARK_OCR_SECRET=$(jq -r '.SPARK_OCR_SECRET' license.json) \
    && SECRET=$(jq -r '.SECRET' license.json) \
    && pip install spark-nlp==$PUBLIC_VERSION findspark wget \
    && pip install spark-nlp-jsl==$PUBLIC_VERSION --extra-index-url https://pypi.johnsnowlabs.com/$SECRET \
    && pip install spark-ocr==$OCR_VERSION --extra-index-url=https://pypi.johnsnowlabs.com/$SPARK_OCR_SECRET --upgrade --no-deps \
    && python test.py

EXPOSE 8515

## CMD ["conda", "init", "bash", ";" , ".", "~/.bashrc", ";" "conda", "activate", "myenv", ";" ,"python3", "test.py"]
ENTRYPOINT ["conda", "run", "-n", "myenv", "python", "main.py"]
