FROM openjdk:8-alpine

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

RUN apk add --no-cache --virtual=.dependencies tar wget bash rsync libc-dev libc6-compat zeromq zeromq-dev libzmq gcc python3 python3-dev

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir notebook==5.* numpy pyspark spark-nlp==1.6.2
RUN wget https://s3.amazonaws.com/auxdata.johnsnowlabs.com/spark-nlp-resources/glove.6B.100d.zip && \
    mkdir -p /home/jovyan/data/embeddings/ && \
    unzip glove.6B.100d.zip -d /home/jovyan/data/embeddings && \
    rm glove.6B.100d.zip

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# Make sure the contents of our repo are in ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

WORKDIR ${HOME}/jupyter

# Specify the default command to run
CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]
