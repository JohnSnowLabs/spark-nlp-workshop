# Databricks notebook source
# MAGIC %md
# MAGIC # Abstracting Real World Data from Oncology Notes: Data Analysis
# MAGIC 
# MAGIC In the previous notebook (`./00-entity-extraction`) we used SparkNLP's pipelines to extract hightly specialized oncological entities from unstructured notes and stored the resulting tabular data in our delta lake.
# MAGIC 
# MAGIC In this notebook we analyze these data to answer questions such as:
# MAGIC What are the most common cancer subtypes? What are the most common symptoms and how are these symptoms associated with each cancer subtype? which indications have the highest risk factor? etc. 

# COMMAND ----------

import numpy as np
import pandas as pd
from pyspark.sql import functions as F

# COMMAND ----------

# MAGIC %run ./04-config

# COMMAND ----------

ade_demo_util=SolAccUtil('onc-lh',data_path='/FileStore/HLS/nlp/data/')
ade_demo_util.print_info()
delta_path=ade_demo_util.settings['delta_path']
# delta_path='/FileStore/HLS/nlp/delta/jsl/'

# COMMAND ----------

# MAGIC %md
# MAGIC let's take a look at the raw text dataset

# COMMAND ----------

df=spark.read.load(f'{delta_path}/bronze/mt-oc-notes')
display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC # 1. ICD-10 Codes and HCC Status

# COMMAND ----------

# MAGIC %md
# MAGIC Now we load the `icd10` delta tables

# COMMAND ----------

icd10_hcc_df=spark.read.load(f'{delta_path}/silver/icd10-hcc-df')
icd10_hcc_df.createOrReplaceTempView('icd10HccView')

best_icd_mapped_df=spark.read.load(f'{delta_path}/gold/best-icd-mapped')
best_icd_mapped_df.createOrReplaceTempView('bestIcdMappedView')
best_icd_mapped_pdf=best_icd_mapped_df.toPandas()

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from icd10HccView
# MAGIC limit 10

# COMMAND ----------

# DBTITLE 1,Count of entities
# MAGIC %sql
# MAGIC select entity, count('*') from icd10HccView
# MAGIC group by 1
# MAGIC order by 2

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.1. Get general information for staff management, reporting, & planning.
# MAGIC 
# MAGIC Let's take a look at the distribution of mapped codes

# COMMAND ----------

# DBTITLE 1,Distribution of Mapped ICDs
display(
  best_icd_mapped_df
  .select('onc_code_desc')
  .filter("onc_code_desc!='-'")
  .groupBy('onc_code_desc')
  .count()
  .orderBy('count')
)

# COMMAND ----------

# MAGIC %md
# MAGIC we can also visualize the results as a countplot to see the number of each parent categories

# COMMAND ----------

import plotly.graph_objects as go

_ps=best_icd_mapped_pdf['onc_code_desc'].value_counts()
data=_ps[_ps.index!='-']

fig = go.Figure(go.Bar(
            x=data.values,
            y=data.index,
            orientation='h'))
fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.2. Reimbursement-ready data with billable codes
# MAGIC In the previous notebook, using an icd10 oncology mapping dictionary, we created a dataset of coded conditions that are all billable. To assess the quality of the mapping, we can look at the distribution of 
# MAGIC the nearest billable codes

# COMMAND ----------

# DBTITLE 1,Number of Nearest Billable Codes by Index
import plotly.express as px
import pandas as pf
_ps=best_icd_mapped_pdf['nearest_billable_code_pos'].value_counts()
data=_ps[_ps!='-']
data_pdf=pd.DataFrame({"count":data.values,"Index of Nearest Billable Codes":data.index})

fig = px.bar(data_pdf, x='Index of Nearest Billable Codes', y='count')
fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.3. See which indications have the highest average risk factor
# MAGIC In our pipeline we used `sbiobertresolve_icd10cm_augmented_billable_hcc` as a sentence resolver, in which the model return HCC codes. We can look at the distribution risk factors for each entity.
# MAGIC Note that since each category has a different number of corresponding data points, to get a full picture of the distribution of risk factors for each condition, we use box plots.

# COMMAND ----------

# DBTITLE 1,Distribution of risk per indication
import plotly.express as px

df = best_icd_mapped_pdf[best_icd_mapped_pdf.onc_code_desc!='-'].dropna()
fig = px.box(df, y="onc_code_desc", x="corresponding_hcc_score", hover_data=df.columns)
fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC As we can see, some categories, even with fewer cases, have higher risk factor.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.4. Analyze Oncological Entities
# MAGIC We can find the most frequent oncological entities.

# COMMAND ----------

onc_df = (
  icd10_hcc_df
  .filter("entity == 'Oncological'")
  .select("path","final_chunk","entity","icd10_code","icd_codes_names","icd_code_billable")
 )
