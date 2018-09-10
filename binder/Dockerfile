FROM openjdk:8-alpine

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

RUN apk add --no-cache --virtual=.dependencies tar wget bash rsync libc-dev libc6-compat zeromq zeromq-dev libzmq gcc python3 python3-dev

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir notebook==5.*
RUN python3 -m pip install --no-cache-dir numpy
RUN python3 -m pip install --no-cache-dir pyspark
RUN python3 -m pip install --no-cache-dir spark-nlp==1.6.2

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
