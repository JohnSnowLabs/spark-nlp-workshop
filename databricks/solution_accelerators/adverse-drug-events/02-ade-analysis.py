# Databricks notebook source
# MAGIC %md
# MAGIC # Analyse DRUG & ADE Entities
# MAGIC Now that we have extractd ADE/Drug entities from conversational text in `01-ade-extraction` notebook, we'll create a lakehouse for ADE and perform some analysis to investigae most common ADEs and associated drugs as well as looking at the corealtion between drugs and adverse events.

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql.types import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

# COMMAND ----------

# MAGIC %run ./03-config

# COMMAND ----------

ade_analysis=SolAccUtil('ade')

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create The ADE Database
# MAGIC First let's create the Adverse Drug Events database which we can later access via `sql` (or `python` or `R`) 

# COMMAND ----------

table_paths={
  'ade_events':f'{ade_analysis.delta_path}/bronze/ade_events',
  'clf_model_results':f'{ade_analysis.delta_path}/silver/clf_model_results',
  'ade_ner_results':f'{ade_analysis.delta_path}/silver/ade_ner_results',
  'ade_ner_confidence':f'{ade_analysis.delta_path}/ade_ner_confidence',
  'assertion_confidence':f'{ade_analysis.delta_path}/gold/assertion_confidence',
  'relations_confidence':f'{ade_analysis.delta_path}/gold/relations_confidence'
}

# COMMAND ----------

db = "ADE"
spark.sql(f"CREATE DATABASE IF NOT EXISTS {db}")
spark.sql(f"USE {db}")

# COMMAND ----------

for tab,path in table_paths.items():
  spark.sql(f"CREATE TABLE IF NOT EXISTS {tab} USING DELTA LOCATION '{path}'")

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Analyze trends
# MAGIC Now let's take a quick look at some of the trends in the data

# COMMAND ----------

# DBTITLE 1,Most frequently referred drugs
# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW most_common_drugs AS
# MAGIC select lower(chunk) as drug,count('*') as count from Ade_Ner_Confidence
# MAGIC where entity = 'DRUG'
# MAGIC and confidence > 0.6
# MAGIC group by 1
# MAGIC order by 2 desc
# MAGIC limit 30

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from most_common_drugs

# COMMAND ----------

# DBTITLE 1,Most common ADEs
# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW most_common_ade AS
# MAGIC   select lower(chunk) as ade,count('*') as count from Ade_Ner_Confidence
# MAGIC   where entity = 'ADE'
# MAGIC   and confidence > 0.6
# MAGIC   group by 1
# MAGIC   order by 2 desc
# MAGIC   limit 30

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from most_common_ade

# COMMAND ----------

# DBTITLE 1,Breakdown of assertion status 
# MAGIC %sql
# MAGIC select assertion, count('*') as assertion_count from Assertion_Confidence
# MAGIC group by assertion
# MAGIC order by assertion_count

# COMMAND ----------

# MAGIC %md
# MAGIC We will find the most frequent `ADE` and `DRUG` entities, then plot them on a chart to show the count of distinct conversations that contains these entities.

# COMMAND ----------

# DBTITLE 1,most frequently asserted ADEs
# MAGIC %sql
# MAGIC with asserted_ade as (
# MAGIC   select id,lower(chunk) as ADE,entity as chunk from Assertion_Confidence
# MAGIC   where assertion !='Absent'
# MAGIC   )
# MAGIC 
# MAGIC select ADE, count('ADE') as count
# MAGIC from (
# MAGIC       select distinct id, aa.ADE from asserted_ade aa
# MAGIC       join most_common_ade mc on mc.ADE = aa.ADE
# MAGIC       )
# MAGIC group by ADE
# MAGIC order by count desc
# MAGIC limit 20

# COMMAND ----------

