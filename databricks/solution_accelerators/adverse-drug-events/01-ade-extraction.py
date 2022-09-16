# Databricks notebook source
# MAGIC %md
# MAGIC # Extracting Entities and Relationships
# MAGIC In this notebook we use JohnSnow Lab's [pipelines for adverse drug events](https://nlp.johnsnowlabs.com/2021/07/15/explain_clinical_doc_ade_en.html) to extarct adverse events (ADE) and drug entities from a collection of 20,000 conversational texts. We then store the extracted entitites and raw data in delta lake and analyze the data in `02-ade-analysis` notebook. 

# COMMAND ----------

# MAGIC %md
# MAGIC **Initial Configurations**

# COMMAND ----------

import json
import os

from pyspark.ml import PipelineModel,Pipeline
from pyspark.sql import functions as F
from pyspark.sql.types import *

from sparknlp.annotator import *
from sparknlp_jsl.annotator import *
from sparknlp.base import *
import sparknlp_jsl
import sparknlp

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")
pd.set_option("display.max_colwidth",100)

print('sparknlp.version : ',sparknlp.version())
print('sparknlp_jsl.version : ',sparknlp_jsl.version())

spark

# COMMAND ----------

# MAGIC %md
# MAGIC For simplicity and ease of use, we run a notebook in the collection which contains definitions and classes for setting and creating paths as well as downloading relevant datasets for this excersize. 

# COMMAND ----------

# MAGIC %run ./03-config

# COMMAND ----------

# DBTITLE 1,initial configurations
ade_demo_util=SolAccUtil('ade')
ade_demo_util.print_paths()
ade_demo_util.display_data()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Download Dataset
# MAGIC 
# MAGIC We will use a slightly modified version of some conversational ADE texts which are downloaded from https://sites.google.com/site/adecorpus/home/document. See
# MAGIC >[Development of a benchmark corpus to support the automatic extraction of drug-related adverse effects from medical case reports](https://www.sciencedirect.com/science/article/pii/S1532046412000615)
# MAGIC for more information about this dataset.
# MAGIC 
# MAGIC **We will work with two main files in the dataset:**
# MAGIC 
# MAGIC - DRUG-AE.rel : Conversations with ADE.
# MAGIC - ADE-NEG.txt : Conversations with no ADE.
# MAGIC 
# MAGIC Lets get started with downloading these files.

# COMMAND ----------

# DBTITLE 1,download dataset
for file in ['DRUG-AE.rel','ADE-NEG.txt']:
  try:
    dbutils.fs.ls(f'{ade_demo_util.data_path}/{file}')
    print(f'{file} is already downloaded')
  except:
    ade_demo_util.load_remote_data(f'https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/tutorials/Certification_Trainings/Healthcare/data/ADE_Corpus_V2/{file}')
    
ade_demo_util.display_data()

# COMMAND ----------

# MAGIC %md
# MAGIC Now we will create a dataset of texts with the ground-truth classification, with respect to their ADE status.

# COMMAND ----------

# DBTITLE 1,dataframe for negative ADE texts 
neg_df = (
  spark.read.text(f"{ade_demo_util.data_path}/ADE-NEG.txt")
  .selectExpr("split(value,'NEG')[1] as text","1!=1 as is_ADE")
  .drop_duplicates()
)
display(neg_df.limit(20))

# COMMAND ----------

# DBTITLE 1,dataframe for positive ADE texts 
pos_df = (
  spark.read.csv(f"{ade_demo_util.data_path}/DRUG-AE.rel", sep="|", header=None)
  .selectExpr("_c1 as text", "1==1 as is_ADE")
  .drop_duplicates()
)

display(pos_df.limit(20))

# COMMAND ----------

# DBTITLE 1,dataframe for all conversational texts with labels
raw_data_df=neg_df.union(pos_df).selectExpr('uuid() as id','*').orderBy('id')
raw_data_df.display()

# COMMAND ----------

raw_data_df.groupBy('is_ADE').count().display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## write ade_events to Delta
# MAGIC We will combine the two dataframes and store the data in the bronze delta layer

