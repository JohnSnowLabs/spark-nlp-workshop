# Databricks notebook source
# MAGIC %md
# MAGIC # PHI De-identification
# MAGIC 
# MAGIC In this notebook we will:
# MAGIC   - Extract PHI entites from extracted texts.
# MAGIC   - Hide PHI entites and get an obfucated versions of pdf files.
# MAGIC 
# MAGIC   
# MAGIC see https://nlp.johnsnowlabs.com/2021/01/20/ner_deid_augmented_en.html for more information.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Initial Configurations

# COMMAND ----------

#run to hide log warnings
#%%python

import logging
logger = spark._jvm.org.apache.log4j
logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

# COMMAND ----------

import os
import json
import string

import numpy as np
import pandas as pd

import sparknlp
import sparknlp_jsl
from sparknlp.base import *
from sparknlp.util import *
from sparknlp.annotator import *
from sparknlp_jsl.base import *
from sparknlp_jsl.annotator import *
from sparknlp.pretrained import ResourceDownloader

import sparkocr
from sparkocr.transformers import *
from sparkocr.utils import *
from sparkocr.enums import *

from pyspark.sql import functions as F
from pyspark.ml import Pipeline, PipelineModel
from sparknlp.training import CoNLL

from sparknlp_display import NerVisualizer

import matplotlib.pyplot as plt

pd.set_option('max_colwidth', 100)
pd.set_option('display.max_columns', 100)  
pd.set_option('display.expand_frame_repr', False)

spark.sql("set spark.sql.legacy.allowUntypedScalaUDF=true")

print('sparknlp.version : ',sparknlp.version())
print('sparknlp_jsl.version : ',sparknlp_jsl.version())
print('sparkocr : ',sparkocr.version())

spark

# COMMAND ----------

# MAGIC %run ./03-config

# COMMAND ----------

util=SolAccUtil('phi_ocr')
util.print_paths()

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## 1. Load processed pdfs from delta lake

# COMMAND ----------

dbutils.fs.ls(f'{util.delta_path}/silver')

# COMMAND ----------

processed_pdf_df=spark.read.load(f'{util.delta_path}/silver/processed_pdf')
processed_pdf_df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Extracting and Hiding PHI Entities
# MAGIC 
# MAGIC In our documents we have some fields which we want to hide. To do it, we will use deidentification model. It identifies instances of protected health information in text documents, and it can either obfuscate them (e.g., replacing names with different, fake names) or mask them. 

# COMMAND ----------

documentAssembler = DocumentAssembler()\
  .setInputCol("corrected_text")\
  .setOutputCol("document")
 
sentenceDetector = SentenceDetectorDLModel.pretrained("sentence_detector_dl_healthcare","en","clinical/models")\
  .setInputCols(["document"]) \
  .setOutputCol("sentence")
 
tokenizer = Tokenizer()\
  .setInputCols(["sentence"])\
  .setOutputCol("token")\
 
word_embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models")\
  .setInputCols(["sentence", "token"])\
  .setOutputCol("embeddings")
 
deid_ner = MedicalNerModel.pretrained("ner_deid_generic_augmented", "en", "clinical/models") \
  .setInputCols(["sentence", "token", "embeddings"]) \
  .setOutputCol("ner")
 
deid_ner_converter = NerConverter() \
  .setInputCols(["sentence", "token", "ner"]) \
  .setOutputCol("ner_chunk")
 
deid_pipeline = Pipeline(
    stages = [
        documentAssembler,
        sentenceDetector,
        tokenizer,
        word_embeddings,
        deid_ner,
        deid_ner_converter])
 
empty_data = spark.createDataFrame([['']]).toDF("corrected_text")
deid_model = deid_pipeline.fit(empty_data)

# COMMAND ----------

# MAGIC %md
# MAGIC We created another pipeline which detects PHI entities. We will use the same text above and visualize again.

# COMMAND ----------

sample_text = processed_pdf_df.limit(2).select("corrected_text").collect()[0].corrected_text
light_deid_model =  LightPipeline(deid_model)
 
ann_text = light_deid_model.fullAnnotate(sample_text)[0]

chunks = []
entities = []
sentence= []
begin = []
end = []

for n in ann_text['ner_chunk']:
        
    begin.append(n.begin)
    end.append(n.end)
    chunks.append(n.result)
    entities.append(n.metadata['entity']) 
    sentence.append(n.metadata['sentence'])
    
df = pd.DataFrame({'chunks':chunks, 'begin': begin, 'end':end, 
                   'sentence_id':sentence, 'entities':entities})
				   
visualiser = NerVisualizer()