# DBTITLE 1,Most frequent drugs
# MAGIC %sql
# MAGIC with drug_ents as (
# MAGIC     select id, lower(chunk) as DRUG
# MAGIC     from Ade_Ner_Confidence
# MAGIC     where entity = 'DRUG'
# MAGIC   )
# MAGIC -- most_common_drugs as (
# MAGIC --     select DRUG,count('DRUG') as count
# MAGIC --     from drug_ents
# MAGIC --     group by 1
# MAGIC --     order by 2 desc
# MAGIC --     limit 20
# MAGIC -- )
# MAGIC 
# MAGIC select DRUG, count('DRUG') as count
# MAGIC from (
# MAGIC       select distinct id, de.DRUG from drug_ents de
# MAGIC       join most_common_drugs mcd on mcd.DRUG = de.DRUG
# MAGIC       )
# MAGIC group by DRUG
# MAGIC order by count desc
# MAGIC limit 20

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. DRUG-ADE association
# MAGIC Now let's take a look at the data and see which ADEs are associated with which drugs. First let't take a look at the counts of `DRUG/ADE` pairs based on co-occurance within the same document.

# COMMAND ----------

# MAGIC %sql 
# MAGIC select distinct id, entity, lower(chunk) as chunk from Ade_Ner_Confidence
# MAGIC   where confidence > 0.6

# COMMAND ----------

# MAGIC %md
# MAGIC For ease of use and better readability, we use `sql` to create the dataset of pairs of drugs and ades:

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE VIEW ADE_DRUG_PAIRS AS 
# MAGIC   with drugs as (
# MAGIC     select id, lower(chunk) as drug
# MAGIC     from Ade_Ner_Confidence
# MAGIC     where entity = 'DRUG'
# MAGIC   ),
# MAGIC   ade as (
# MAGIC     select id, chunk as ade
# MAGIC     from Ade_Ner_Confidence
# MAGIC     where entity = 'ADE'
# MAGIC   )
# MAGIC   select * from (
# MAGIC     select a.id, a.ade, d.drug
# MAGIC       from ade a
# MAGIC       join drugs d on a.id=d.id
# MAGIC       join most_common_ade mca on a.ade = mca.ade
# MAGIC       join most_common_drugs mcd on d.drug = mcd.drug
# MAGIC )

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from ADE_DRUG_PAIRS

# COMMAND ----------

# MAGIC %md
# MAGIC Now we use the `pivot` function to count the drug/ade pairs

# COMMAND ----------

ade_drug_df = (
  spark.sql("select distinct id,ade,drug from ADE_DRUG_PAIRS")
  .groupBy('ade','drug')
  .agg(F.count('*').alias('count'))
  .groupBy('drug')
  .pivot('ade')
  .sum('count')
  .fillna(0)
)
display(ade_drug_df)

# COMMAND ----------

# MAGIC %md
# MAGIC Now let us take a closer look at the ADE/DRUG pairs to see which DRUG/ADE pairs are most commonly reported

# COMMAND ----------

ade_drug_pdf=ade_drug_df.toPandas()
ade_drug_pdf.index=ade_drug_pdf['drug']
ade_drug_pdf=ade_drug_pdf.drop('drug',axis=1)

# COMMAND ----------

ade_drug_pdf.shape

# COMMAND ----------

selected_rows=ade_drug_pdf.index[ade_drug_pdf.sum(axis=1)>1]
selected_columns=ade_drug_pdf.columns[ade_drug_pdf.sum(axis=0)>1]
data_pdf=ade_drug_pdf.loc[selected_rows,selected_columns]

# COMMAND ----------

# MAGIC %md
# MAGIC Now let's visualize the heatmap of the co-occurence of drugs and ADEs. We can directly look at the counts of drugs by ADE

# COMMAND ----------

import plotly.express as px
def plot_heatmap(data,color='occurence'):
  fig = px.imshow(data,labels=dict(x="ade", y="drug", color=color),y=list(data.index),x=list(data.columns))
  fig.update_layout(
    autosize=False,
    width=1100,
    height=1100,
  )
  fig.update_xaxes(side="top")
  return(fig)

# COMMAND ----------

# DBTITLE 1,DRUG/ADE counts
fg=plot_heatmap(data_pdf)
fg.show()

# COMMAND ----------

