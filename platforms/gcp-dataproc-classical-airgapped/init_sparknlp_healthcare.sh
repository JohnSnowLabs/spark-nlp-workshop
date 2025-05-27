#!/bin/bash
set -eux

echo "=== Checking Python version ==="
python3 --version
which python3

echo "=== Checking pip ==="
which pip3 || true

echo "=== Listing GCS files ==="
gsutil ls gs://spark-healthcare-nlp/

echo "=== Downloading wheels ==="
gsutil cp gs://spark-healthcare-nlp/whls/spark_nlp-6.0.0-py2.py3-none-any.whl /tmp/
gsutil cp gs://spark-healthcare-nlp/whls/spark_nlp_jsl-6.0.0-py3-none-any.whl /tmp/

echo "=== Installing wheels ==="
python3 -m pip install --no-index --find-links /tmp /tmp/spark_nlp-6.0.0-py2.py3-none-any.whl /tmp/spark_nlp_jsl-6.0.0-py3-none-any.whl
