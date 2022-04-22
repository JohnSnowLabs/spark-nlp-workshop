import nlu
text= """You can visualize any of the 100 + Sentence Embeddings
with 10+ dimension reduction algorithms
and view the results in 3D, 2D, and 1D  
which can be colored by various classifier labels!
"""
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('embed_sentence.bert').viz_streamlit_sentence_embed_manifold(text)

