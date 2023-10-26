FROM ubuntu:20.04

RUN apt-get update -y && apt-get -y upgrade && \
    apt-get install -y \
        wget \
        jq \
        lsb-release \
        openjdk-8-jdk-headless \
        build-essential \
        python3 \
        python3-pip && \
    pip3 install --quiet --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man /usr/share/doc /usr/share/doc-base

ENV PYSPARK_DRIVER_PYTHON=python3
ENV PYSPARK_PYTHON=python3


COPY ./requirements.txt /requirements.txt
COPY ./entrypoint.sh /entrypoint.sh
COPY . .


RUN pip install -r requirements.txt

RUN chmod +x entrypoint.sh

WORKDIR /notebooks
ENTRYPOINT ["/entrypoint.sh"]
