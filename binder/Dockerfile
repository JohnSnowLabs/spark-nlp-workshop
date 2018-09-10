FROM openjdk:8-alpine

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}

RUN apk add --no-cache --virtual=.dependencies tar wget bash rsync libc-dev zmq gcc python3 python3-dev

RUN python3 -m pip install --no-cache-dir notebook==5.*

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# Make sure the contents of our repo are in ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

# Specify the default command to run
CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]
