#Abstracting Real World Data from Oncology Notes

In this collection, we use [John Snow Labs’ Spark NLP for Healthcare](https://www.johnsnowlabs.com/spark-nlp-health/), the most widely-used NLP library in the healthcare and life science industries, to extarct, classify and structure clinical and biomedical text data with state-of-the-art accuracy at scale. 
For this solution we used the [MT ONCOLOGY NOTES]((https://www.mtsamplereports.com/) dataset. It offers resources primarily in the form of transcribed sample medical reports across medical specialties and common medical transcription words/phrases encountered in specific sections that form part of a medical report  – sections such as physical examination or PE, review of systems or ROS, laboratory data and mental status exam, among others. 

We chose 50 de-identified oncology reports from the MT Oncology notes dataset as the source of the unstructured text and landed the raw text data into the Delta Lake bronze layer. For demonstration purposes, we limited the number of samples to 50, but the framework presented in this solution accelerator can be scaled to accommodate millions of clinical notes and text files. 

The first step in our accelerator is to extract variables using various models for [Named-Entity Recognition (NER)](https://www.johnsnowlabs.com/named-entity-recognition-ner-with-bert-in-spark-nlp/). To do that, we first set up our NLP pipeline, which contains [annotators](https://nlp.johnsnowlabs.com/docs/en/annotators) such as [documentAssembler](https://nlp.johnsnowlabs.com/docs/en/annotators#documentassembler) and [sentenceDetector](https://nlp.johnsnowlabs.com/docs/en/annotators#sentencedetector) and [tokenizer](https://nlp.johnsnowlabs.com/docs/en/annotators#tokenizer)  that are trained specifically for healthcare-related NER. 
<br>
<img src="https://hls-eng-data-public.s3.amazonaws.com/img/phi-deid-ra.png" width=65%>

We then create dataframes of extracted entitities and land the tables in Delta where can be accessed for interactive analysis or dashboarding using [databricks SQL](https://databricks.com/product/databricks-sql). 

<br>
<img src="https://hls-eng-data-public.s3.amazonaws.com/img/jsl-dash.png" width=65%>

## Data

[MT ONCOLOGY NOTES](https://www.mtsamplereports.com/) comprises of millions of ehr records of patients. It contains semi-structured data like demographics, insurance details, and a lot more, but most importantly, it also contains free-text data like real encounters and notes.

## Solution Overview
Here we show how to use Spark NLP's existing models to process raw text and extract highly specialized cancer information that can be used for various downstream use cases, including:
- Staff demand analysis according to specialties.
- Preparing reimbursement-ready data with billable codes.
- Analysis of risk factors of patients and symptoms.
- Analysis of cancer disease and symptoms.
- Drug usage analysis for inventory management.
- Preparing timeline of procedures.
- Relations between internal body part and procedures.
- Analysis of procedures used on oncological events.
- Checking assertion status of oncological findings.

### Notebooks
There are three notebooks in this package:

1. `config`: Notebook for configuring the environment
2. `entity-extraction`: Extract drugs, oncological entitities, assertion status and relationships and writes the data into Delta lake.
3. `oncology-analytics`: Interactive analysis of the data. 

## License
Copyright / License info of the notebook. Copyright [2021] the Notebook Authors.  The source in this notebook is provided subject to the [Apache 2.0 License](https://spdx.org/licenses/Apache-2.0.html).  All included or referenced third party libraries are subject to the licenses set forth below.

|Library Name|Library License|Library License URL|Library Source URL|
| :-: | :-:| :-: | :-:|
|Pandas |BSD 3-Clause License| https://github.com/pandas-dev/pandas/blob/master/LICENSE | https://github.com/pandas-dev/pandas|
|Numpy |BSD 3-Clause License| https://github.com/numpy/numpy/blob/main/LICENSE.txt | https://github.com/numpy/numpy|
|Apache Spark |Apache License 2.0| https://github.com/apache/spark/blob/master/LICENSE | https://github.com/apache/spark/tree/master/python/pyspark|
|MatPlotLib | | https://github.com/matplotlib/matplotlib/blob/master/LICENSE/LICENSE | https://github.com/matplotlib/matplotlib|
|Seaborn |BSD 3-Clause License | https://github.com/seaborn/seaborn/blob/master/LICENSE | https://github.com/seaborn/seaborn/|
|Plotly|MIT License|https://github.com/plotly/plotly.py/blob/master/LICENSE.txt|https://github.com/plotly/plotly.py|
|Spark NLP Display|Apache License 2.0|https://github.com/JohnSnowLabs/spark-nlp-display/blob/main/LICENSE|https://github.com/JohnSnowLabs/spark-nlp-display|
|Spark NLP |Apache License 2.0| https://github.com/JohnSnowLabs/spark-nlp/blob/master/LICENSE | https://github.com/JohnSnowLabs/spark-nlp|
|Spark NLP for Healthcare|[Proprietary license - John Snow Labs Inc.](https://www.johnsnowlabs.com/spark-nlp-health/) |NA|NA|


|Author|
|-|
|Databricks Inc.|
|John Snow Labs Inc.|

## Disclaimers
Databricks Inc. (“Databricks”) does not dispense medical, diagnosis, or treatment advice. This Solution Accelerator (“tool”) is for informational purposes only and may not be used as a substitute for professional medical advice, treatment, or diagnosis. This tool may not be used within Databricks to process Protected Health Information (“PHI”) as defined in the Health Insurance Portability and Accountability Act of 1996, unless you have executed with Databricks a contract that allows for processing PHI, an accompanying Business Associate Agreement (BAA), and are running this notebook within a HIPAA Account.  Please note that if you run this notebook within Azure Databricks, your contract with Microsoft applies.
