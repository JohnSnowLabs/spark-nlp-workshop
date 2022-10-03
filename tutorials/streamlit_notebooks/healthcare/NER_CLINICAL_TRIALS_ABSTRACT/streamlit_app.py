import streamlit as st 
st.set_page_config(
    layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    page_title='Clinical Trial Abstracts Entities',  # String or None. Strings get appended with "• Streamlit". 
    page_icon='../../resources/favicon.png',  # String, anything supported by st.image, or None.
)
import pandas as pd
import numpy as np
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
import sys
sys.path.append(os.path.abspath('../'))
sys.path.append(os.path.abspath('../../'))
import streamlit_apps_config as config
from streamlit_ner_output import show_html2, jsl_display_annotations, get_color

## Marking down NER Style
st.markdown(config.STYLE_CONFIG, unsafe_allow_html=True)

root_path = config.project_path


########## To Remove the Main Menu Hamburger ########

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

########## Side Bar ########

##-- Hrishabh Digaari: FOR SOLVING THE ISSUE OF INTERMITTENT IMAGES & LOGO-----------------------------------------------------
import base64
@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache(allow_output_mutation=True)
def get_img_with_href(local_img_path, target_url):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''
        <a href="{target_url}">
            <img height="90%" width="90%" src="data:image/{img_format};base64,{bin_str}" />
        </a>'''
    return html_code

logo_html = get_img_with_href('../../resources/jsl-logo.png', 'https://www.johnsnowlabs.com/')
st.sidebar.markdown(logo_html, unsafe_allow_html=True)


## loading logo (older version without href)
# st.sidebar.image('../../resources/jsl-logo.png', use_column_width=True)

### loading description file
descriptions = pd.read_json('../../streamlit_apps_descriptions.json')

## Getting NER model list
descriptions = descriptions[descriptions['app'] == 'NER_CLINICAL_TRIALS_ABSTRACT']
model_names = descriptions['model_name'].values

## Displaying Availabe models
st.sidebar.title("Choose the pretrained model to test")
selected_model = st.sidebar.selectbox("", list(model_names))



######## Main Page #########

#### displaying selected model's output
app_title = descriptions[descriptions['model_name'] == selected_model]['title'].iloc[0]
app_description = descriptions[descriptions['model_name'] == selected_model]['description'].iloc[0]
#st.title('Spark NLP NER')
st.title(app_title)
st.markdown("<h2>"+app_description+"</h2>", unsafe_allow_html=True)
st.subheader("")
#### Loading Files 

TEXT_FILE_PATH = os.path.join(os.getcwd(),'inputs/'+selected_model)
RESULT_FILE_PATH = os.path.join(os.getcwd(),'outputs/'+selected_model)

input_files = sorted(os.listdir(TEXT_FILE_PATH))
input_files_paths = [os.path.join(TEXT_FILE_PATH, fname) for fname in input_files]
result_files_paths = [os.path.join(RESULT_FILE_PATH, fname.split('.')[0]+'.json') for fname in input_files]

title_text_mapping_dict={}
title_json_mapping_dict={}
for index, file_path in enumerate(input_files_paths):
  lines = open(file_path, 'r', encoding='utf-8').readlines()
  title = lines[0]
  text = ''.join(lines[1:])
  title_text_mapping_dict[title] = text
  title_json_mapping_dict[title] = result_files_paths[index]



#### Displaying Available examples
selected_title = st.selectbox("Choose Sample Text", list(title_json_mapping_dict.keys()))#input_files_list)
## selected example
selected_file = title_json_mapping_dict[selected_title]

#### reading result file
df = pd.read_json(selected_file)

labels_set = set()
for i in df['ner_chunk'].values:
  i[4]['entity'] = i[4]['entity'].strip().upper()
  labels_set.add(i[4]['entity'])
labels_set = list(labels_set)

labels = st.sidebar.multiselect(
        "Entity labels", options=labels_set, default=list(labels_set)
    )

### Show Entities
selected_text = title_text_mapping_dict[selected_title]
show_html2(selected_text, df, labels, "Text annotated with identified Named Entities")

# st.sidebar.markdown("Spark NLP version: {}".format(sparknlp.version()))

try_link="""<a href="https://colab.research.google.com/github/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/streamlit_notebooks/healthcare/NER_CLINICAL_TRIALS_ABSTRACT.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" style="zoom: 1.3" alt="Open In Colab"/></a>"""
st.sidebar.title("")
st.sidebar.markdown("Try it yourself:")
st.sidebar.markdown(try_link, unsafe_allow_html=True)