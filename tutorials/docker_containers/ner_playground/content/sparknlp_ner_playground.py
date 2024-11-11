import streamlit as st
st.set_page_config(
    layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    page_title='Spark NLP Clinical NER Playground',  # String or None. Strings get appended with "• Streamlit". 
    page_icon='./resources/favicon.png',  # String, anything supported by st.image, or None.
)
import os
USE_BERT = os.getenv("USE_BERT", 0)
if USE_BERT == '0' or USE_BERT == 'false' or USE_BERT == 'False' or USE_BERT == False:
    USE_BERT = False
elif USE_BERT == 1 or USE_BERT == '1' or USE_BERT == 'true' or USE_BERT == 'True' or USE_BERT == True:
    USE_BERT = True
print ('USE_BERT >>>', USE_BERT)
import pandas as pd
import base64
import wget

from sparknlp_display import NerVisualizer

st.sidebar.image('./resources/jsl-logo.png', use_column_width=True)

from resources.style_config import STYLE_CONFIG

st.markdown(STYLE_CONFIG, unsafe_allow_html=True)


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

print ("Spark NLP Version :", sparknlp.version())
print ("Spark NLP_JSL Version :", sparknlp_jsl.version())

import json
with open('/content/sparknlp_keys.json', 'r') as f:
    license_keys = json.load(f)
# with open('/home/ubuntu/hasham/jsl_keys.json', 'r') as f:
#     license_keys = json.load(f)


secret = license_keys['SECRET']
os.environ['SPARK_NLP_LICENSE'] = license_keys['SPARK_NLP_LICENSE']
os.environ['AWS_ACCESS_KEY_ID'] = license_keys['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY'] = license_keys['AWS_SECRET_ACCESS_KEY']

spark = sparknlp_jsl.start(license_keys['SECRET'])

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

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
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
    wget.download("https://nlp.johnsnowlabs.com/models.json", "/")
    import json
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


ner_models_clinical, ner_models_biobert = get_models_list()

if USE_BERT:
    st.sidebar.text('Running with BioBert Embeddings')
    model_dict = load_sparknlp_models_biobert()
else:
    st.sidebar.text('Running with GLoVe Embeddings')
    model_dict = load_sparknlp_models()

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



def build_dynamic_pipeline(payload):
    
    document = DocumentAssembler()\
        .setInputCol("text")\
        .setOutputCol("document")

    sentence = model_dict['sentenceDetector']

    token = Tokenizer()\
        .setInputCols(['sentence'])\
        .setOutputCol('token')
        
    embeddings = model_dict['embeddings']

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
st.sidebar.write('Chunks will be merged if multiple models selected')

def get_labels(model):
    
    m = set(list([c.split('-')[-1] for c in model.getClasses() if len(c)>1]))
    
    return list(m)

def get_payload():
    
    ner_list = sorted(list(model_dict.keys()))
    
    ner_payload = dict()
    
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

print ('App ready!')

ner_list = [i for i in model_dict.keys() if 'ner' in i.lower()]

sorted(ner_list)

run_all_ners = st.sidebar.checkbox('Run all NERs')
st.sidebar.markdown("<hr>", unsafe_allow_html=True)

if run_all_ners:
    
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


ner_text = st.text_area('NER Input Text', 'A 28-year-old female with a history of gestational diabetes mellitus diagnosed eight years prior to presentation and subsequent type two diabetes mellitus ( T2DM ), one prior episode of HTG-induced pancreatitis three years prior to presentation , associated with an acute hepatitis , and obesity with a body mass index ( BMI ) of 33.5 kg/m2 , presented with a one-week history of polyuria , polydipsia , poor appetite , and vomiting. The patient was prescribed 1 capsule of Advil 10 mg for 5 days and magnesium hydroxide 100mg/1ml suspension PO. He was seen by the endocrinology service and she was discharged on 40 units of insulin glargine at night , 12 units of insulin lispro with meals , and metformin 1000 mg two times a day .', height=250)

import time

start_time = time.time()

if len(ner_payload)!=0:
    
    ner_pipeline, chunk_col = build_dynamic_pipeline (ner_payload)
    
    entities_df = get_entities (ner_pipeline, ner_text)
    
    get_table_download_link(entities_df )

    display_time(start_time)
    
    
# how to run
# streamlit run sparknlp_ner_playground.py
