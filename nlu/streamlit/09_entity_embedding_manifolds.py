import nlu
text= """Donald Trump likes to visit New York
Angela Merkel likes to visit Berlin!
Peter loves visiting Paris
"""
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('en.ner.conll',verbose=True).viz_streamlit_entity_embed_manifold(text)

