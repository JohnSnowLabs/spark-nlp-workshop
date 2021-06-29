import nlu
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('ner').viz_streamlit_ner('Donald Trump from America and Angela Merkel from Germany do not share many views')