# COMMAND ----------

raw_data_df.repartition(12).write.format('delta').mode('overwrite').save(f'{ade_demo_util.delta_path}/bronze/ade_events')

# COMMAND ----------

# MAGIC %md
# MAGIC # 1. Conversational ADE Classification

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1.1 Use Case: Text Classification According To Contains ADE or Not

# COMMAND ----------

# MAGIC %md
# MAGIC Now we will try to predict if a text contains ADE or not by using `classifierdl_ade_conversational_biobert`. For this, we will create a new dataframe merging all ADE negative and ADE positive texts and shuffle that.

# COMMAND ----------

ade_events_df=spark.read.load(f'{ade_demo_util.delta_path}/bronze/ade_events').orderBy(F.rand(seed=42)).repartition(64).cache()
display(ade_events_df.limit(20))

# COMMAND ----------

document_assembler = DocumentAssembler()\
        .setInputCol("text")\
        .setOutputCol("document")

tokenizer = Tokenizer()\
        .setInputCols(['document'])\
        .setOutputCol('token')

embeddings = BertEmbeddings.pretrained('biobert_pubmed_base_cased')\
        .setInputCols(["document", 'token'])\
        .setOutputCol("embeddings")

sentence_embeddings = SentenceEmbeddings() \
        .setInputCols(["document", "embeddings"]) \
        .setOutputCol("sentence_embeddings") \
        .setPoolingStrategy("AVERAGE")

conv_classifier = ClassifierDLModel.pretrained('classifierdl_ade_conversational_biobert', 'en', 'clinical/models')\
        .setInputCols(['document', 'token', 'sentence_embeddings'])\
        .setOutputCol('conv_class')

clf_pipeline = Pipeline(stages=[
    document_assembler, 
    tokenizer, 
    embeddings, 
    sentence_embeddings, 
    conv_classifier])

empty_data = spark.createDataFrame([['']]).toDF("text")
clf_model = clf_pipeline.fit(empty_data)

# COMMAND ----------

# MAGIC %md
# MAGIC Now we transform the conversational texts dataframe using the ADE calssifier pipeline and write the resulting dataframe to delta lake for future access.

# COMMAND ----------

clf_model_results_df=clf_model.transform(ade_events_df).select("id", "text", "is_ADE" ,"conv_class.result")
clf_model_results_df.write.format('delta').mode('overwrite').save(f'{ade_demo_util.delta_path}/silver/clf_model_results')

# COMMAND ----------

clf_model_results_df=(
  spark.read.load(f'{ade_demo_util.delta_path}/silver/clf_model_results')
  .selectExpr("id", "text", "is_ADE" ,"cast(result[0] AS BOOLEAN) as predicted_ADE")
)

# COMMAND ----------

display(clf_model_results_df)

# COMMAND ----------

clf_pdf=clf_model_results_df.selectExpr('cast(is_ADE as int) as ADE_actual', 'cast(predicted_ADE as int) as ADE_predicted').toPandas()
confusion_matrix = pd.crosstab(clf_pdf['ADE_actual'], clf_pdf['ADE_predicted'], rownames=['Actual'], colnames=['Predicted'])
confusion_matrix

# COMMAND ----------

# MAGIC %md
# MAGIC Based on the above conufsion matrix our model has an accuracy of `(TP+TN)/(P+N) = 86%`

# COMMAND ----------

(3249+14753)/(1022+3249+14753+1872)

# COMMAND ----------

# MAGIC %md
# MAGIC Lets get the `classifierdl_ade_conversational_biobert` model results in `conv_cl_result` column.

# COMMAND ----------

# MAGIC %md
# MAGIC # 2. ADE-DRUG NER Examination
# MAGIC Now we will extract `ADE` and `DRUG` entities from the conversational texts by using a combination of `ner_ade_clinical` and `ner_posology` models.

# COMMAND ----------

ade_df = spark.read.format('delta').load(f'{ade_demo_util.delta_path}/bronze/ade_events').drop("is_ADE").repartition(64)
display(ade_df.limit(20))

