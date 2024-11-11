
import streamlit as st
import pandas as pd
import base64

from sparknlp_display import NerVisualizer

st.sidebar.image('https://nlp.johnsnowlabs.com/assets/images/logo.png', use_column_width=True)

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""

st.title("Spark NLP Clinical NER Playground")

import json
import os
from pyspark.ml import Pipeline,PipelineModel
from pyspark.sql import SparkSession

from sparknlp.annotator import *
from sparknlp_jsl.annotator import *
from sparknlp.base import *
import sparknlp_jsl
import sparknlp


import json

spark = sparknlp_jsl.start(os.environ['SECRET'])

print ("Spark NLP Version :", sparknlp.version())
print ("Spark NLP_JSL Version :", sparknlp_jsl.version())


@st.cache(allow_output_mutation=True, suppress_st_warning=True)
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
        'embeddings_clinical':embeddings_clinical
            }
    
    for ner_model in ner_models_clinical:

      try:
        model_dict[ner_model] = MedicalNerModel.pretrained(ner_model,"en","clinical/models")\
                            .setInputCols(["sentence","token","embeddings"])\
                            .setOutputCol("ner")
      except:
        pass
        #st.write ('model name is wrong > ', ner_model)

    print ('models loaded !')

    return model_dict

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_sparknlp_models_biobert():

    print ('loading pretrained models')

    sentenceDetector = SentenceDetectorDLModel.pretrained("sentence_detector_dl_healthcare","en","clinical/models")\
        .setInputCols(["document"])\
        .setOutputCol("sentence")

    embeddings_biobert = BertEmbeddings.pretrained("biobert_pubmed_base_cased").setInputCols(["sentence", "token"]).setOutputCol("embeddings")

    model_dict = {
        'sentenceDetector': sentenceDetector,
        'embeddings_biobert':embeddings_biobert
    }
    
    for ner_model in ner_models_biobert :

      try:
        model_dict[ner_model] = MedicalNerModel.pretrained(ner_model,"en","clinical/models")\
                            .setInputCols(["sentence","token","embeddings"])\
                            .setOutputCol("ner")
      except:
        pass
        #st.write ('model name is wrong > ', ner_model)

    print ('models loaded !')

    return model_dict

import subprocess

subprocess.run(["wget", "https://nlp.johnsnowlabs.com/models.json"])

with open('/content/models.json') as f:
  model_master_list = json.load(f)

ner_models_biobert = list(set([x['name'] for x in model_master_list if x['task']=="Named Entity Recognition" and x['edition'].startswith('Spark NLP for Healthcare') and 'biobert' in x['name'] and x['edition'].split()[-1]>='3.0']))
ner_models_clinical = list(set([x['name'] for x in model_master_list if x['task']=="Named Entity Recognition" and x['edition'].startswith('Spark NLP for Healthcare') and 'biobert' not in x['name'] and 'healthcare' not in x['name'] and x['edition'].split()[-1]>='3.0']))


model_dict_1 = load_sparknlp_models()
model_dict_2 = load_sparknlp_models_biobert()


if not st.sidebar.checkbox('with BioBert Embeddings'):
  emb = 'clinical'
  model_dict = model_dict_1
else:
  model_dict = model_dict_2
  emb = 'biobert'


def display_time(start_tm):
    end_tm = time.time()
    diff = end_tm - start_tm
    st.write('<span style="color:red">{} sec</span>'.format(round(diff,4)), unsafe_allow_html=True)


def viz (annotated_text, chunk_col):

  raw_html = NerVisualizer().display(annotated_text, chunk_col, return_html=True)
  sti = raw_html.find('<style>')
  ste = raw_html.find('</style>')+8
  st.markdown(raw_html[sti:ste], unsafe_allow_html=True)

  st.write(HTML_WRAPPER.format(raw_html[ste:]), unsafe_allow_html=True)


def get_table_download_link(df):
    
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download table as csv file</a>'
    st.write('')
    st.markdown(href, unsafe_allow_html=True)



