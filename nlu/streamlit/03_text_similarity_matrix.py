import nlu
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('ner').viz_streamlit_word_similarity(['I love love love  NLU !', 'I also love love love LOVE Streamlit'])