onc_pdf=onc_df.toPandas()
onc_pdf.head(10)

# COMMAND ----------

# DBTITLE 1,Most Common Oncological Entities
import plotly.express as px

_ps=onc_pdf['icd_codes_names'].value_counts()
data=_ps[_ps.index!='-']
data_pdf=pd.DataFrame({"count":data.values,'icd code names':data.index})
data_pdf=data_pdf[data_pdf['count']>5]
fig = px.bar(data_pdf, y='icd code names', x='count',orientation='h')
fig.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Report Counts by ICD10CM Code Names
# MAGIC Each bar shows count of reports contain the cancer entities.

# COMMAND ----------

display(
  onc_df.select('icd_codes_names','path')
  .dropDuplicates()
  .groupBy('icd_codes_names')
  .count()
  .orderBy(F.desc('count'))
  .limit(20)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Most common symptoms
# MAGIC  We can find the most common symptoms counting the unique symptoms in documents.

# COMMAND ----------

display(
  icd10_hcc_df
  .filter("lower(entity)='symptom'")
  .selectExpr('path','icd_codes_names as symptom')
  .dropDuplicates()
  .groupBy('symptom')
  .count()
  .orderBy(F.desc('count'))
  .limit(30)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Extract most frequent oncological diseases and symptoms based on documents
# MAGIC 
# MAGIC Here, we will count the number documents for each symptom-disease pair. To do this, first we filter high confidence entities and then create a pivot table. 

# COMMAND ----------

entity_symptom_df = (
  icd10_hcc_df
  .select('path','entity','icd_codes_names')
  .filter("lower(entity) in ('symptom','oncological') AND confidence > 0.30")
  .dropDuplicates()
)
display(entity_symptom_df)

# COMMAND ----------

condition_symptom_df = (
  entity_symptom_df.groupBy('path').pivot("entity").agg(F.collect_list("icd_codes_names"))
  .withColumnRenamed('Oncological','Condition')
  .withColumn('Conditions',F.explode('Condition'))
  .withColumn('Symptoms',F.explode('Symptom'))
  .drop('Condition','Symptom')
  .dropna()
  .fillna(0)
)
display(condition_symptom_df)

# COMMAND ----------

conditions_symptoms_count_df=condition_symptom_df.groupBy('Conditions').pivot("Symptoms").count().fillna(0)
conditions_symptoms_count_pdf=conditions_symptoms_count_df.toPandas()
conditions_symptoms_count_pdf.index=conditions_symptoms_count_pdf['Conditions']
conditions_symptoms_count_pdf=conditions_symptoms_count_pdf.drop('Conditions',axis=1)

# COMMAND ----------

selected_rows=conditions_symptoms_count_pdf.index[conditions_symptoms_count_pdf.sum(axis=1)>10]
selected_columns=conditions_symptoms_count_pdf.columns[conditions_symptoms_count_pdf.sum(axis=0)>10]

# COMMAND ----------

data_pdf=conditions_symptoms_count_pdf.loc[selected_rows,selected_columns]

# COMMAND ----------

# MAGIC %md
# MAGIC Now let's visualize the heatmap of the co-occurence of conditions and symptoms. We can directly look at the counts of symptoms by condition

# COMMAND ----------

import plotly.express as px
def plot_heatmap(data,color='occurence'):
  fig = px.imshow(data,labels=dict(x="Condition", y="Symptom", color=color),y=list(data.index),x=list(data.columns))
  fig.update_layout(
    autosize=False,
    width=1100,
    height=1100,
  )
  fig.update_xaxes(side="top")
  return(fig)

# COMMAND ----------

fg=plot_heatmap(data_pdf)
fg.show()

# COMMAND ----------

# MAGIC %md
# MAGIC As we see, this heatmap does not take the expected frequency of a given symptom into account. In order to reflect any correlation between the symptom in question and a given condition, we need to normalize the counts. 
# MAGIC To do so, we use `MinMaxScaler` to scale the values. 

# COMMAND ----------

from sklearn.preprocessing import MinMaxScaler
normalized_data=MinMaxScaler().fit(data_pdf).transform(data_pdf)

# COMMAND ----------

norm_data_pdf=pd.DataFrame(normalized_data,index=data_pdf.index,columns=data_pdf.columns)
plot_heatmap(norm_data_pdf,'normalized occurence')

# COMMAND ----------

# MAGIC %md
# MAGIC As we can see, now the symptoms that were not appeared to be enriched show high correlation with corresponding conditions.

# COMMAND ----------

# MAGIC %md
# MAGIC # 2. Get Drug codes from the notes

# COMMAND ----------

# MAGIC %md
# MAGIC ## Analyze drug usage patterns for inventory management and reporting
# MAGIC 
# MAGIC We are checking how many times any drug are encountered in the documents.

# COMMAND ----------

rxnorm_res_df=spark.read.load(f'{delta_path}/gold/rxnorm-res-cleaned')

# COMMAND ----------

display(
  rxnorm_res_df
  .filter('confidence > 0.8')
  .groupBy('drugs')
  .count()
  .orderBy(F.desc('count'))
  .limit(20)
)

# COMMAND ----------

# MAGIC %md
# MAGIC # 3. Get Timeline Using RE Models

# COMMAND ----------

# MAGIC %md
# MAGIC ## Find the problems occured after treatments 
# MAGIC 
# MAGIC We are filtering the dataframe to select rows with following conditions to see problems occured after treatments.
# MAGIC * `relation =='AFTER'`
# MAGIC * `entity1=='TREATMENT'`
# MAGIC * `entity2=='PROBLEM'`

# COMMAND ----------

temporal_re_df=spark.read.load(f"{delta_path}/silver/temporal-re")

# COMMAND ----------

display(temporal_re_df)

# COMMAND ----------

# DBTITLE 1,Problems occuring after treatment
display(
  temporal_re_df
  .where("relation == 'AFTER' AND entity1=='TREATMENT' AND entity2 == 'PROBLEM'")
  .filter('confidence > 0.8')
  .orderBy(F.desc('confidence'))
)

# COMMAND ----------

# MAGIC %md
# MAGIC # 4. Analyze the Relations Between Body Parts and Procedures
# MAGIC 
# MAGIC In the extraction notebook, we created a relation extration model to identify relationships between body parts and problem entities by using pretrained **RelationExtractionModel** `re_bodypart_problem`. Now let's load the data and take a look at the relationship between bodypart and procedures. By filtering the dataframe to select rows satisfying `entity1 != entity2` we can see the relations between different entities and see the procedures applied to internal organs

# COMMAND ----------

bodypart_re_df=spark.read.load(f'{delta_path}/silver/bodypart-relationships')

# COMMAND ----------

display(
  bodypart_re_df
  .where('entity1!=entity2')
  .drop_duplicates()
  )

# COMMAND ----------

# MAGIC %md
# MAGIC # 5. Get Procedure codes from notes
# MAGIC 
# MAGIC We will created dataset for procedure codes, using `jsl_ner_wip_greedy_clinical` NER mdodle and set NerConverter's WhiteList `['Procedure']` in order to get only drug entities. Let's take a look at this table:

# COMMAND ----------

cpt_df=spark.read.load(f'{delta_path}/silver/cpt')

# COMMAND ----------

display(cpt_df)

# COMMAND ----------

# MAGIC %md
# MAGIC we can the see most common procedures being performed and count the number of each procedures and plot it.

# COMMAND ----------

#top 20
display(
  cpt_df
  .groupBy('cpt')
  .count()
  .orderBy(F.desc('count'))
  .limit(20)
)

# COMMAND ----------

# MAGIC %md
# MAGIC # 6. Get Assertion Status of Cancer Entities
# MAGIC 
# MAGIC Using the assertion status dataset we can find the number of family members of cancer patients with cancer or symptoms, and we can fruther check if the symptom is absent or present.

# COMMAND ----------

assertion_df=spark.read.load(f'{delta_path}/silver/assertion').drop_duplicates()

# COMMAND ----------

display(assertion_df)

# COMMAND ----------

n_associated_with_someone_else = assertion_df.where("assertion=='associated_with_someone_else'").count()
print(f"Number of family members have cancer or symptoms: {n_associated_with_someone_else} ")

# COMMAND ----------

display(assertion_df)

# COMMAND ----------

# DBTITLE 1,Assertion status of the most common symptoms 
display(
  assertion_df
  .groupBy('assertion')
  .count()
)

# COMMAND ----------

assertion_symptom_df= (
  assertion_df
  .where("assertion in ('present', 'absent') AND entity=='Symptom'")
)
most_common_symptoms_df=(
  assertion_symptom_df
  .select('path','chunk')
  .groupBy('chunk')
  .count()
  .orderBy(F.desc('count'))
  .limit(20)
  )
display(most_common_symptoms_df)

# COMMAND ----------

# DBTITLE 1,Common symptoms 
display(
  assertion_symptom_df
  .join(most_common_symptoms_df, on='chunk')
  .groupBy('chunk','assertion')
  .count()
  .orderBy(F.desc('count'))
  )

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
# MAGIC |Plotly |MIT License| https://github.com/plotly/plotly.py/blob/master/LICENSE.txt | https://github.com/plotly/plotly.py|
# MAGIC |Scikit-Learn |BSD 3-Clause| https://github.com/scikit-learn/scikit-learn/blob/main/COPYING | https://github.com/scikit-learn/scikit-learn/|
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