# COMMAND ----------

ade_df.count()

# COMMAND ----------

# DBTITLE 1,create pipeline
documentAssembler = DocumentAssembler()\
    .setInputCol("text")\
    .setOutputCol("document")

sentenceDetector = SentenceDetector()\
    .setInputCols(["document"])\
    .setOutputCol("sentence")

tokenizer = Tokenizer()\
    .setInputCols(["sentence"])\
    .setOutputCol("token")

word_embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models")\
    .setInputCols(["sentence", "token"])\
    .setOutputCol("embeddings")
  
ade_ner = MedicalNerModel.pretrained("ner_ade_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("ade_ner")

ade_ner_converter = NerConverter() \
    .setInputCols(["sentence", "token", "ade_ner"]) \
    .setOutputCol("ade_ner_chunk")\

pos_ner = MedicalNerModel.pretrained("ner_posology", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("pos_ner")

pos_ner_converter = NerConverter() \
    .setInputCols(["sentence", "token", "pos_ner"]) \
    .setOutputCol("pos_ner_chunk")\
    .setWhiteList(["DRUG"])

chunk_merger = ChunkMergeApproach()\
    .setInputCols("ade_ner_chunk","pos_ner_chunk")\
    .setOutputCol("ner_chunk")\


ner_pipeline = Pipeline(stages=[
    documentAssembler, 
    sentenceDetector,
    tokenizer,
    word_embeddings,
    ade_ner,
    ade_ner_converter,
    pos_ner,
    pos_ner_converter,
    chunk_merger
    ])


empty_data = spark.createDataFrame([[""]]).toDF("text")
ade_ner_model = ner_pipeline.fit(empty_data)

# COMMAND ----------

# DBTITLE 1,transform dataframe of texts
ade_ner_result_df = ade_ner_model.transform(ade_df)

# COMMAND ----------

# DBTITLE 1,write results to delta
ade_ner_result_df.write.format('delta').mode('overwrite').save(f'{ade_demo_util.delta_path}/silver/ade_ner_results')

# COMMAND ----------

# MAGIC %md
# MAGIC let's take a look at the  `ADE` and `DRUG` phrases detected in conversations

# COMMAND ----------

ade_ner_result_df=spark.read.load(f'{ade_demo_util.delta_path}/silver/ade_ner_results')

# COMMAND ----------

display(
  ade_ner_result_df
  .selectExpr('id', 'text','ner_chunk.result as ADE_phrases','size(ner_chunk.result)>0 as is_ADE')
              .filter('is_ADE')
              .limit(20)
)

# COMMAND ----------

# MAGIC %md
# MAGIC we can also look at the extracted chunks and their confidence

# COMMAND ----------

ade_ner_confidence_df = (
  ade_ner_result_df
  .select('id', F.explode(F.arrays_zip("ner_chunk.result","ner_chunk.metadata")).alias("cols"))
  .selectExpr('id', "cols['result'] as chunk",
              "cols['metadata']['entity'] as entity",
              "cast(cols['metadata']['confidence'] as double) as confidence")
)

# COMMAND ----------

ade_ner_confidence_df.display(10)

# COMMAND ----------

# DBTITLE 1,Write to GOLD
ade_ner_confidence_df.write.format('delta').mode('overwrite').save(f'{ade_demo_util.delta_path}/ade_ner_confidence')

# COMMAND ----------

# MAGIC %md
# MAGIC **Highlight the extracted entities on the raw text by using `sparknlp_display` library for better visual understanding.**

# COMMAND ----------

sample_text=(
  ade_ner_confidence_df
  .groupBy('id','entity').agg(F.count('entity').alias('count'),F.max('confidence'))
  .filter('count > 1')
  .orderBy('max(confidence)',desc=False)
  .select('id').dropDuplicates()
  .join(ade_df,on='id')
  .select('text')
  .limit(5)
).collect()

# COMMAND ----------

from sparknlp_display import NerVisualizer
visualiser = NerVisualizer()
light_model = LightPipeline(ade_ner_model)
for index, text in enumerate(sample_text):

    print("\n", "*"*50, f'Sample Text {index+1}', "*"*50, "\n")
    light_result = light_model.fullAnnotate(text)
    # change color of an entity label
    visualiser.set_label_colors({'ADE':'#ff037d', 'DRUG':'#7EBF9B'})    
    ner_vis = visualiser.display(light_result[0], label_col='ner_chunk', document_col='document', return_html=True)
    
    displayHTML(ner_vis)

# COMMAND ----------

# MAGIC %md
# MAGIC # 3. Get Assertion Status of ADE & DRUG Entities
# MAGIC In this section we will create a new pipeline by setting a WhiteList in `NerConverter` to get only `ADE` entities which comes from `ner_ade_clinical` model. Also will add the `assertion_dl` model to get the assertion status of them. We can use the same annotators that are common with the NER pipeline we created before.

# COMMAND ----------

ade_ner_converter = NerConverter() \
    .setInputCols(["sentence", "token", "ade_ner"]) \
    .setOutputCol("ade_ner_chunk")\
    .setWhiteList(["ADE"])
 
assertion = AssertionDLModel.pretrained("assertion_dl", "en", "clinical/models") \
    .setInputCols(["sentence", "ade_ner_chunk", "embeddings"]) \
    .setOutputCol("assertion")
 
assertion_pipeline = Pipeline(stages=[
    documentAssembler, 
    sentenceDetector,
    tokenizer,
    word_embeddings,
    ade_ner,
    ade_ner_converter,
    assertion
])
 
empty_data = spark.createDataFrame([[""]]).toDF("text")
assertion_model = assertion_pipeline.fit(empty_data)

# COMMAND ----------

assertion_df = assertion_model.transform(ade_df)

# COMMAND ----------

# MAGIC %md
# MAGIC **Now we will create a dataframe with `ADE` chunks and their assertion status and the confidence level of results.**

# COMMAND ----------

assertion_confidence_df = (
  assertion_df.withColumn("assertion_result", F.col("assertion.result"))
  .select('id', 'text', F.explode(F.arrays_zip("ade_ner_chunk.result","ade_ner_chunk.metadata", "assertion_result")).alias("cols"))
  .selectExpr('id', 'text', "cols['result'] as chunk",
              "cols['metadata']['entity'] as entity",
              "cols['assertion_result'] as assertion",
              "cols['metadata']['confidence'] as confidence")
)
assertion_confidence_df.display()

# COMMAND ----------

assertion_confidence_df.write.format('delta').mode('overwrite').option("overwriteSchema", "true").save(f'{ade_demo_util.delta_path}/gold/assertion_confidence')

# COMMAND ----------

# MAGIC %md
# MAGIC **Show the assertion status of the entities on the raw text.**

# COMMAND ----------

assertion_confidence_df = spark.read.load(f'{ade_demo_util.delta_path}/gold/assertion_confidence')

# COMMAND ----------

sample_text=(
  ade_ner_confidence_df
  .groupBy('id','entity').agg(F.count('entity').alias('count'),F.max('confidence'))
  .filter('count > 1')
  .orderBy('max(confidence)',desc=False)
  .select('id').dropDuplicates()
  .join(ade_df,on='id')
  .select('text')
  .limit(5)
).collect()

# COMMAND ----------

from sparknlp_display import AssertionVisualizer

assertion_vis = AssertionVisualizer()
as_light_model = LightPipeline(assertion_model)

for index, text in enumerate(sample_text):
    as_light_result = as_light_model.fullAnnotate(text)
    print("\n", "*"*50, f'Sample Text {index+1}', "*"*50, "\n")
    assertion_vis.set_label_colors({'ADE':'#113CB8'})
    assert_vis =     assertion_vis.display(as_light_result[0], 
                                            label_col = 'ade_ner_chunk', 
                                            assertion_col = 'assertion', 
                                            document_col = 'document',
                                            return_html=True
                                            )
    displayHTML(assert_vis)

# COMMAND ----------

# MAGIC %md
# MAGIC # 4. Analyze Relations Between ADE & DRUG Entities
# MAGIC We can extract the relations between `ADE` and `DRUG` entities by using `re_ade_clinical` model. We won't use `SentenceDetector` annotator in this pipeline to check the relations between entities in difference sentences.

# COMMAND ----------

documentAssembler = DocumentAssembler()\
    .setInputCol("text")\
    .setOutputCol("sentence")

tokenizer = Tokenizer()\
    .setInputCols(["sentence"])\
    .setOutputCol("token")

word_embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models")\
    .setInputCols(["sentence", "token"])\
    .setOutputCol("embeddings")
  
ade_ner = MedicalNerModel.pretrained("ner_ade_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("ner")

ner_converter = NerConverter() \
    .setInputCols(["sentence", "token", "ner"]) \
    .setOutputCol("ner_chunk")

pos_tagger = PerceptronModel.pretrained("pos_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token"])\
    .setOutputCol("pos_tags")    

dependency_parser = DependencyParserModel.pretrained("dependency_conllu", "en")\
    .setInputCols(["sentence", "pos_tags", "token"])\
    .setOutputCol("dependencies")

reModel = RelationExtractionModel.pretrained("re_ade_clinical", "en", 'clinical/models')\
    .setInputCols(["embeddings", "pos_tags", "ner_chunk", "dependencies"])\
    .setOutputCol("relations")\
    .setMaxSyntacticDistance(0)\
    .setRelationPairs(["ade-drug", "drug-ade"])


re_pipeline = Pipeline(stages=[
    documentAssembler, 
    tokenizer,
    word_embeddings,
    ade_ner,
    ner_converter,
    pos_tagger,
    dependency_parser,
    reModel
])

empty_data = spark.createDataFrame([[""]]).toDF("text")
re_model = re_pipeline.fit(empty_data)

# COMMAND ----------

relations_df = re_model.transform(ade_df)

# COMMAND ----------

# MAGIC %md
# MAGIC **Now we can show our detected entities, their relations and confidence levels in a dataframe.**

# COMMAND ----------

relations_confidence_df = (
  relations_df
  .select('id','text', F.explode(F.arrays_zip('relations.result', 'relations.metadata')).alias("cols"))
  .selectExpr('id','text', "cols['result'] as relation",
              "cols['metadata']['entity1'] as entity1",
              "cols['metadata']['chunk1'] as chunk1",
              "cols['metadata']['entity2'] as entity2",
              "cols['metadata']['chunk2'] as chunk2",
              "cols['metadata']['confidence'] as confidence")
)

# COMMAND ----------

relations_confidence_df.write.format('delta').mode('overwrite').save(f'{ade_demo_util.delta_path}/gold/relations_confidence')

# COMMAND ----------

# MAGIC %md
# MAGIC **Show the relations on the raw text bu using `sparknlp_display` library.**

# COMMAND ----------

relations_confidence_df=spark.read.load(f'{ade_demo_util.delta_path}/gold/relations_confidence')

# COMMAND ----------

sample_text=(
  relations_confidence_df
  .groupBy('id','relation').agg(F.count('relation').alias('count'),F.max('confidence'))
  .filter('count > 2')
  .orderBy('max(confidence)',desc=False)
  .select('id').dropDuplicates()
  .join(ade_df,on='id')
  .select('text')
  .limit(5)
).collect()

# COMMAND ----------

from sparknlp_display import RelationExtractionVisualizer

re_light_model = LightPipeline(re_model)
re_vis = RelationExtractionVisualizer()

# sample_text = df.filter(df["id"].isin([12, 34, 29, 4256, 1649])).select(["text"]).collect()

for index, text in enumerate(sample_text):

    print("\n", "*"*50, f'Sample Text {index+1}', "*"*50, "\n")
    
    re_light_result = re_light_model.fullAnnotate(text)

    relation_vis = re_vis.display(re_light_result[0],
                                  relation_col = 'relations',
                                  document_col = 'sentence',
                                  show_relations=True,
                                  return_html=True
                                   )
    
    displayHTML(relation_vis)

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