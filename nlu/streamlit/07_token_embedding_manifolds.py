import nlu
texts = ['You can visualize any of the 100 + embeddings','with 10+ dimension reduction algorithms','and view the results in 3D, 2D, and 1D  which can be colored by various classifier labels!',]
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('bert').viz_streamlit_word_embed_manifold(default_texts=texts,default_algos_to_apply=['TSNE'],)

