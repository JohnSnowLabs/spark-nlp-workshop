# Databricks notebook source
# MAGIC %md
# MAGIC #Abstracting Real World Data from Oncology Notes: Entity Extraction
# MAGIC [MT ONCOLOGY NOTES](https://www.mtsamplereports.com/) comprises of millions of ehr records of patients. It contains semi-structured data like demographics, insurance details, and a lot more, but most importantly, it also contains free-text data like real encounters and notes.
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
# MAGIC 
# MAGIC Please use a cluster with **9.1 ML CPU** Runtime.

# COMMAND ----------

# MAGIC %md
# MAGIC ##0. Initial configurations

# COMMAND ----------

# MAGIC %pip install mlflow

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

from pyspark.sql import functions as F
from pyspark.ml import Pipeline, PipelineModel
from sparknlp.training import CoNLL

pd.set_option('max_colwidth', 100)
pd.set_option('display.max_columns', 100)  
pd.set_option('display.expand_frame_repr', False)

print('sparknlp.version : ',sparknlp.version())
print('sparknlp_jsl.version : ',sparknlp_jsl.version())

spark


# COMMAND ----------

# MAGIC %md
# MAGIC ### Download oncology notes

# COMMAND ----------

# MAGIC %run
# MAGIC ./04-config

# COMMAND ----------

data_path = '/FileStore/HLS/nlp/data/'

ade_demo_util=SolAccUtil('onc-lh',data_path=data_path)
ade_demo_util.print_info()

# COMMAND ----------

mlflow.set_experiment(ade_demo_util.settings['experiment_name'])

# COMMAND ----------

data_path=ade_demo_util.settings['data_path']
os.environ['data_path']=f'/dbfs{data_path}'
delta_path=ade_demo_util.settings['delta_path']
notes_path = f'{data_path}/mt_onc_50/'

# COMMAND ----------

# DBTITLE 1,download data
# MAGIC %sh
# MAGIC cd $data_path
# MAGIC wget https://hls-eng-data-public.s3.amazonaws.com/data/mt_onc_50.zip
# MAGIC unzip -o mt_onc_50.zip

# COMMAND ----------

display(dbutils.fs.ls(notes_path),10)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Read Data and Write to Bronze Delta Layer
# MAGIC 
# MAGIC There are 50 clinical notes stored in delta table. We read the data nd write the raw notes data into bronze delta tables

# COMMAND ----------

df = sc.wholeTextFiles(notes_path).toDF().withColumnRenamed('_1','path').withColumnRenamed('_2','text')
display(df.limit(5))

# COMMAND ----------

df.count()

# COMMAND ----------

# DBTITLE 1,write to delta bronze layer
df.write.format('delta').mode('overwrite').save(f'{delta_path}/bronze/mt-oc-notes')
display(dbutils.fs.ls(f'{delta_path}/bronze/mt-oc-notes'))

# COMMAND ----------

sample_text = df.limit(1).select("text").collect()[0]

# COMMAND ----------

# MAGIC %md
# MAGIC ### Setup initial NLP pipelines and stages
# MAGIC First let's define all stages that are common among all downstream pipelines

# COMMAND ----------

documentAssembler = DocumentAssembler()\
  .setInputCol("text")\
  .setOutputCol("document")

documentAssemblerResolver = DocumentAssembler()\
  .setInputCol("text")\
  .setOutputCol("ner_chunks")

sentenceDetector = SentenceDetectorDLModel.pretrained("sentence_detector_dl_healthcare","en","clinical/models") \
  .setInputCols(["document"]) \
  .setOutputCol("sentence")

tokenizer = Tokenizer()\
  .setInputCols(["sentence"])\
  .setOutputCol("token")

word_embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models")\
  .setInputCols(["sentence", "token"])\
  .setOutputCol("embeddings")


# COMMAND ----------

base_stages = [
        documentAssembler,
        sentenceDetector,
        tokenizer,
        word_embeddings
]

# COMMAND ----------

# MAGIC %md
# MAGIC ### Vizualize the Entities Using Spark NLP Display Library

# COMMAND ----------

# MAGIC %md
# MAGIC At first, we will create a NER pipeline. And then, we can see the labbeled entities on text.

# COMMAND ----------

# Cancer
bionlp_ner = MedicalNerModel.pretrained("ner_bionlp", "en", "clinical/models") \
  .setInputCols(["sentence", "token", "embeddings"]) \
  .setOutputCol("bionlp_ner")\
  .setBatchSize(128)\
  .setIncludeConfidence(False)

bionlp_ner_converter = NerConverter() \
  .setInputCols(["sentence", "token", "bionlp_ner"]) \
  .setOutputCol("bionlp_ner_chunk")\
  .setWhiteList(["Cancer"])

# Clinical Terminology
jsl_ner = MedicalNerModel.pretrained("jsl_ner_wip_clinical", "en", "clinical/models") \
  .setInputCols(["sentence", "token", "embeddings"]) \
  .setOutputCol("jsl_ner")\
  .setBatchSize(128)\
  .setIncludeConfidence(False)

jsl_ner_converter = NerConverter() \
  .setInputCols(["sentence", "token", "jsl_ner"]) \
  .setOutputCol("jsl_ner_chunk")\
  .setWhiteList(["Oncological", "Symptom", "Treatment"])

# COMMAND ----------

