#!/bin/bash
set -x -e

echo -e 'export PYSPARK_PYTHON=/usr/bin/python3 
export HADOOP_CONF_DIR=/etc/hadoop/conf
export SPARK_JARS_DIR=/usr/lib/spark/jars
export SPARK_HOME=/usr/lib/spark' >> $HOME/.bashrc && source $HOME/.bashrc

# Installing Spark-NLP wheel
sudo pip3 install -q --upgrade -q  spark-nlp=={PUBLIC_VERSION}

# Installing Spark NLP Healthcare wheel
sudo pip3 install -q spark-nlp-jsl==$JSL_VERSION  --extra-index-url https://pypi.johnsnowlabs.com/$SECRET

# Installing more libraries if needed
sudo pip3 install numpy
sudo pip3 install pandas

# Installing Jars
sudo wget  https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/jars/spark-nlp-assembly-{PUBLIC_VERSION}.jar -P /usr/lib/spark/jars/
sudo wget -q https://s3.eu-west-1.amazonaws.com/pypi.johnsnowlabs.com/{SECRET}/spark-nlp-jsl-{JSL_VERSION}.jar -P /usr/lib/spark/jars/

set +x
exit 0


