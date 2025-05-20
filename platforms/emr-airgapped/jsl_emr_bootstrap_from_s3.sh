#!/bin/bash
set -x -e

# Set environment variables and persist them in .bashrc
echo -e 'export PYSPARK_PYTHON=/usr/bin/python3
export HADOOP_CONF_DIR=/etc/hadoop/conf
export SPARK_JARS_DIR=/usr/lib/spark/jars
export SPARK_HOME=/usr/lib/spark' >> $HOME/.bashrc && source $HOME/.bashrc

# Need to pre-download all necessary resources(jars and python dependencies) into an S3 bucket

PUBLIC_VERSION="X.Y.Z"      # Replace with the desired public Spark NLP version (e.g., 6.0.0)
JSL_VERSION="A.B.C"         # Replace with your licensed Spark NLP for Healthcare version (e.g., 6.0.0)

# JARs
# Download and install Spark NLP assembly jar
aws s3 cp s3://aws-bundle-s3/jars/spark-nlp-assembly-${PUBLIC_VERSION}.jar /tmp/
sudo mv /tmp/spark-nlp-assembly-${PUBLIC_VERSION}.jar /usr/lib/spark/jars/

# Download and install Spark NLP for Healthcare jar
aws s3 cp s3://aws-bundle-s3/jars/spark-nlp-jsl-${JSL_VERSION}.jar /tmp/
sudo mv /tmp/spark-nlp-jsl-${JSL_VERSION}.jar /usr/lib/spark/jars/

# Python wheels
# Download and install Python dependencies
aws s3 cp s3://aws-bundle-s3/python_libs/ /tmp/python_libs/ --recursive
sudo pip3 install --force-reinstall /tmp/python_libs/*.whl

set +x
exit 0