# MAGIC %md
# MAGIC We used two diferent NER models (`jsl_ner_wip_clinical` and `bionlp_ner`) and we need to merge them by a chunk merger. There are two different entities related to oncology. So we will change `Cancer` entities to `Oncological` by `setReplaceDictResource` parameter. This parameter gets the list from a csv file. Before merging the entities, we are creating the csv file with a row `Cancer,Oncological`.

# COMMAND ----------

dbutils.fs.put('/tmp/replace_dict.csv','Cancer,Oncological',overwrite=True)

chunk_merger = ChunkMergeApproach()\
  .setInputCols("bionlp_ner_chunk","jsl_ner_chunk")\
  .setOutputCol("final_ner_chunk")\
  .setReplaceDictResource('/tmp/replace_dict.csv',"text", {"delimiter":","})

ner_pipeline= Pipeline(
                        stages = base_stages+[
                            bionlp_ner,
                            bionlp_ner_converter,
                            jsl_ner,
                            jsl_ner_converter,
                            chunk_merger]
)

empty_data = spark.createDataFrame([['']]).toDF("text")
ner_model = ner_pipeline.fit(empty_data)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Now we will visualize a sample text with `NerVisualizer`. Since `NerVisualizer` woks with Lightpipeline, so we will create a `light_model` with our `ner_model_model`.

# COMMAND ----------

light_model =  LightPipeline(ner_model)
ann_text = light_model.fullAnnotate(sample_text)[0]
ann_text.keys()

# COMMAND ----------

from sparknlp_display import NerVisualizer

visualiser = NerVisualizer()

# Change color of an entity label
visualiser.set_label_colors({'ONCOLOGICAL':'#ff2e51', 'TREATMENT': '#3bdeff', 'SYMPTOM': '#00ff40' })

ner_vis = visualiser.display(ann_text, label_col='final_ner_chunk',return_html=True)

displayHTML(ner_vis)

# COMMAND ----------

# MAGIC 
# MAGIC 
# MAGIC 
# MAGIC %md
# MAGIC ## 1. ICD-10 code extraction
# MAGIC In this step we get ICD-10 codes using entity resolvers and use the data for various use cases.
# MAGIC We can use `hcc_billable` entity resolver to get ICD10-CM codes for identified entities. The unique this about this resolver is it also provides HCC risk factor and billable status for each ICD code. We can use this information for a lot of tasks.

# COMMAND ----------

# MAGIC %md
# MAGIC Now we will transform our dataframe by using `ner_model` that we already created, and then we will get the `ner_chunks` into a list to use for the resolver LightPipeline.

# COMMAND ----------

ner_res = ner_model.transform(df)

# COMMAND ----------

# MAGIC %md
# MAGIC Optionally we can also store `ner_res` data into the broze delta laeyer for future accesibility

# COMMAND ----------

ner_res.repartition('path').write.format('delta').mode('overwrite').save(f'{delta_path}/bronze/ner-res-notes')

# COMMAND ----------

ner_pdf = ner_res.select("path", F.explode(F.arrays_zip('final_ner_chunk.result', 
                                                       'final_ner_chunk.metadata')).alias("cols"))\
                .select("path", F.expr("cols['result']").alias("final_chunk"), 
                                F.expr("cols['metadata']['entity']").alias("entity"))\
                .toPandas()

ner_chunks = list(ner_pdf.final_chunk)
display(ner_pdf)

# COMMAND ----------

# MAGIC %md
# MAGIC We are creating resolver PipelineModel with `document_assembler`, `sbert_jsl_medium_uncased` embedding and `sbertresolve_icd10cm_slim_billable_hcc_med` resolver. 

# COMMAND ----------

sbert_embedder = BertSentenceEmbeddings.pretrained("sbert_jsl_medium_uncased", 'en', 'clinical/models')\
  .setInputCols(["ner_chunks"])\
  .setOutputCol("sentence_embeddings")

icd10_resolver = SentenceEntityResolverModel.pretrained("sbertresolve_icd10cm_slim_billable_hcc_med","en", "clinical/models")\
  .setInputCols(["ner_chunks", "sentence_embeddings"]) \
  .setOutputCol("icd10_code")\
  .setDistanceFunction("EUCLIDEAN")

icd_pipelineModel = PipelineModel(stages=[
            documentAssemblerResolver,
            sbert_embedder,
            icd10_resolver
            ])

# COMMAND ----------

icd10_hcc_lp = LightPipeline(icd_pipelineModel)
icd10_hcc_result = icd10_hcc_lp.fullAnnotate(ner_chunks)

# COMMAND ----------

# MAGIC %md
# MAGIC Now we will create a pandas dataframe to show the results obviously. We will walk on the `icd10_hcc_result` line by line and take icd10 code (`icd10_code`), confidence levels (`confidence`), all possible codes (`all_k_results`), resolutions of the all possible codes (`all_k_resolutions`) and HCC details (`all_k_aux_labels`) of the icd10 code. 

# COMMAND ----------

tuples = []

for i in range(len(icd10_hcc_result)):
    for x,y in zip(icd10_hcc_result[i]["ner_chunks"], icd10_hcc_result[i]["icd10_code"]):
        tuples.append((ner_pdf.path.iloc[i],x.result, ner_pdf.entity.iloc[i], y.result, y.metadata["confidence"], y.metadata["all_k_results"], y.metadata["all_k_resolutions"], y.metadata["all_k_aux_labels"]))

