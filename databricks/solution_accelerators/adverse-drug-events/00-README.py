# Databricks notebook source
slides_html="""
<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vSru8d8LC-C_77PM44Wjo7Ti5zR0OkHSUlFU22BRoRhXkIwYIyMhTZ-7AIsf3hCTGcID-Tu2MarTuiT/embed?start=false&loop=false&delayms=3000" frameborder="0" width="960" height="569" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>
"""
displayHTML(slides_html)

# COMMAND ----------

# MAGIC %md
# MAGIC # Detecting Adverse Drug Events From Conversational Texts
# MAGIC 
# MAGIC Adverse Drug Events (ADEs) are potentially very dangerous to patients and are top causes of morbidity and mortality. Many ADEs are hard to discover as they happen to certain groups of people in certain conditions and they may take a long time to expose. Healthcare providers conduct clinical trials to discover ADEs before selling the products but normally are limited in numbers. Thus, post-market drug safety monitoring is required to help discover ADEs after the drugs are sold on the market. 
# MAGIC 
# MAGIC Less than 5% of ADEs are reported via official channels and the vast majority is described in free-text channels: emails & phone calls to patient support centers, social media posts, sales conversations between clinicians and pharma sales reps, online patient forums, and so on. This requires pharmaceuticals and drug safety groups to monitor and analyze unstructured medical text from a variety of jargons, formats, channels, and languages - with needs for timeliness and scale that require automation. 
# MAGIC 
# MAGIC In the solution accelerator, we show how to use Spark NLP's existing models to process conversational text and extract highly specialized ADE and DRUG information, store the data in lakehouse, and analyze the data for various downstream use cases, including:
# MAGIC 
# MAGIC - Conversational Texts ADE Classification
# MAGIC - Detecting ADE and Drug Entities From Texts
# MAGIC - Analysis of Drug and ADE Entities
# MAGIC - Finding Drugs and ADEs Have Been Talked Most
# MAGIC - Detecting Most Common Drug-ADE Pairs
# MAGIC - Checking Assertion Status of ADEs
# MAGIC - Relations Between ADEs and Drugs
# MAGIC 
# MAGIC There are three noetbooks in this package:
# MAGIC 
# MAGIC 
# MAGIC 1. `./01-ade-extraction`: Extract ADE, DRUGS, assertion status and relationships betwene drugs and ades
# MAGIC 2. `./02-ade-analysis`: Create a deltakake of ADE and drugs  based on extracted entities and analyze the results (drug/ade correlations)
# MAGIC 3. `./03-config`: Notebook for configurating the environment
# MAGIC 
# MAGIC <img src="https://drive.google.com/uc?id=1TL8z5cjKLgXjqCcbgIA4Lfg8M6lXmyzG">

# COMMAND ----------

# MAGIC %md
# MAGIC #NOTE:
# MAGIC To run the `./01-ade-extraction` extraction notebook, you need to have John Snow Lab's pre-trained models intsalled on your cluster. For more information on how to install these models installed see: [John Snow Labs NLP on Databricks
# MAGIC ](https://www.johnsnowlabs.com/databricks), in addition you need the following libraires intsalled: 
# MAGIC <img src="https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/databricks/solution_accelerators/images/410_cluster.jpg">

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
