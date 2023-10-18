#!/bin/bash
set -x -e

SECRET=$1
SECRET2=$2
IFS='-' read -r -a array <<< $SECRET
VERSION=${array[0]}
echo $VERSION

IFS='-' read -r -a array <<< $SECRET2
JSL_VERSION=${array[0]}
echo $JSL_VERSION

sudo pip3 install --upgrade pip setuptools
sudo pip3 install pillow==9.0.1 imageio==2.16.0 pip ipython pandas spark-nlp==$VERSION
sudo pip3 install spark-ocr==$VERSION --extra-index-url https://pypi.johnsnowlabs.com/$SECRET

sudo pip3 install -q spark-nlp-jsl==$JSL_VERSION  --extra-index-url https://pypi.johnsnowlabs.com/$SECRET2
sudo pip3 install termcolor

sudo wget https://pypi.johnsnowlabs.com/$SECRET/jars/spark-ocr-assembly-$VERSION.jar -P /usr/lib/spark/jars
sudo wget https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/jars/spark-nlp-assembly-$VERSION.jar -P /usr/lib/spark/jars

set +x
exit 0
