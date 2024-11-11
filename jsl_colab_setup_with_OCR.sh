#!/bin/bash

#default values for pyspark, spark-nlp, and SPARK_HOME

PYSPARK="3.0.2"
SPARKNLP=$PUBLIC_VERSION
SPARKNLP_JSL=$JSL_VERSION
SPARK_NLP_LICENSE=$SPARK_NLP_LICENSE
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
JSL_SECRET=$SECRET

while getopts p: option
do
 case "${option}"
 in
 p) PYSPARK=${OPTARG};;
 esac
done

SPARKHOME="/content/spark-3.1.1-bin-hadoop2.7"

echo "setup Colab for PySpark $PYSPARK and Spark NLP $SPARKNLP"
apt-get update
apt-get purge -y openjdk-11* -qq > /dev/null && sudo apt-get autoremove -y -qq > /dev/null
apt-get install -y openjdk-8-jdk-headless -qq > /dev/null

if [[ "$PYSPARK" == "3.1"* ]]; then
  wget -q "https://downloads.apache.org/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-3.1.1-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/content/spark-3.1.1-bin-hadoop2.7"
elif [[ "$PYSPARK" == "3.0"* ]]; then
  wget -q "https://downloads.apache.org/spark/spark-3.0.2/spark-3.0.2-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-3.0.2-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/content/spark-3.0.2-bin-hadoop2.7"
elif [[ "$PYSPARK" == "2"* ]]; then
  wget -q "https://downloads.apache.org/spark/spark-2.4.7/spark-2.4.7-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-2.4.7-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/content/spark-2.4.7-bin-hadoop2.7"
else
  wget -q "https://downloads.apache.org/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-3.1.1-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/content/spark-3.1.1-bin-hadoop2.7"
fi

export SPARK_HOME=$SPARKHOME
export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"

# Install pyspark spark-nlp
! pip install implicits
! pip install --upgrade -q pyspark==$PYSPARK spark-nlp==$SPARKNLP findspark
! pip install --upgrade -q spark-nlp-jsl==$SPARKNLP_JSL  --extra-index-url https://pypi.johnsnowlabs.com/$JSL_SECRET
! pip install spark-ocr==$OCR_VERSION --user --extra-index-url=https://pypi.johnsnowlabs.com/$JSL_OCR_SECRET --upgrade --no-deps