icd10_hcc_pdf = pd.DataFrame(tuples, columns=["path", "final_chunk", "entity", "icd10_code", "confidence", "all_codes", "resolutions", "hcc_list"])


codes = []
resolutions = []
hcc_all = []

for code, resolution, hcc in zip(icd10_hcc_pdf['all_codes'], icd10_hcc_pdf['resolutions'], icd10_hcc_pdf['hcc_list']):
    
    codes.append( code.split(':::'))
    resolutions.append(resolution.split(':::'))
    hcc_all.append(hcc.split(":::"))

icd10_hcc_pdf['all_codes'] = codes  
icd10_hcc_pdf['resolutions'] = resolutions
icd10_hcc_pdf['hcc_list'] = hcc_all

# COMMAND ----------

# MAGIC %md
# MAGIC The values in `billable`, `hcc_store` and `hcc_status` columns are seperated by `||` and we will change them to a list.

# COMMAND ----------

def extract_billable(bil):
  
  billable = []
  status = []
  score = []

  for b in bil:
    billable.append(b.split("||")[0])
    status.append(b.split("||")[1])
    score.append(b.split("||")[2])

  return (billable, status, score)

icd10_hcc_pdf["hcc_status"] = icd10_hcc_pdf["hcc_list"].apply(extract_billable).apply(pd.Series).iloc[:,1]
icd10_hcc_pdf["hcc_score"] = icd10_hcc_pdf["hcc_list"].apply(extract_billable).apply(pd.Series).iloc[:,2]
icd10_hcc_pdf["billable"] = icd10_hcc_pdf["hcc_list"].apply(extract_billable).apply(pd.Series).iloc[:,0]

icd10_hcc_pdf.drop("hcc_list", axis=1, inplace= True)
icd10_hcc_pdf['icd_codes_names'] = icd10_hcc_pdf['resolutions'].apply(lambda x : x[0].split("[")[0])
icd10_hcc_pdf['icd_code_billable'] = icd10_hcc_pdf['billable'].apply(lambda x : x[0])

# COMMAND ----------

# MAGIC %md
# MAGIC #### Write `icd10_hcc_df` to Delta
# MAGIC Now we proceed to write resolved ICD10 codes which also contain information regarding HCC status corresponding to each code as one of the silver delta tables in our clinical lakehouse

# COMMAND ----------

icd10_hcc_df = spark.createDataFrame(icd10_hcc_pdf)
icd10_hcc_df.write.format('delta').mode('overwrite').save(f'{delta_path}/silver/icd10-hcc-df')

# COMMAND ----------

