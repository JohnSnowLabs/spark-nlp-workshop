import streamlit as st
st.set_page_config(
    layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
    initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
    page_title='Detect tumor characteristics',  # String or None. Strings get appended with "• Streamlit".
    page_icon='../../resources/favicon.png',  # String, anything supported by st.image, or None.
)
import pandas as pd
import numpy as np
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
import sys
sys.path.append(os.path.abspath('./NER_COLAB'))
#sys.path.append(os.path.abspath('../../'))
import streamlit_apps_config as config
from streamlit_ner_output import show_html2, jsl_display_annotations, get_color

## Marking down NER Style
st.markdown(config.STYLE_CONFIG, unsafe_allow_html=True)

root_path = config.project_path


########## To Remove the Main Menu Hamburger ########

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

########## Side Bar ########

## loading logo(newer version with href)
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

logo_html = get_img_with_href('./NER_COLAB/resources/jsl-logo.png', 'https://www.johnsnowlabs.com/')
st.sidebar.markdown(logo_html, unsafe_allow_html=True)


## loading logo (older version without href)
# st.sidebar.image('../../resources/jsl-logo.png', use_column_width=True)

### loading description file
descriptions = pd.read_json('./NER_COLAB/streamlit_apps_descriptions.json')

## Getting NER model list
descriptions = descriptions[descriptions['app'] == 'NER_TUMOR']
model_names = descriptions['model_name'].values

## Displaying Availabe models
st.sidebar.title("Choose the pretrained model to test")
test_data = pd.read_json('./test.json')

selected_model = st.sidebar.selectbox("", test_data.columns[1:])


######## Main Page #########

#### displaying selected model's output
#app_title = descriptions[descriptions['model_name'] == selected_model]['title'].iloc[0]
#app_description = descriptions[descriptions['model_name'] == selected_model]['description'].iloc[0]
#st.title('Spark NLP NER')
#st.title(app_title)
#st.markdown("<h2>"+app_description+"</h2>", unsafe_allow_html=True)
#st.subheader("")
#### Loading Files

#TEXT_FILE_PATH = os.path.join(os.getcwd(),'inputs/'+selected_model)
#RESULT_FILE_PATH = os.path.join(os.getcwd(),'outputs/'+selected_model)

#input_files = sorted(os.listdir(TEXT_FILE_PATH))
#input_files_paths = [os.path.join(TEXT_FILE_PATH, fname) for fname in input_files]
#result_files_paths = [os.path.join(RESULT_FILE_PATH, fname.split('.')[0]+'.json') for fname in input_files]

#title_text_mapping_dict={}
#title_json_mapping_dict={}
#for index, file_path in enumerate(input_files_paths):
#  lines = open(file_path, 'r', encoding='utf-8').readlines()
#  title = lines[0]
#  text = ''.join(lines[1:])
#  title_text_mapping_dict[title] = text
#  title_json_mapping_dict[title] = result_files_paths[index]



#### Displaying Available examples


import SessionState

ss = SessionState.get(x=1)

selected_title = list(zip(test_data.index ,test_data.Insight))[ss.x]

c1, c2 = st.columns(2)

with c1:
  if st.button("Previous Insight"):
      ss.x = ss.x - 1
      selected_title = list(zip(test_data.index ,test_data.Insight))[ss.x]

with c2:
  if st.button("Next Insight"):
      ss.x = ss.x + 1
      selected_title = list(zip(test_data.index ,test_data.Insight))[ss.x]

#if st.button("Next Insight"):
#    ss.x = ss.x + 1
#    selected_title = list(zip(test_data.index ,test_data.Insight))[ss.x]

#if st.button("Previous Insight"):
#    ss.x = ss.x - 1
#    selected_title = list(zip(test_data.index ,test_data.Insight))[ss.x]

widget = st.empty()
ss.x = widget.slider('Position', 0, max(test_data.index), ss.x)

#slider = st.slider("Select Insight", 0, max(test_data.index))

#title = st.selectbox("Choose Sample Text", zip(test_data.index ,test_data.Insight))#input_files_list)
#selected = st.button('Go to selected text')

#if selected:
#    selected_title = title
#    df = pd.DataFrame({"ner_chunk"  : test_data[selected_model][selected_title[0]]})

## selected example

labels_set = set()

df = pd.DataFrame({"ner_chunk"  : test_data[selected_model][selected_title[0]]})

for i in test_data[selected_model][selected_title[0]]:
    i[4]['entity'] = i[4]['entity'].strip().upper()
    labels_set.add(i[4]['entity'])

labels_set = list(labels_set)

labels = st.sidebar.multiselect(
        "Entity labels", options=labels_set, default=list(labels_set)
    )

### Show Entities
#selected_text = title_text_mapping_dict[selected_title]
show_html2(test_data.Insight[ss.x], df, labels, "Text annotated with identified Named Entities")
