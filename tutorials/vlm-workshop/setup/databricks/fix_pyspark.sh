#!/bin/bash
# Databricks init script: remove incompatible pyspark 4.1.1 from DBR 14.3
# Upload to /Workspace/Users/<you>/fix_pyspark.sh and set as cluster init script.
pip uninstall -y pyspark 2>/dev/null || true
