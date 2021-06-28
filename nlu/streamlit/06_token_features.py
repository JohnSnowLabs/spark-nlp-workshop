import nlu
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('spell stem lemma pos').viz_streamlit_token('I liek pentut buttr and jelly !')
