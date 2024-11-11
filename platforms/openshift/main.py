from typing import Optional
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import time
import json
import os
import wget
import pandas as pd
from pyspark.ml import Pipeline,PipelineModel
from pyspark.sql import SparkSession
from sparknlp.annotator import *
from sparknlp_jsl.annotator import *
from sparknlp.base import *
import sparknlp_jsl
import sparknlp
from datetime import datetime, timezone
import warnings 
warnings.filterwarnings("ignore")

app = FastAPI()

ner_models_clinical = []
ner_models_biobert = []
event_list = dict()

## helper functions
def load_sparknlp_models():

    print ('loading pretrained models')

    sentenceDetector = SentenceDetectorDLModel.pretrained("sentence_detector_dl_healthcare","en","clinical/models")\
        .setInputCols(["document"])\
        .setOutputCol("sentence")

    embeddings_clinical = WordEmbeddingsModel.pretrained("embeddings_clinical","en","clinical/models")\
        .setInputCols(["sentence","token"])\
        .setOutputCol("embeddings")
    
    model_dict = {
        'sentenceDetector': sentenceDetector,
        'embeddings':embeddings_clinical
            }
    
    for ner_model in ner_models_clinical:

        try:
            t_model = MedicalNerModel.pretrained(ner_model,"en","clinical/models")\
                                .setInputCols(["sentence","token","embeddings"])\
                                .setOutputCol("ner")
            if t_model.getStorageRef().strip() == 'clinical':
                model_dict[ner_model] = t_model
        except:
            pass
            #st.write ('model name is wrong > ', ner_model)
        
    print ('glove models loaded !')

    return model_dict

def load_sparknlp_models_biobert():

    print ('loading pretrained models')

    sentenceDetector = SentenceDetectorDLModel.pretrained("sentence_detector_dl_healthcare","en","clinical/models")\
        .setInputCols(["document"])\
        .setOutputCol("sentence")

    embeddings_biobert = BertEmbeddings.pretrained("biobert_pubmed_base_cased").setInputCols(["sentence", "token"]).setOutputCol("embeddings")

    model_dict = {
        'sentenceDetector': sentenceDetector,
        'embeddings':embeddings_biobert
    }
    
    for ner_model in ner_models_biobert :

        try:
            t_model = MedicalNerModel.pretrained(ner_model,"en","clinical/models")\
                            .setInputCols(["sentence","token","embeddings"])\
                            .setOutputCol("ner")
            if t_model.getStorageRef().strip() == 'biobert_pubmed_base_cased':
                model_dict[ner_model] = t_model
        except:
            pass
            #st.write ('model name is wrong > ', ner_model)

    print ('biobert models loaded !')

    return model_dict

def get_models_list():
    
    wget.download("https://nlp.johnsnowlabs.com/models.json", '/')
    
    with open('/models.json', 'r') as f_:
        jsn = json.load(f_)
    
    valid_models = set()
    for mdl in jsn:
        if (mdl['task'] == 'Named Entity Recognition') and ('Healthcare' in mdl['edition']) and (mdl['name'].startswith('ner_')) and (mdl['language'] == 'en') and (not mdl['name'].endswith('_en')) and (not mdl['name'].endswith('_healthcare')) and mdl['edition'].split()[-1]>='3.0' and (not mdl['name'].endswith('bert')) and (not mdl['name'].endswith('glove')):
            valid_models.add(mdl['name'])
    valid_models.update(['jsl_rd_ner_wip_greedy_clinical'])
    
    valid_models_bert = set()
    for mdl in jsn:
        if (mdl['task'] == 'Named Entity Recognition') and ('Healthcare' in mdl['edition']) and (mdl['name'].startswith('ner_')) and (mdl['language'] == 'en') and (mdl['name'].endswith('biobert')) and mdl['edition'].split()[-1]>= '3.0':
            valid_models_bert.add(mdl['name'])
    valid_models_bert.update(['jsl_rd_ner_wip_greedy_biobert'])
    
    return list(valid_models), list(valid_models_bert) 