ner_vis = visualiser.display(ann_text, label_col='ner_chunk',return_html=True)
 
displayHTML(ner_vis)

# COMMAND ----------

obfuscation = DeIdentification()\
      .setInputCols(["sentence", "token", "ner_chunk"]) \
      .setOutputCol("deidentified") \
      .setMode("obfuscate")\
      .setObfuscateRefSource("faker")\
      .setObfuscateDate(True)

obfuscation_pipeline = Pipeline(stages=[
        deid_pipeline,
        obfuscation
    ])

# COMMAND ----------

from pyspark.sql.types import BinaryType

empty_data = spark.createDataFrame([['']]).toDF("corrected_text")
obfuscation_model = obfuscation_pipeline.fit(empty_data)

# COMMAND ----------

obfuscated_pdf_df = obfuscation_model.transform(processed_pdf_df)

# COMMAND ----------

obfuscated_pdf_df.select(processed_pdf_df.columns+['token.result','ner.result']).display()

# COMMAND ----------

result_df=(
  obfuscated_pdf_df
  .selectExpr("*", 'token.result as token_result', 'ner.result as ner_result', 'ner_chunk.result as ner_chunk_result', 'ner_chunk.metadata as ner_chunk_metadata','sentence.result as sentence_result', 'deidentified.result as deidentified_result')
  .select('id',
          'path',
          'total_pages',
          'documentnum',
          'pagenum',
          'corrected_image',
          'confidence',
          'corrected_text',
          F.arrays_zip('token_result', 'ner_result').alias('token_ner_res'),
          F.arrays_zip('ner_chunk_result', 'ner_chunk_metadata').alias('ner_chunk_res_meta'),
          F.arrays_zip('sentence_result', 'deidentified_result').alias('sentence_deid_res')
         )
)

# COMMAND ----------

# MAGIC %md
# MAGIC Let's count the number of entities we want to deidentificate and then see them.

# COMMAND ----------

(
  result_df
  .selectExpr("explode(token_ner_res) as col")
  .selectExpr("col['token_result'] as token","col['ner_result'] as ner_label")
  .groupBy('ner_label')
  .count()
  .orderBy('count', ascending=False)
).display()

# COMMAND ----------

result_df.selectExpr("explode(ner_chunk_res_meta) as cols").selectExpr("cols['ner_chunk_result'] as chunk","cols['ner_chunk_metadata']['entity'] as ner_label").display() 

# COMMAND ----------

# MAGIC %md
# MAGIC In deidentified column, entities like date and name are replaced by fake identities. Let's see some of them.

# COMMAND ----------

obfusated_text_df = (
  result_df
  .selectExpr('id', "explode(sentence_deid_res) as cols")
  .selectExpr('id', "cols['sentence_result'] as sentence","cols['deidentified_result'] as deidentified")
)
obfusated_text_df.display()

# COMMAND ----------

obfusated_text_pdf=obfusated_text_df.toPandas()
obfusated_text_pdf.iloc[4][['sentence','deidentified']]

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Getting Obfuscated Version of Each File
# MAGIC Now we have obfuscated version of each file in dataframe. Each page is in diiferent page. Let's merge and save the files as txt.

# COMMAND ----------

obfs_results_df=obfusated_text_df.groupby('id').agg(
  F.concat_ws(' ',F.collect_list('sentence')).alias('orig_text'),
  F.concat_ws(' ',F.collect_list('deidentified')).alias('deid_text'),
)

# COMMAND ----------

_sample=obfs_results_df.filter("orig_text rlike 'Vietnam'").collect()[0]
org_sample=(_sample['orig_text'])
deid_sample=(_sample['deid_text'])

# COMMAND ----------

org_sample.index('was born in')
deid_sample[deid_sample.index('was born in')-1:deid_sample.index('was born in')+50]

# COMMAND ----------

ind=org_sample.index('Vietnam')
org_sample[ind-10:ind+10],deid_sample[ind-10:ind+10]

# COMMAND ----------

ind1=org_sample.index('was born in')
ind2=deid_sample.index('was born in')
str1=org_sample[ind1-1:ind1+100]
str2=deid_sample[ind2-1:ind2+100]
html_str=f"""
<p>
<b>Original text</b><br>
<mark>{str1}</mark>
</p>
<p>
<b>deidentified text</b><br>
<mark>{str2}</mark>
</p>
"""
displayHTML(html_str)

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3.1. Write obfuscated texts to delta

# COMMAND ----------

obfs_results_df.selectExpr('id','deid_text as deidentified_notes').write.mode("overWrite").save(f"{util.delta_path}/silver/obfuscated_notes")