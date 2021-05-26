#!/bin/bash


PYSPARK="3.1.1"
SPARKNLP="3.0.3"
SPARKHOME="/home/ec2-user/SageMaker/spark-3.1.1-bin-hadoop2.7"

echo "setup SageMaker for PySpark $PYSPARK and Spark NLP $SPARKNLP"
JAVA_8=$(alternatives --display java | grep 'jre-1.8.0-openjdk.x86_64/bin/java'| cut -d' ' -f1)
sudo alternatives --set java $JAVA_8

if [[ "$PYSPARK" == "3.1"* ]]; then
  wget -q "https://downloads.apache.org/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-3.1.1-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/home/ec2-user/SageMaker/spark-3.1.1-bin-hadoop2.7"
elif [[ "$PYSPARK" == "3.0"* ]]; then
  wget -q "https://downloads.apache.org/spark/spark-3.0.2/spark-3.0.2-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-3.0.2-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME=""/home/ec2-user/SageMaker/spark-3.0.2-bin-hadoop2.7""
elif [[ "$PYSPARK" == "2"* ]]; then
  wget -q "https://downloads.apache.org/spark/spark-2.4.7/spark-2.4.7-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-2.4.7-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/home/ec2-user/SageMaker/spark-2.4.7-bin-hadoop2.7"
else
  wget -q "https://downloads.apache.org/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-3.1.1-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/home/ec2-user/SageMaker/spark-3.1.1-bin-hadoop2.7"
fi

export SPARK_HOME=$SPARKHOME
export JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"

# Install pyspark spark-nlp
! pip install --upgrade -q pyspark==$PYSPARK spark-nlp==$SPARKNLP findspark
! pip install --upgrade -q spark-nlp-jsl==$SPARKNLP_JSL  --extra-index-url https://pypi.johnsnowlabs.com/$JSL_SECRET
