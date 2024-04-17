#!/bin/bash
set -x -e

echo -e 'export PYSPARK_PYTHON=/usr/bin/python3 
export JSL_EMR=1
export HADOOP_CONF_DIR=/etc/hadoop/conf 
export SPARK_JARS_DIR=/usr/lib/spark/jars 
export SPARK_HOME=/usr/lib/spark 
export SPARK_NLP_LICENSE=<SPARK_NLP_LICENSE>
export SECRET=<SECRET>
export JSL_VERSION=<JSL_VERSION>
export SPARK_OCR_LICENSE=<SPARK_OCR_LICENSE>
export SPARK_OCR_SECRET=<SPARK_OCR_SECRET>
export OCR_VERSION=<OCR_VERSION>
export PUBLIC_VERSION=<PUBLIC_VERSION>
export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY> ' >> $HOME/.bashrc && source $HOME/.bashrc


sudo python3 -m pip install 'urllib3<2.0'

# Installing SparkOCR
sudo python3 -m pip  install --upgrade -q spark-ocr==$OCR_VERSION --extra-index-url https://pypi.johnsnowlabs.com/$SPARK_OCR_SECRET

# Installing Spark NLP Healthcare
sudo python3 -m pip install --upgrade -q spark-nlp-jsl==$JSL_VERSION  --extra-index-url https://pypi.johnsnowlabs.com/$SECRET

sudo wget  https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/jars/spark-nlp-assembly-$PUBLIC_VERSION.jar -P /usr/lib/spark/jars/
sudo wget -q https://s3.eu-west-1.amazonaws.com/pypi.johnsnowlabs.com/$SPARK_OCR_SECRET/jars/spark-ocr-assembly-$OCR_VERSION.jar -P /usr/lib/spark/jars/
sudo wget -q https://s3.eu-west-1.amazonaws.com/pypi.johnsnowlabs.com/$SECRET/spark-nlp-jsl-$JSL_VERSION.jar -P /usr/lib/spark/jars/


sudo python3 -m pip install pyspark==3.4.1 --upgrade
sudo python3 -m pip install spark-nlp==$PUBLIC_VERSION
sudo python3 -m pip install pandas --upgrade

sudo usermod -a -G hdfsadmingroup livy
sudo usermod -a -G hdfsadmingroup hadoop

set +x
exit 0


