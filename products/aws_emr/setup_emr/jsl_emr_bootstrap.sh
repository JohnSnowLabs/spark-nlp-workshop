#!/bin/bash
set -x -e

echo -e 'export PYSPARK_PYTHON=/usr/bin/python3 
export JSL_EMR=1
export HADOOP_CONF_DIR=/etc/hadoop/conf 
export SPARK_JARS_DIR=/usr/lib/spark/jars 
export SPARK_HOME=/usr/lib/spark' >> $HOME/.bashrc && source $HOME/.bashrc

sudo python3 -m pip install 'urllib3<2.0'
sudo python3 -m pip install johnsnowlabs_by_kshitiz==5.0.2rc10

sudo -E python3 -c "from johnsnowlabs import nlp;nlp.install(med_license='<med_licence_key>', spark_nlp=True, nlp=True, visual=False, hardware_platform='cpu')"
sudo bash -c "mkdir -p /usr/lib/spark/jars; cp /lib/.johnsnowlabs/johnsnowlabs/java_installs/*.jar /usr/lib/spark/jars/"
# Make sure pyspark is removed as EMR installs it by default
sudo python3 -m pip uninstall -y pyspark

set +x
exit 0

