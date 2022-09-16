# Databricks notebook source
# MAGIC %md
# MAGIC #Abstracting Real World Data from Oncology Notes
# MAGIC 
# MAGIC In this collection, we use [John Snow Labs’ Spark NLP for Healthcare](https://www.johnsnowlabs.com/spark-nlp-health/), the most widely-used NLP library in the healthcare and life science industries, to extarct, classify and structure clinical and biomedical text data with state-of-the-art accuracy at scale. 
# MAGIC For this solution we used the [MT ONCOLOGY NOTES]((https://www.mtsamplereports.com/) dataset. It offers resources primarily in the form of transcribed sample medical reports across medical specialties and common medical transcription words/phrases encountered in specific sections that form part of a medical report  – sections such as physical examination or PE, review of systems or ROS, laboratory data and mental status exam, among others. 
# MAGIC 
# MAGIC We chose 50 de-identified oncology reports from the MT Oncology notes dataset as the source of the unstructured text and landed the raw text data into the Delta Lake bronze layer. For demonstration purposes, we limited the number of samples to 50, but the framework presented in this solution accelerator can be scaled to accommodate millions of clinical notes and text files. 
# MAGIC 
# MAGIC The first step in our accelerator is to extract variables using various models for [Named-Entity Recognition (NER)](https://www.johnsnowlabs.com/named-entity-recognition-ner-with-bert-in-spark-nlp/). To do that, we first set up our NLP pipeline, which contains [annotators](https://nlp.johnsnowlabs.com/docs/en/annotators) such as [documentAssembler](https://nlp.johnsnowlabs.com/docs/en/annotators#documentassembler) and [sentenceDetector](https://nlp.johnsnowlabs.com/docs/en/annotators#sentencedetector) and [tokenizer](https://nlp.johnsnowlabs.com/docs/en/annotators#tokenizer)  that are trained specifically for healthcare-related NER. 
# MAGIC <br>
# MAGIC <img src="https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/databricks/solution_accelerators/images/dbr_flow.png" width=65%>
# MAGIC 
# MAGIC We then create dataframes of extracted entitities and land the tables in Delta where can be accessed for interactive analysis or dashboarding using [databricks SQL](https://databricks.com/product/databricks-sql). 
# MAGIC 
# MAGIC <br>
# MAGIC <img src="https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/databricks/solution_accelerators/images/insights_from_oncology_repots" width=65%>
# MAGIC 
# MAGIC ## Data
# MAGIC 
# MAGIC [MT ONCOLOGY NOTES](https://www.mtsamplereports.com/) comprises of millions of ehr records of patients. It contains semi-structured data like demographics, insurance details, and a lot more, but most importantly, it also contains free-text data like real encounters and notes.
# MAGIC 
# MAGIC ## Solution Overview
# MAGIC Here we show how to use Spark NLP's existing models to process raw text and extract highly specialized cancer information that can be used for various downstream use cases, including:
# MAGIC - Staff demand analysis according to specialties.
# MAGIC - Preparing reimbursement-ready data with billable codes.
# MAGIC - Analysis of risk factors of patients and symptoms.
# MAGIC - Analysis of cancer disease and symptoms.
# MAGIC - Drug usage analysis for inventory management.
# MAGIC - Preparing timeline of procedures.
# MAGIC - Relations between internal body part and procedures.
# MAGIC - Analysis of procedures used on oncological events.
# MAGIC - Checking assertion status of oncological findings.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Notebooks
# MAGIC There are three notebooks in this package:
# MAGIC 
# MAGIC 1. `config`: Notebook for configuring the environment
# MAGIC 2. `entity-extraction`: Extract drugs, oncological entitities, assertion status and relationships and writes the data into Delta lake.
# MAGIC 3. `oncology-analytics`: Interactive analysis of the data. 

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup
# MAGIC If you are new to Databricks, create an account at: https://databricks.com/try-databricks
# MAGIC ### Turnkey John Snow Labs installation
# MAGIC 
# MAGIC Complete John Snow Labs onboarding form at: www.JohnSnowLabs.com/Databricks and speficy `Name`, `email`, `Databricks instance URL` and [access token](https://docs.databricks.com/dev-tools/api/latest/authentication.html#authentication-using-databricks-personal-access-tokens). Choose a cluster to install in, or install in a new one. Verify your email to start the installation
# MAGIC 
# MAGIC ### What does the turnkey John Snow Labs installation do?
# MAGIC - Create a new Databricks cluster if needed
# MAGIC - Install Spark NLP for Healthcare & Spark OCR
# MAGIC - Generate a new 30-day free trial license key
# MAGIC - Install the license key in the cluster
# MAGIC - Load 20+ Python notebooks with examples
# MAGIC - Email you once it’s all done
# MAGIC 
# MAGIC In addition you need the following libraires intsalled:
# MAGIC 
# MAGIC <img src="https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/databricks/solution_accelerators/images/410_cluster.jpg" width=80%>

