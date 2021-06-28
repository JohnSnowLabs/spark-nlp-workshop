import nlu
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('sentiment').viz_streamlit_classes('I love NLU and Streamlit!')
