#!/bin/bash


PYSPARK="3.2.2"
SPARKNLP="4.3.0"
SPARKHOME="/home/ec2-user/SageMaker/spark-3.2.2-bin-hadoop2.7"
OCR="4.3.1"

echo "setup SageMaker for PySpark $PYSPARK and Spark NLP $SPARKNLP and Spark OCR $OCR_VERSION and Spark NLP for Healthcare $JSL_VERSION"
JAVA_8=$(alternatives --display java | grep 'jre-1.8.0-openjdk.x86_64/bin/java'| cut -d' ' -f1)
sudo alternatives --set java $JAVA_8

if [[ "$PYSPARK" == "3.1"* ]]; then
  wget -q "https://archive.apache.org/dist/spark/spark-3.1.1/spark-3.1.1-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-3.1.1-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/home/ec2-user/SageMaker/spark-3.1.1-bin-hadoop2.7"
elif [[ "$PYSPARK" == "3.0"* ]]; then
  wget -q "https://archive.apache.org/dist/spark/spark-3.0.2/spark-3.0.2-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-3.0.2-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME=""/home/ec2-user/SageMaker/spark-3.0.2-bin-hadoop2.7""
elif [[ "$PYSPARK" == "2"* ]]; then
  wget -q "https://downloads.apache.org/spark/spark-2.4.7/spark-2.4.7-bin-hadoop2.7.tgz" > /dev/null
  tar -xvf spark-2.4.7-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/home/ec2-user/SageMaker/spark-2.4.7-bin-hadoop2.7"
else
  wget -q "https://downloads.apache.org/spark/spark-3.2.2/spark-3.2.2-bin-hadoop2.7.tgz" -O spark-3.2.2-bin-hadoop2.7.tgz > /dev/null
  tar -xvf spark-3.2.2-bin-hadoop2.7.tgz > /dev/null
  SPARKHOME="/home/ec2-user/SageMaker/spark-3.2.2-bin-hadoop2.7"
fi

export SPARK_HOME=$SPARKHOME

# Install pyspark spark-nlp
! pip install --upgrade -q pyspark==$PYSPARK spark-nlp==$PUBLIC_VERSION findspark
! pip install --upgrade -q spark-nlp-jsl==$JSL_VERSION  --extra-index-url https://pypi.johnsnowlabs.com/$SECRET
! pip install --upgrade -q spark-ocr==$OCR_VERSION --extra-index-url=https://pypi.johnsnowlabs.com/$SPARK_OCR_SECRET
