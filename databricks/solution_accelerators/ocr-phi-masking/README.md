# PHI de-identification 
Under the Health Insurance Portability and Accountability Act (HIPAA) minimum necessary standard, HIPAA-covered entities (such as health systems and insurers) are required to make reasonable efforts to ensure that access to Protected Health Information (PHI) is limited to the minimum necessary information to accomplish the intended purpose of particular use, disclosure, or request.

In this solution accelerator we show how to use databricks lakehouse platform and John Snow Lab's SparkOCR and NLP for Health Care pre-trained models to:

1. Store clinical notes in pdf format in deltalake
2. Use [SparkOCR](https://nlp.johnsnowlabs.com/docs/en/ocr) to improve image quality and extract text from pdfs
3. Use [SparkNLP pre-trained models](https://nlp.johnsnowlabs.com/2020/08/04/deidentify_large_en.html) for phi extarction and de-identification


<img src="https://hls-eng-data-public.s3.amazonaws.com/img/phi-deid-ra.png" width=65%>

## Notebooks
<img src="https://hls-eng-data-public.s3.amazonaws.com/img/phi-deid-dataflow.png" width=30%>

 1. `pdf-ocr`: This notebook imports pdf files containing oncology reports and uses sparkOCR for image processing and text extraction. Resulting entities and text are stored in delta
 2. `phi-deidentification`: In this notebook we use pre-trained models to extract phi and mask extracted phi. Resulting obfuscated clinical notes are stored in delta for downstream analysis. 
 3. `config`: Utility notebook for setting up the environment
 
 ## License
Copyright / License info of the notebook. Copyright [2021] the Notebook Authors.  The source in this notebook is provided subject to the [Apache 2.0 License](https://spdx.org/licenses/Apache-2.0.html).  All included or referenced third party libraries are subject to the licenses set forth below.

|Library Name|Library License|Library License URL|Library Source URL| 
| :-: | :-:| :-: | :-:|
|Pandas |BSD 3-Clause License| https://github.com/pandas-dev/pandas/blob/master/LICENSE | https://github.com/pandas-dev/pandas|
|Numpy |BSD 3-Clause License| https://github.com/numpy/numpy/blob/main/LICENSE.txt | https://github.com/numpy/numpy|
|Apache Spark |Apache License 2.0| https://github.com/apache/spark/blob/master/LICENSE | https://github.com/apache/spark/tree/master/python/pyspark|
|Spark NLP |Apache-2.0 License| https://github.com/JohnSnowLabs/spark-nlp/blob/master/LICENSE | https://github.com/JohnSnowLabs/spark-nlp|
|MatPlotLib | | https://github.com/matplotlib/matplotlib/blob/master/LICENSE/LICENSE | https://github.com/matplotlib/matplotlib|
|Pillow (PIL) | HPND License| https://github.com/python-pillow/Pillow/blob/master/LICENSE | https://github.com/python-pillow/Pillow/|
|Spark NLP for Healthcare|[Proprietary license - John Snow Labs Inc.](https://www.johnsnowlabs.com/spark-nlp-health/) |NA|NA|
|Spark OCR |[Proprietary license - John Snow Labs Inc.](https://nlp.johnsnowlabs.com/docs/en/ocr) |NA|NA|

|Author|
|-|
|Databricks Inc.|
|John Snow Labs Inc.|

## Disclaimers
Databricks Inc. (“Databricks”) does not dispense medical, diagnosis, or treatment advice. This Solution Accelerator (“tool”) is for informational purposes only and may not be used as a substitute for professional medical advice, treatment, or diagnosis. This tool may not be used within Databricks to process Protected Health Information (“PHI”) as defined in the Health Insurance Portability and Accountability Act of 1996, unless you have executed with Databricks a contract that allows for processing PHI, an accompanying Business Associate Agreement (BAA), and are running this notebook within a HIPAA Account.  Please note that if you run this notebook within Azure Databricks, your contract with Microsoft applies.
