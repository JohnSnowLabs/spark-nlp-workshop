#!/bin/bash
set -x -e

echo -e 'export PYSPARK_PYTHON=/usr/bin/python3 
export HADOOP_CONF_DIR=/etc/hadoop/conf 
export SPARK_JARS_DIR=/usr/lib/spark/jars 
export SPARK_HOME=/usr/lib/spark' >> $HOME/.bashrc && source $HOME/.bashrc

sudo python3 -m pip install awscli boto spark-nlp==3.1.0
sudo python3 -m pip install --upgrade spark-nlp-jsl==3.1.1 --extra-index-url https://pypi.johnsnowlabs.com/$1

sudo wget https://pypi.johnsnowlabs.com/$1/spark-nlp-jsl-3.1.1.jar -P /usr/lib/spark/jars
sudo wget https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/jars/spark-nlp-assembly-3.1.0.jar -P /usr/lib/spark/jars


set +x
exit 0