def get_ner_results(modelname ='ner_clinical', USE_BERT=0, text='I love Spark NLP'):
    
    # Annotator that transforms a text column from dataframe into an Annotation ready for NLP
    documentAssembler = DocumentAssembler()\
            .setInputCol("text")\
            .setOutputCol("document")
            
    sentenceDetector = SentenceDetectorDLModel.pretrained("sentence_detector_dl_healthcare","en","clinical/models")\
            .setInputCols(["document"])\
            .setOutputCol("sentence")
     
    # Tokenizer splits words in a relevant format for NLP
    tokenizer = Tokenizer()\
            .setInputCols(["sentence"])\
            .setOutputCol("token")
    
    if USE_BERT == 1:
        embeddings = BertEmbeddings.pretrained("biobert_pubmed_base_cased").setInputCols(["sentence","token"]).setOutputCol("embeddings")
    
    else:
        # Clinical word embeddings trained on PubMED dataset
        embeddings = WordEmbeddingsModel.pretrained("embeddings_clinical","en","clinical/models")\
                .setInputCols(["sentence","token"])\
                .setOutputCol("embeddings")
    
    # NER model trained on i2b2 (sampled from MIMIC) dataset
    ner = MedicalNerModel.pretrained(modelname, "en","clinical/models")\
            .setInputCols(["sentence","token","embeddings"])\
            .setOutputCol("ner")
    
    ner_converter = NerConverter()\
        .setInputCols(["sentence","token","ner"])\
        .setOutputCol("ner_chunk")

    nlpPipeline = Pipeline(stages=[
            documentAssembler,
            sentenceDetector,
            tokenizer,
            embeddings,
            ner,
            ner_converter])
    
    empty_data = spark.createDataFrame([[""]]).toDF("text")
    
    ner_model = nlpPipeline.fit(empty_data)
    
    light_model = LightPipeline(ner_model)
    
    full_annotated_text = light_model.fullAnnotate(text)[0]
    
    chunks=[]
    entities=[]
    
    for n in full_annotated_text["ner_chunk"]:
        chunks.append(n.result)
        entities.append(n.metadata['entity']) 
        
    df = pd.DataFrame({'chunks':chunks, 'entities':entities})
    
    return df.to_dict()

def test_sparkNLP():
    from sparknlp.pretrained import PretrainedPipeline

    ner_pipeline = PretrainedPipeline("ner_model_finder", "en", "clinical/models")

    result = ner_pipeline.annotate("medication")

    print(100*'-')
    print(result)
    print(100*'-')

@app.on_event("startup")
async def startup_event():
    
    event_list['0_start_up']=datetime.now()
    print(f'startup has been started at {datetime.now()}...', )
    
    with open('license.json', 'r') as f:
        license_keys = json.load(f)
    
    # Defining license key-value pairs as local variables
    locals().update(license_keys)
    
    # Adding license key-value pairs to environment variables
    os.environ.update(license_keys)
    
    print ("Spark NLP Version :", sparknlp.version())
    print ("Spark NLP_JSL Version :", sparknlp_jsl.version())
    
    global spark
    
    spark = sparknlp_jsl.start(license_keys['SECRET'])
    print(f'****** spark nlp healthcare version fired up {datetime.now()} ******')
    event_list['1_sparknlp_fired']=datetime.now()
    

    ner_models_clinical, ner_models_biobert = get_models_list()
    print(f'***** NER clinical and biobert models are listed {datetime.now()} .....')
    event_list['2_models_listed']=datetime.now()
    
    # load NER clinical and biobert models
    print(f'***** Running with GLoVe Embeddings  {datetime.now()} *****')
    model_dict = load_sparknlp_models()
    event_list['3_glove_embeddings']=datetime.now()
    
    print(f'***** Running with BioBert Embeddings {datetime.now()} *****')
    model_dict = load_sparknlp_models_biobert()
    event_list['4_biobert_embeddings']=datetime.now()
    
    print(event_list)
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/spark")
def read_spark():
    session = dict()
    session["Spark NLP Version"] = sparknlp.version()
    session["Spark NLP_JSL Version"] = sparknlp_jsl.version()
    session["App Name"] = spark.sparkContext.getConf().getAll()[6][1]
    print(session)
    
    return session

@app.get("/time")
def get_time():
    return event_list

@app.get("/test")
def test_API():
    from sparknlp.pretrained import PretrainedPipeline

    ner_pipeline = PretrainedPipeline("ner_model_finder", "en", "clinical/models")

    result = ner_pipeline.annotate("medication")
    print(result)
    return result

@app.get("/ner")
def get_ner(modelName: str, BERT_USE: Optional[int] = 0, text: Optional[str] = 'I love SparkNLP'):
    return get_ner_results(modelName, BERT_USE, text)
    
@app.on_event("shutdown")
async def shutdown_event():
    print('Shutdown')
    spark.stop()
    
    
if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=8515)
