import nlu
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('ner').viz_streamlit(['I love NLU !','I love Streamlit!'])
