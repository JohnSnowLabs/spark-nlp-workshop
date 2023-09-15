#!/bin/bash
sudo usermod -a -G hdfsadmingroup livy
sudo usermod -a -G hdfsadmingroup hadoop
# Issue with EMR. See https://stackoverflow.com/questions/68406738/aws-emr-pandas-conflict-with-numpy-in-pyspark-after-bootstrapping
sudo python3 -m pip uninstall -y numpy
sudo python3 -m pip install "numpy>1.17.3"
sudo python3 -m pip install scipy scikit-learn "tensorflow==2.11.0" tensorflow-addons matplotlib
exit 0
