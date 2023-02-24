FROM bitnami/spark:3.1.1
USER root

RUN apt-get update
RUN apt install ffmpeg libsm6 libxext6 vim -y

# LABEL about the custom image
LABEL maintainer="support@johnsnowlabs.com"
LABEL version="4.2.3"
LABEL description="This is custom Docker Image for testing ZeroShot in johnsnowlabs 4.2.3 library."

# Installing Python 3.7
RUN apt install -y python3 python3-pip python3-venv

# Creating JSL folder, copying files
RUN mkdir /home/jsl

COPY requirements.txt /home/jsl/
COPY license.json /home/jsl/

# Creating virtual environment and installing johnsnowlabs library (legal, finance, healthcare)
RUN cd /home/jsl && \
    python3.7 -m venv jslenv && \
    . /home/jsl/jslenv/bin/activate && \
    pip install --upgrade pip && \
    pip install cmake==3.24.1.1 && \
    pip install johnsnowlabs==4.2.3 && \
    pip install -r requirements.txt && \
    python -c "from johnsnowlabs import *;nlp.install(json_license_path='/home/jsl/license.json')"

COPY . /home/jsl/

# Setting workdir
WORKDIR /home/jsl

EXPOSE 8888

ENTRYPOINT /home/jsl/jslenv/bin/python /home/jsl/main.py finance
