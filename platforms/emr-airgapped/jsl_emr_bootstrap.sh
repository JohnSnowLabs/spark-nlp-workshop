#!/bin/bash
set -x -e

echo -e 'export PYSPARK_PYTHON=/usr/bin/python3 
export HADOOP_CONF_DIR=/etc/hadoop/conf
export SPARK_JARS_DIR=/usr/lib/spark/jars
export SPARK_HOME=/usr/lib/spark' >> $HOME/.bashrc && source $HOME/.bashrc

# Define version variables
# You can find these variables in your license dictionary
PUBLIC_VERSION="X.Y.Z"      # Replace with the desired public Spark NLP version (e.g., 6.0.3)
JSL_VERSION="A.B.C"         # Replace with your licensed Spark NLP for Healthcare version (e.g., 6.0.3)
SECRET="your_secret_key"    # Replace with your license key or secret token

# Download Spark NLP public jar
sudo wget https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/jars/spark-nlp-assembly-${PUBLIC_VERSION}.jar -P /usr/lib/spark/jars/

# Download Spark NLP for Healthcare jar
sudo wget -q https://s3.eu-west-1.amazonaws.com/pypi.johnsnowlabs.com/${SECRET}/spark-nlp-jsl-${JSL_VERSION}.jar -P /usr/lib/spark/jars/

# Install Spark NLP Python package
sudo pip3 install -q --upgrade spark-nlp==${PUBLIC_VERSION}

# Install Spark NLP for Healthcare Python package
sudo pip3 install -q spark-nlp-jsl==${JSL_VERSION} --extra-index-url https://pypi.johnsnowlabs.com/${SECRET}

# Install additional Python dependencies
sudo pip3 install numpy pandas

set +x
exit 0
