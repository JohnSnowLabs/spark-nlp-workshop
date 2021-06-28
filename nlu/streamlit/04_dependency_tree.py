import nlu
nlu.enable_streamlit_caching() # Optional caching the models, recommended
nlu.load('dep.typed').viz_streamlit_dep_tree('POS tags define a grammatical label for each token and the Dependency Tree classifies Relations between the tokens')