def build_dynamic_pipeline(payload, embeddings_name='embeddings_clinical'):
    
    document = DocumentAssembler()\
        .setInputCol("text")\
        .setOutputCol("document")

    sentence = model_dict['sentenceDetector']

    token = Tokenizer()\
        .setInputCols(['sentence'])\
        .setOutputCol('token')
        
    embeddings = model_dict[embeddings_name]

    st.write()

    ner_pipe = []

    for ner, entities in payload.items():
        
        first = len(ner_pipe) == 0
        
        ner_pipe.append(model_dict[ner]\
                .setInputCols(["sentence", "token", "embeddings"]) \
                .setOutputCol("{}_tags".format(ner))
                       )

        ner_pipe.append(NerConverter()\
                  .setInputCols(["sentence", "token", "{}_tags".format(ner)])\
                  .setOutputCol("{}_chunks".format(ner))\
                  .setWhiteList(entities)
                           )
        
        if not first:
            
            ner_pipe.append(ChunkMergeApproach().setInputCols(prev, "{}_chunks".format(ner)).\
                            setOutputCol("{}_chunks".format(ner)))
            
            
        prev = "{}_chunks".format(ner)

    ner_pipeline = Pipeline(
            stages = [
            document,
            sentence,
            token,
            embeddings]+ner_pipe)
    
    return ner_pipeline, prev
    
st.sidebar.header('Select pretrained NER Model(s)')

st.sidebar.write('')

def get_labels(model):
    
    m = set(list([c.split('-')[1] for c in model.getClasses() if len(c)>1]))
    
    return list(m)

def get_payload():
    
    ner_list = [i for i in model_dict.keys() if 'ner' in i]
    
    ner_payload =dict()
    
    for ner in ner_list:
    
        if ner=='clinical_ner':
            
            st.sidebar.checkbox(ner, value=True)
            
        if st.sidebar.checkbox(ner):

            classes = get_labels(model_dict[ner])

            concepts = st.sidebar.multiselect("entities in {}".format(ner), options=classes, default=classes)

            ner_payload[ner] = concepts
            
    return ner_payload

from sparknlp_display import NerVisualizer


def get_entities (ner_pipeline, text):
    
    empty_data = spark.createDataFrame([[""]]).toDF("text")

    ner_model = ner_pipeline.fit(empty_data)

    light_model = LightPipeline(ner_model)

    full_annotated_text = light_model.fullAnnotate(text)[0]

    st.write('')
    st.subheader('Entities')

    chunks=[]
    entities=[]
    
    for n in full_annotated_text[chunk_col]:

        chunks.append(n.result)
        entities.append(n.metadata['entity']) 

    df = pd.DataFrame({'chunks':chunks, 'entities':entities})

    #show_html_spacy(full_annotated_text, chunk_col)

    viz (full_annotated_text, chunk_col)
    
    st.table(df)
    
    return df


ner_list = [i for i in model_dict.keys() if 'ner' in i.lower()]

sorted(ner_list)

if st.sidebar.checkbox('Run all NERs'):
    
    st.sidebar.markdown("---")
    
    ner_payload = dict()

    concepts = []
    
    for ner in ner_list:

        classes = get_labels(model_dict[ner])

        ner_concepts = st.sidebar.multiselect("entities in {}".format(ner), options=classes, default=classes)

        ner_payload[ner] = ner_concepts
        
        concepts.extend(ner_concepts)

else:
    
    ner_payload = dict()

    for ner in ner_list:

        if st.sidebar.checkbox(ner):

            classes = get_labels(model_dict[ner])

            ner_concepts = st.sidebar.multiselect("entities in {}".format(ner), options=classes, default=classes)

            ner_payload[ner] = ner_concepts


ner_text = st.text_area('NER Input Text', 'A 28-year-old female with a history of gestational diabetes mellitus diagnosed eight years prior to presentation and subsequent type two diabetes mellitus ( T2DM ), one prior episode of HTG-induced pancreatitis three years prior to presentation , associated with an acute hepatitis , and obesity with a body mass index ( BMI ) of 33.5 kg/m2 , presented with a one-week history of polyuria , polydipsia , poor appetite , and vomiting. The patient was prescribed 1 capsule of Advil 10 mg for 5 days and magnesium hydroxide 100mg/1ml suspension PO. He was seen by the endocrinology service and she was discharged on 40 units of insulin glargine at night , 12 units of insulin lispro with meals , and metformin 1000 mg two times a day .')

import time

start_time = time.time()

if len(ner_payload)!=0:
        
    st.header("***chunks will be merged if multiple models selected***")
    
    if emb=='clinical':
      ner_pipeline, chunk_col = build_dynamic_pipeline (ner_payload)
    else:
      ner_pipeline, chunk_col = build_dynamic_pipeline (ner_payload, embeddings_name='embeddings_biobert')

    entities_df = get_entities (ner_pipeline, ner_text)
    
    get_table_download_link(entities_df )

    display_time(start_time)
    
    
# how to run
# streamlit run sparknlp_ner_playground.py