# COMMAND ----------

slides_html="""
<iframe src="https://docs.google.com/presentation/d/1wNQaCy5drc7C5R-bZWp-PA7GLef09SAOr7jCs18uibg/embed?start=true&loop=true&delayms=4000" frameborder="0" width="900" height="560" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>
"""
displayHTML(slides_html)

# COMMAND ----------

# MAGIC %md
# MAGIC ## License
# MAGIC Copyright / License info of the notebook. Copyright [2021] the Notebook Authors.  The source in this notebook is provided subject to the [Apache 2.0 License](https://spdx.org/licenses/Apache-2.0.html).  All included or referenced third party libraries are subject to the licenses set forth below.
# MAGIC 
# MAGIC |Library Name|Library License|Library License URL|Library Source URL|
# MAGIC | :-: | :-:| :-: | :-:|
# MAGIC |Pandas |BSD 3-Clause License| https://github.com/pandas-dev/pandas/blob/master/LICENSE | https://github.com/pandas-dev/pandas|
# MAGIC |Numpy |BSD 3-Clause License| https://github.com/numpy/numpy/blob/main/LICENSE.txt | https://github.com/numpy/numpy|
# MAGIC |Apache Spark |Apache License 2.0| https://github.com/apache/spark/blob/master/LICENSE | https://github.com/apache/spark/tree/master/python/pyspark|
# MAGIC |MatPlotLib | | https://github.com/matplotlib/matplotlib/blob/master/LICENSE/LICENSE | https://github.com/matplotlib/matplotlib|
# MAGIC |Seaborn |BSD 3-Clause License | https://github.com/seaborn/seaborn/blob/master/LICENSE | https://github.com/seaborn/seaborn/|
# MAGIC |Plotly|MIT License|https://github.com/plotly/plotly.py/blob/master/LICENSE.txt|https://github.com/plotly/plotly.py|
# MAGIC |Spark NLP Display|Apache License 2.0|https://github.com/JohnSnowLabs/spark-nlp-display/blob/main/LICENSE|https://github.com/JohnSnowLabs/spark-nlp-display|
# MAGIC |Spark NLP |Apache License 2.0| https://github.com/JohnSnowLabs/spark-nlp/blob/master/LICENSE | https://github.com/JohnSnowLabs/spark-nlp|
# MAGIC |Spark NLP for Healthcare|[Proprietary license - John Snow Labs Inc.](https://www.johnsnowlabs.com/spark-nlp-health/) |NA|NA|
# MAGIC 
# MAGIC 
# MAGIC |Author|
# MAGIC |-|
# MAGIC |Databricks Inc.|
# MAGIC |John Snow Labs Inc.|

# COMMAND ----------

# MAGIC %md
# MAGIC ## Disclaimers
# MAGIC Databricks Inc. (“Databricks”) does not dispense medical, diagnosis, or treatment advice. This Solution Accelerator (“tool”) is for informational purposes only and may not be used as a substitute for professional medical advice, treatment, or diagnosis. This tool may not be used within Databricks to process Protected Health Information (“PHI”) as defined in the Health Insurance Portability and Accountability Act of 1996, unless you have executed with Databricks a contract that allows for processing PHI, an accompanying Business Associate Agreement (BAA), and are running this notebook within a HIPAA Account.  Please note that if you run this notebook within Azure Databricks, your contract with Microsoft applies.