display(icd10_hcc_df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Preparing reimbursement-ready data with billable codes
# MAGIC 
# MAGIC Here, we will check how many of the ICD codes are billable.

# COMMAND ----------

print(icd10_hcc_pdf['icd_code_billable'].value_counts())

# COMMAND ----------

import seaborn as sns
import matplotlib.pyplot as plt
plt.figure(figsize=(3,4), dpi=200)
plt.pie(icd10_hcc_pdf['icd_code_billable'].value_counts(), 
        labels = ["billable", "not billable"], 
        autopct = "%1.1f%%"
       )
plt.title("Ratio Billable & Non-billable Codes", size=10)
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC As we can see, some of the best matching codes are not billable. For such indications we can find codes that are relevant as well as billable

# COMMAND ----------

icd10_oncology_mapping = {"C81-C96": "Malignant neoplasms of lymphoid, hematopoietic and related tissue",
                          "C76-C80": "Malignant neoplasms of ill-defined, other secondary and unspecified sites",
                          "D00-D09": "In situ neoplasms",
                          "C51-C58": "Malignant neoplasms of female genital organs",
                          "C43-C44": "Melanoma and other malignant neoplasms of skin",
                          "C15-C26": "Malignant neoplasms of digestive organs",
                          "C73-C75": "Malignant neoplasms of thyroid and other endocrine glands",
                          "D60-D64": "Aplastic and other anemias and other bone marrow failure syndromes",
                          "E70-E88": "Metabolic disorders",
                          "G89-G99": "Other disorders of the nervous system",
                          "R50-R69": "General symptoms and signs",
                          "R10-R19": "Symptoms and signs involving the digestive system and abdomen",
                          "Z00-Z13": "Persons encountering health services for examinations"}


def map_to_parent(x):
    charcode = x[0].lower()
    numcodes = int(x[1])
    
    for k, v in icd10_oncology_mapping.items():
        
        lower, upper = k.split('-')
        
        if charcode >= lower[0].lower() and numcodes >= int(lower[1]):
            
            if charcode < upper[0].lower():
                return v
            elif charcode == upper[0].lower() and numcodes <= int(upper[1]):
                return v

# COMMAND ----------

icd10_hcc_pdf["onc_code_desc"] = icd10_hcc_pdf["icd10_code"].apply(map_to_parent).fillna("-")

# COMMAND ----------

best_paid_icd_matches = []
indication_with_no_billable_icd = []

for i_, row in icd10_hcc_pdf.iterrows():
    if '1' not in row['billable']:
        indication_with_no_billable_icd.append([row['final_chunk'], 
                                      row['resolutions'][0], 
                                      row['all_codes'][0],
                                      row['billable'][0],
                                      row['hcc_score'][0],
                                      row['onc_code_desc'], 
                                      "-" ])
    else:
        n_zero_ind = list(row['billable']).index('1')
        best_paid_icd_matches.append([row['final_chunk'], 
                                      row['resolutions'][n_zero_ind], 
                                      row['all_codes'][n_zero_ind],
                                      row['billable'][n_zero_ind],
                                      row['hcc_score'][n_zero_ind],
                                      row['onc_code_desc'],
                                      n_zero_ind])

best_icd_mapped_pdf = pd.DataFrame(best_paid_icd_matches, columns=['ner_chunk', 'code_desc', 'code' , 'billable', 
                                             'corresponding_hcc_score', 'onc_code_desc', 'nearest_billable_code_pos'])
best_icd_mapped_pdf['corresponding_hcc_score'] = pd.to_numeric(best_icd_mapped_pdf['corresponding_hcc_score'], errors='coerce')

best_icd_mapped_pdf.head()

# COMMAND ----------

# MAGIC %md
# MAGIC **All chunks have been mapped to payable ICD codes**

# COMMAND ----------

print(best_icd_mapped_pdf.billable.value_counts())

# COMMAND ----------

# MAGIC %md
# MAGIC #### Write `best_icd_mapped_df` to Delta
# MAGIC Now we can write the reimbursement-ready data with billable codes into a gold delta layer, which can be accessed for reporting and BI

# COMMAND ----------

best_icd_mapped_df = spark.createDataFrame(best_icd_mapped_pdf)
best_icd_mapped_df.write.format('delta').mode('overwrite').save(f'{delta_path}/gold/best-icd-mapped')

# COMMAND ----------

display(best_icd_mapped_df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Get Drug codes from the notes
# MAGIC 
# MAGIC We will create a new pipeline to get drug codes. As NER model, we are using `ner_posology_large` and setting NerConverter's WhiteList `['DRUG']` in order to get only drug entities.

# COMMAND ----------

## to get drugs
drugs_ner_ing = MedicalNerModel.pretrained("ner_posology_large", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("ner_drug")\
    .setIncludeConfidence(False)

drugs_ner_converter_ing = NerConverter() \
    .setInputCols(["sentence", "token", "ner_drug"]) \
    .setOutputCol("ner_chunk")\
    .setWhiteList(["DRUG"])
      
pipeline_rxnorm_ingredient = Pipeline(
    stages = [
        documentAssembler,
        sentenceDetector,
        tokenizer,
        word_embeddings,
        drugs_ner_ing,
        drugs_ner_converter_ing])

data_ner = spark.createDataFrame([['']]).toDF("text")
rxnorm_ner_model = pipeline_rxnorm_ingredient.fit(data_ner)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Visualize Drug Entities
# MAGIC 
# MAGIC Now we will visualize a sample text with `NerVisualizer`.

# COMMAND ----------

# MAGIC %md
# MAGIC `NerVisualizer` works with LightPipeline, so we will create a `rxnorm_lp` with our `rxnorm_model`.

# COMMAND ----------

rxnorm_ner_lp = LightPipeline(rxnorm_ner_model)

ann_text = rxnorm_ner_lp.fullAnnotate(sample_text)[0]
print(ann_text.keys())

# COMMAND ----------

#Creating the vizualizer 
from sparknlp_display import NerVisualizer

visualiser = NerVisualizer()

# Change color of an entity label
visualiser.set_label_colors({'DRUG':'#008080'})
ner_vis = visualiser.display(ann_text, label_col='ner_chunk',return_html=True)

#Displaying the vizualizer 
displayHTML(ner_vis)

# COMMAND ----------

# MAGIC %md
# MAGIC Now we will take rxnorm ner_chunks into a list for using in resolver pipeline

# COMMAND ----------

rxnorm_code_res_df = rxnorm_ner_lp.transform(df) 

# COMMAND ----------

rxnorm_code_res_pdf = rxnorm_code_res_df.select("path", F.explode(F.arrays_zip('ner_chunk.result', 
                                                                      'ner_chunk.metadata')).alias("cols"))\
                         .select("path", F.expr("cols['result']").alias("ner_chunk"), 
                                         F.expr("cols['metadata']['entity']").alias("entity")).toPandas()

rxnorm_ner_chunks = list(rxnorm_code_res_pdf.ner_chunk)

# COMMAND ----------

# MAGIC %md
# MAGIC We will create our resolver pipeline and get rxnorm codes of these ner_chunks.

# COMMAND ----------

sbert_embedder = BertSentenceEmbeddings.pretrained("sbiobert_base_cased_mli", 'en', 'clinical/models')\
  .setInputCols(["ner_chunks"])\
  .setOutputCol("sentence_embeddings")

rxnorm_resolver = SentenceEntityResolverModel.pretrained("sbiobertresolve_rxnorm_augmented","en", "clinical/models")\
  .setInputCols(["ner_chunks", "sentence_embeddings"]) \
  .setOutputCol("rxnorm_code")\
  .setDistanceFunction("EUCLIDEAN")

rxnorm_pipelineModel = PipelineModel(stages=[
            documentAssemblerResolver,
            sbert_embedder,
            rxnorm_resolver
            ])

# COMMAND ----------

rxnorm_resolver_lp = LightPipeline(rxnorm_pipelineModel)

# COMMAND ----------

rxnorm_code_res = rxnorm_resolver_lp.fullAnnotate(rxnorm_ner_chunks)

# COMMAND ----------

# MAGIC %md
# MAGIC We are selecting the columns which we need and convert to Pandas DataFrame. The values in `all_codes` and `resolitions` columns are seperated by ":::" and we are converting these columns to lists.

# COMMAND ----------

tuples = []

for i in range(len(rxnorm_code_res)):
    for x,y in zip(rxnorm_code_res[i]["ner_chunks"], rxnorm_code_res[i]["rxnorm_code"]):
        tuples.append((rxnorm_code_res_pdf.path.iloc[i],x.result, y.result, y.metadata["confidence"], y.metadata["all_k_results"], y.metadata["all_k_resolutions"]))

rxnorm_res_cleaned_pdf = pd.DataFrame(tuples, columns=["path", "drug_chunk", "rxnorm_code", "confidence", "all_codes", "resolutions"])


codes = []
resolutions = []

for code, resolution in zip(rxnorm_res_cleaned_pdf['all_codes'], rxnorm_res_cleaned_pdf['resolutions']):
    
    codes.append(code.split(':::'))
    resolutions.append(resolution.split(':::'))
    
  
rxnorm_res_cleaned_pdf['all_codes'] = codes  
rxnorm_res_cleaned_pdf['resolutions'] = resolutions
rxnorm_res_cleaned_pdf['drugs'] = rxnorm_res_cleaned_pdf['resolutions'].apply(lambda x : x[0])

# COMMAND ----------

display(rxnorm_res_cleaned_pdf.head(5))

# COMMAND ----------

# MAGIC %md
# MAGIC #### Write `rxnorm_res_cleaned_df `to Delta

# COMMAND ----------

rxnorm_res_cleaned_df = spark.createDataFrame(rxnorm_res_cleaned_pdf)
rxnorm_res_cleaned_df.write.format('delta').mode('overwrite').save(f'{delta_path}/gold/rxnorm-res-cleaned')

# COMMAND ----------

display(rxnorm_res_cleaned_df.limit(5))

# COMMAND ----------

# MAGIC %md
# MAGIC Checking all posology entities `DRUG`, `FREQUENCY`, `DURATION`, `STRENGTH`, `FORM`, `DOSAGE` and `ROUTE` and their RXNORM Code by using `ner_posology_greedy` model. <br/>
# MAGIC We will take our greedy chunks into rxnorm resolver to see what will change

# COMMAND ----------

documentAssembler = DocumentAssembler()\
    .setInputCol("text")\
    .setOutputCol("document")

sentenceDetector = SentenceDetectorDLModel.pretrained("sentence_detector_dl_healthcare","en","clinical/models") \
    .setInputCols(["document"]) \
    .setOutputCol("sentence")

tokenizer = Tokenizer()\
    .setInputCols(["sentence"])\
    .setOutputCol("token")\

word_embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models")\
    .setInputCols(["sentence", "token"])\
    .setOutputCol("embeddings")

## to get drugs
drugs_ner_ing = MedicalNerModel.pretrained("ner_posology_greedy", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("ner_drug")

drugs_ner_converter_ing = NerConverter() \
    .setInputCols(["sentence", "token", "ner_drug"]) \
    .setOutputCol("ner_chunk_drug")\
    .setWhiteList(["DRUG"])

greedy_ner_converter_ing = NerConverter() \
    .setInputCols(["sentence", "token", "ner_drug"]) \
    .setOutputCol("ner_chunk_greedy")

drugs_c2doc = Chunk2Doc().setInputCols("ner_chunk_drug").setOutputCol("ner_chunk_doc") 

sbert_embedder_ing = BertSentenceEmbeddings.pretrained("sbiobert_base_cased_mli", 'en', 'clinical/models')\
    .setInputCols(["ner_chunk_doc"])\
    .setOutputCol("sentence_embeddings")

rxnorm_resolver = SentenceEntityResolverModel.pretrained("sbiobertresolve_rxnorm_augmented","en", "clinical/models")\
    .setInputCols(["ner_chunk_drug", "sentence_embeddings"]) \
    .setOutputCol("rxnorm_code")\
    .setDistanceFunction("EUCLIDEAN")
    

pipeline_rxnorm_ingredient = Pipeline(
    stages = [
        documentAssembler,
        sentenceDetector,
        tokenizer,
        word_embeddings,
        drugs_ner_ing,
        drugs_ner_converter_ing, 
        greedy_ner_converter_ing,
        drugs_c2doc, 
        sbert_embedder_ing,
        rxnorm_resolver])

data_ner = spark.createDataFrame([['']]).toDF("text")
rxnorm_model = pipeline_rxnorm_ingredient.fit(data_ner)

# COMMAND ----------

rxnorm_greedy_lp = LightPipeline(rxnorm_model)

# COMMAND ----------

ann_text = rxnorm_greedy_lp.fullAnnotate(sample_text)[0]
print(ann_text.keys())

# COMMAND ----------

# MAGIC %md
# MAGIC Visualize Greedy Algorithm Entities without WhiteList

# COMMAND ----------

#Creating the vizualizer 
from sparknlp_display import NerVisualizer

visualiser = NerVisualizer()

# Change color of an entity label
visualiser.set_label_colors({'DRUG':'#008080'})
ner_vis = visualiser.display(ann_text, label_col='ner_chunk_greedy',return_html=True)

#Displaying the vizualizer 
displayHTML(ner_vis)

# COMMAND ----------

rxnorm_code_res = rxnorm_model.transform(df) 

# COMMAND ----------

rxnorm_res = rxnorm_code_res.select("path", F.explode(F.arrays_zip( rxnorm_code_res.ner_chunk_drug.result, rxnorm_code_res.rxnorm_code.result, rxnorm_code_res.rxnorm_code.metadata)).alias("cols"))\
                            .select("path", F.expr("cols['0']").alias("drug_chunk"),
                                            F.expr("cols['1']").alias("rxnorm_code"),
                                            F.expr("cols['2']['confidence']").alias("confidence"),
                                            F.expr("cols['2']['all_k_results']").alias("all_codes"),
                                            F.expr("cols['2']['all_k_resolutions']").alias("resolutions")).toPandas()


codes = []
resolutions = []

for code, resolution in zip(rxnorm_res['all_codes'], rxnorm_res['resolutions']):
    
    codes.append(code.split(':::'))
    resolutions.append(resolution.split(':::'))
    
  
rxnorm_res['all_codes'] = codes  
rxnorm_res['resolutions'] = resolutions
rxnorm_res['drugs'] = rxnorm_res['resolutions'].apply(lambda x : x[0])

# COMMAND ----------

rxnorm_res.head(5)

# COMMAND ----------

rxnorm_code_greedy_res_pdf = rxnorm_code_res.select("path", F.explode(F.arrays_zip('ner_chunk_drug.result', 
                                                               'ner_chunk_drug.metadata')).alias("cols"))\
                         .select("path", F.expr("cols['result']").alias("ner_chunk"), 
                                         F.expr("cols['metadata']['entity']").alias("entity")).toPandas()

# COMMAND ----------

# MAGIC %md
# MAGIC #### Write `rxnorm_code_greedy_res_df` to Delta

# COMMAND ----------

rxnorm_code_greedy_res_df=spark.createDataFrame(rxnorm_code_greedy_res_pdf)
rxnorm_code_greedy_res_df.write.format('delta').mode("overwrite").save(f"{delta_path}/silver/rxnorm-code-greedy-res")

# COMMAND ----------

display(rxnorm_code_greedy_res_df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Get Timeline Using RE Models
# MAGIC 
# MAGIC We will create a relation extration model to identify temporal relationships among clinical events by using pretrained **RelationExtractionModel** `re_temporal_events_clinical`.

# COMMAND ----------

pos_tagger = PerceptronModel.pretrained("pos_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token"])\
    .setOutputCol("pos_tags")

events_ner_tagger = MedicalNerModel()\
    .pretrained("ner_events_clinical", "en", "clinical/models")\
    .setInputCols("sentence", "token", "embeddings")\
    .setOutputCol("ner_tags")\
    .setIncludeConfidence(False)

ner_chunker = NerConverterInternal()\
    .setInputCols(["sentence", "token", "ner_tags"])\
    .setOutputCol("ner_chunks")

dependency_parser = DependencyParserModel.pretrained("dependency_conllu", "en")\
    .setInputCols(["sentence", "pos_tags", "token"])\
    .setOutputCol("dependencies")

clinical_re_Model = RelationExtractionModel()\
    .pretrained("re_temporal_events_clinical", "en", 'clinical/models')\
    .setInputCols(["embeddings", "pos_tags", "ner_chunks", "dependencies"])\
    .setOutputCol("relations")\
    .setMaxSyntacticDistance(4)\
    .setPredictionThreshold(0.9)

pipeline = Pipeline(stages=[
  documentAssembler,
  sentenceDetector,
  tokenizer, 
  word_embeddings, 
  pos_tagger, 
  events_ner_tagger,
  ner_chunker,
  dependency_parser,
  clinical_re_Model
])

empty_data = spark.createDataFrame([[""]]).toDF("text")
model = pipeline.fit(empty_data)

# COMMAND ----------

temporal_re_df = model.transform(df)

# COMMAND ----------

# MAGIC %md
# MAGIC Now we write the results in our delta silver layer

# COMMAND ----------

temporal_re_df_silver = temporal_re_df.select("path", F.explode(F.arrays_zip('relations.result', 'relations.metadata')).alias("cols"))\
                                  .select("path",
                                          F.expr("cols['result']").alias("relation"),
                                          F.expr("cols['metadata']['entity1']").alias('entity1'),
                                          F.expr("cols['metadata']['chunk1']").alias('chunk1'),
                                          F.expr("cols['metadata']['entity2']").alias('entity2'),
                                          F.expr("cols['metadata']['chunk2']").alias('chunk2'),
                                          F.expr("cols['metadata']['confidence']").alias('confidence')
                                         )

# COMMAND ----------

# MAGIC %md
# MAGIC #### Write `temporal_re_df_silver` Delta

# COMMAND ----------

temporal_re_df_silver.write.format('delta').mode("overwrite").save(f"{delta_path}/silver/temporal-re")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Relations Between Body Parts and Procedures
# MAGIC 
# MAGIC We will create a relation extration model to identify relationships between body parts and problem entities by using pretrained **RelationExtractionModel** `re_bodypart_problem`.

# COMMAND ----------

pos_tagger = PerceptronModel.pretrained("pos_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token"])\
    .setOutputCol("pos_tags")

ner_tagger = MedicalNerModel() \
    .pretrained("jsl_ner_wip_greedy_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("ner_tags")\
    .setIncludeConfidence(False)

ner_converter = NerConverter() \
    .setInputCols(["sentence", "token", "ner_tags"]) \
    .setOutputCol("ner_chunks_re")\
    .setWhiteList(['Internal_organ_or_component', 'Problem', 'Procedure'])

dependency_parser = DependencyParserModel() \
    .pretrained("dependency_conllu", "en") \
    .setInputCols(["sentence", "pos_tags", "token"]) \
    .setOutputCol("dependencies")

re_model = RelationExtractionModel()\
    .pretrained('re_bodypart_problem', 'en', "clinical/models") \
    .setPredictionThreshold(0.5)\
    .setInputCols(["embeddings", "pos_tags", "ner_chunks_re", "dependencies"]) \
    .setOutputCol("relations")

bodypart_re_pipeline = Pipeline(stages=[documentAssembler, 
                            sentenceDetector, 
                            tokenizer, 
                            pos_tagger, 
                            word_embeddings, 
                            ner_tagger, 
                            ner_converter,
                            dependency_parser, 
                            re_model])


empty_data = spark.createDataFrame([['']]).toDF("text")
bodypart_re_model = bodypart_re_pipeline.fit(empty_data)

# COMMAND ----------

bodypart_re_df = bodypart_re_model.transform(df)

# COMMAND ----------

bodypart_re_df = bodypart_re_df.select("path", F.explode(F.arrays_zip('relations.result', 'relations.metadata')).alias("cols"))\
                                .select("path",
                                        F.expr("cols['result']").alias("relation"),
                                        F.expr("cols['metadata']['entity1']").alias('entity1'),
                                        F.expr("cols['metadata']['chunk1']").alias('chunk1'),
                                        F.expr("cols['metadata']['entity2']").alias('entity2'),
                                        F.expr("cols['metadata']['chunk2']").alias('chunk2'),
                                        F.expr("cols['metadata']['confidence']").alias('confidence')
                                        )

# COMMAND ----------

# MAGIC %md
# MAGIC #### Write `bodypart_re_df` to Delta

# COMMAND ----------

bodypart_re_df.write.format('delta').mode("overwrite").save(f'{delta_path}/silver/bodypart-relationships')

# COMMAND ----------

display(bodypart_re_df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Get Procedure codes from notes
# MAGIC 
# MAGIC We will create a new pipeline to get procedure codes. As NER model, we are using `jsl_ner_wip_greedy_clinical` and setting NerConverter's WhiteList `['Procedure']` in order to get only drug entities.

# COMMAND ----------

proc_ner = MedicalNerModel.pretrained("jsl_ner_wip_greedy_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("ner_proc")\
    .setIncludeConfidence(False)

proc_ner_converter = NerConverter() \
    .setInputCols(["sentence", "token", "ner_proc"]) \
    .setOutputCol("ner_chunk")\
    .setWhiteList(['Procedure'])


bert_pipeline_cpt = Pipeline(
    stages = [
        documentAssembler,
        sentenceDetector,
        tokenizer,
        word_embeddings,
        proc_ner,
        proc_ner_converter])

empty_data = spark.createDataFrame([['']]).toDF("text")
cpt_model = bert_pipeline_cpt.fit(empty_data)

# COMMAND ----------

cpt_code_res = cpt_model.transform(df) 

# COMMAND ----------

# MAGIC %md
# MAGIC Now we will take the ner_chunks into a list to use in resolver pipeline

# COMMAND ----------

cpt_ner_df = cpt_code_res.select("path", F.explode(F.arrays_zip('ner_chunk.result', 
                                                                'ner_chunk.metadata')).alias("cols"))\
                         .select("path", F.expr("cols['result']").alias("ner_chunk"), 
                                         F.expr("cols['metadata']['entity']").alias("entity")).toPandas()

cpt_ner_chunks = list(cpt_ner_df.ner_chunk)

# COMMAND ----------

sbert_embedder = BertSentenceEmbeddings.pretrained("sbiobert_base_cased_mli", 'en', 'clinical/models')\
  .setInputCols(["ner_chunks"])\
  .setOutputCol("sentence_embeddings")

cpt_resolver = SentenceEntityResolverModel.pretrained("sbiobertresolve_cpt_augmented","en", "clinical/models")\
  .setInputCols(["ner_chunks", "sentence_embeddings"]) \
  .setOutputCol("cpt_code")\
  .setDistanceFunction("EUCLIDEAN")

cpt_pipelineModel = PipelineModel(stages=[
            documentAssemblerResolver,
            sbert_embedder,
            cpt_resolver
            ])

# COMMAND ----------

cpt_lp = LightPipeline(cpt_pipelineModel)

# COMMAND ----------

cpt_code_res = cpt_lp.fullAnnotate(cpt_ner_chunks)

# COMMAND ----------

tuples = []

for i in range(len(cpt_code_res)):
    for x,y in zip(cpt_code_res[i]["ner_chunks"], cpt_code_res[i]["cpt_code"]):
        tuples.append((cpt_ner_df.path.iloc[i],x.result, cpt_ner_df.entity.iloc[i], y.result, y.metadata["confidence"], y.metadata["all_k_results"], y.metadata["all_k_resolutions"]))

cpt_df = pd.DataFrame(tuples, columns=["path", "chunks", "entity", "cpt_code", "confidence", "all_codes", "resolutions"])



codes = []
resolutions = []

for code, resolution in zip(cpt_df['all_codes'], cpt_df['resolutions']):
    
    codes.append(code.split(':::'))
    resolutions.append(resolution.split(':::'))
    
  
cpt_df['all_codes'] = codes  
cpt_df['resolutions'] = resolutions
cpt_df['cpt'] = cpt_df['resolutions'].apply(lambda x : x[0])

# COMMAND ----------

cpt_df.head()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Write `cpt_df` to Delta

# COMMAND ----------

cpt_df=spark.createDataFrame(cpt_df)
cpt_df.write.format('delta').mode('overwrite').save(f"{delta_path}/silver/cpt")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Get Assertion Status of Cancer Entities
# MAGIC 
# MAGIC We will create a new pipeline to get assertion status of cancer entities procedure codes. As NER model, we are using `jsl_ner_wip_greedy_clinical`.

# COMMAND ----------

# Cancer
bionlp_ner = MedicalNerModel.pretrained("ner_bionlp", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("bionlp_ner")\
    .setIncludeConfidence(False)

bionlp_ner_converter = NerConverter() \
    .setInputCols(["sentence", "token", "bionlp_ner"]) \
    .setOutputCol("bionlp_ner_chunk")\
    .setWhiteList(["Cancer"])

# Clinical Terminology
jsl_ner = MedicalNerModel.pretrained("jsl_ner_wip_greedy_clinical", "en", "clinical/models") \
    .setInputCols(["sentence", "token", "embeddings"]) \
    .setOutputCol("jsl_ner")\
    .setIncludeConfidence(False)

jsl_ner_converter = NerConverter() \
    .setInputCols(["sentence", "token", "jsl_ner"]) \
    .setOutputCol("jsl_ner_chunk")\
    .setWhiteList(["Oncological", "Symptom"])

chunk_merger = ChunkMergeApproach()\
    .setInputCols('bionlp_ner_chunk', "jsl_ner_chunk")\
    .setOutputCol('final_ner_chunk')

cancer_assertion = AssertionDLModel.pretrained("assertion_dl", "en", "clinical/models") \
    .setInputCols(["sentence", "final_ner_chunk", "embeddings"]) \
    .setOutputCol("assertion")


assertion_pipeline = Pipeline(
    stages = base_stages+[
        bionlp_ner,
        bionlp_ner_converter,
        jsl_ner,
        jsl_ner_converter,
        chunk_merger,
        cancer_assertion
    ])
empty_data = spark.createDataFrame([['']]).toDF("text")
assertion_model = assertion_pipeline.fit(empty_data)

# COMMAND ----------

assertion_res = assertion_model.transform(df)

# COMMAND ----------

assertion_df = (assertion_res.selectExpr('*', 'final_ner_chunk.result as final_ner_chunk_result', 'final_ner_chunk.metadata as final_ner_chunk_metadata', 'assertion.result as assertion_result')
                .select("path", F.explode(F.arrays_zip('final_ner_chunk_result', 'final_ner_chunk_metadata', 'assertion_result')).alias("cols"))
                .select("path", F.expr("cols['final_ner_chunk_result']").alias("chunk"),
                                F.expr("cols['final_ner_chunk_metadata']['entity']").alias("entity"),
                                F.expr("cols['assertion_result']").alias("assertion"))
               )

# COMMAND ----------

assertion_df.head(10)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Write `assertion_df` to Delta

# COMMAND ----------

assertion_df.write.format('delta').mode('overwrite').save(f'{delta_path}/silver/assertion')

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
# MAGIC |Spark NLP |Apache-2.0 License| https://github.com/JohnSnowLabs/spark-nlp/blob/master/LICENSE | https://github.com/JohnSnowLabs/spark-nlp|
# MAGIC |MatPlotLib | | https://github.com/matplotlib/matplotlib/blob/master/LICENSE/LICENSE | https://github.com/matplotlib/matplotlib|
# MAGIC |Seaborn | | https://github.com/seaborn/seaborn/blob/master/licences/HUSL_LICENSE | https://github.com/seaborn/seaborn/|
# MAGIC |Pillow (PIL) | HPND License| https://github.com/python-pillow/Pillow/blob/master/LICENSE | https://github.com/python-pillow/Pillow/|
# MAGIC |Spark NLP for Healthcare|[Proprietary license - John Snow Labs Inc.](https://www.johnsnowlabs.com/spark-nlp-health/) |NA|NA|
# MAGIC |Spark OCR |[Proprietary license - John Snow Labs Inc.](https://nlp.johnsnowlabs.com/docs/en/ocr) |NA|NA|
# MAGIC 
# MAGIC |Author|
# MAGIC |-|
# MAGIC |Databricks Inc.|
# MAGIC |John Snow Labs Inc.|

# COMMAND ----------

# MAGIC %md
# MAGIC ## Disclaimers
# MAGIC Databricks Inc. (“Databricks”) does not dispense medical, diagnosis, or treatment advice. This Solution Accelerator (“tool”) is for informational purposes only and may not be used as a substitute for professional medical advice, treatment, or diagnosis. This tool may not be used within Databricks to process Protected Health Information (“PHI”) as defined in the Health Insurance Portability and Accountability Act of 1996, unless you have executed with Databricks a contract that allows for processing PHI, an accompanying Business Associate Agreement (BAA), and are running this notebook within a HIPAA Account.  Please note that if you run this notebook within Azure Databricks, your contract with Microsoft applies.