# MAGIC %md
# MAGIC Based on this, we notice that the most common ADE/drug pair is  *heparin*/*[throbocytopenia](https://www.mayoclinic.org/diseases-conditions/thrombocytopenia/symptoms-causes/syc-20378293#:~:text=Thrombocytopenia%20is%20a%20condition%20in,plugs%20in%20blood%20vessel%20injuries.)*, which is consitent with the fact that [heparin](https://www.mayoclinic.org/drugs-supplements/heparin-intravenous-route-subcutaneous-route/description/drg-20068726) is an anticoagulant and most [reported adverse events](https://www.mayoclinic.org/drugs-supplements/heparin-intravenous-route-subcutaneous-route/side-effects/drg-20068726) are related to abnormal bleeding. 
# MAGIC In this analysis however, we do not take the expected frequency of a given ADE into account. In order to reflect any correlation between the ADE in question and a given condition, we need to normalize the counts. To do so, we use [`MinMaxScaler`](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html) to scale the values. 

# COMMAND ----------

from sklearn.preprocessing import MinMaxScaler
normalized_data=MinMaxScaler().fit(data_pdf).transform(data_pdf)

# COMMAND ----------

# DBTITLE 1,DRUG/ADE association (normalized counts)
norm_data_pdf=pd.DataFrame(normalized_data,index=data_pdf.index,columns=data_pdf.columns)
plot_heatmap(norm_data_pdf,'normalized occurence')

# COMMAND ----------

# MAGIC %md
# MAGIC In the above plot we are able to compare ADEs accross different drugs.

# COMMAND ----------

# MAGIC %sql
# MAGIC select relation, count('*') from Relations_Confidence
# MAGIC group by relation

# COMMAND ----------

# MAGIC %md
# MAGIC Now let us only consider drug-ade pairs that are linked, i.e. `realtion=1`

# COMMAND ----------

# MAGIC %sql
# MAGIC create or REPLACE TEMPORARY VIEW distinct_drug_ade_pairs as
# MAGIC   with ade_drug_pairs as (
# MAGIC   select id,chunk1 as ade,chunk2 as drug 
# MAGIC   from Relations_Confidence rc
# MAGIC   where relation=1 and entity1='ADE' and entity2='DRUG' and confidence>0.6
# MAGIC )
# MAGIC select distinct dap.id,dap.ade,dap.drug
# MAGIC   from ade_drug_pairs dap
# MAGIC   join most_common_ade mca on mca.ade=dap.ade
# MAGIC   join most_common_drugs mcd on mcd.drug = dap.drug

# COMMAND ----------

ade_drug_pairs_df = (
  spark.sql("select * from distinct_drug_ade_pairs")
  .groupBy('ade','drug')
  .agg(F.count('*').alias('count'))
  .groupBy('drug')
  .pivot('ade')
  .sum('count')
  .fillna(0)
)
display(ade_drug_pairs_df)

# COMMAND ----------

ade_drug_pairs_pdf=ade_drug_pairs_df.toPandas()
ade_drug_pairs_pdf.index=ade_drug_pairs_pdf['drug']
ade_drug_pairs_pdf.drop(['drug'],axis=1,inplace=True)

# COMMAND ----------

selected_rows=ade_drug_pairs_pdf.index[ade_drug_pairs_pdf.sum(axis=1)>1]
selected_columns=ade_drug_pairs_pdf.columns[ade_drug_pairs_pdf.sum(axis=0)>1]
data_pdf=ade_drug_pairs_pdf.loc[selected_rows,selected_columns]
normalized_data=MinMaxScaler().fit(data_pdf).transform(data_pdf)
norm_data_pdf=pd.DataFrame(normalized_data,index=data_pdf.index,columns=data_pdf.columns)

# COMMAND ----------

fg=plot_heatmap(norm_data_pdf)
fg.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Interactive dashboard
# MAGIC Using databricks SQL capabilities we can also create interactive dashboards for monitoring ADEs based on conversational text. For example, in this dashboard users can select a drug of interest from a dropdown menue to see all reported ADEs and their count
# MAGIC <img src="https://drive.google.com/uc?id=1TL8z5cjKLgXjqCcbgIA4Lfg8M6lXmyzG">

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