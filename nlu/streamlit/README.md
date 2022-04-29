# NLU & Streamlit visualizations
<img width="65%" align="right" src="https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/gif/start.gif">

This folder contains examples and tutorials on how to visualize the 1000+ state-of-the-art NLP models provided by NLU in *just 1 line of code* in `streamlit`.
It includes simple `1-liners` you can sprinkle into your Streamlit app to for features like **Dependency Trees, Named Entities (NER), text classification results, semantic simmilarity,
embedding visualizations via ELMO, BERT, ALBERT, XLNET and much more** .  Additionally, improvements for T5, various resolvers have been added and models `Farsi`, `Hebrew`, `Korean`, and `Turkish`

This is the ultimate NLP research tool. You can visualize and compare the results of hundreds of context aware deep learning embeddings and compare them with classical vanilla embeddings like Glove
and can see with your own eyes how context is encoded by transformer models like `BERT` or `XLNET`and many more !
Besides that, you can also compare the results of the 200+ NER models John Snow Labs provides and see how peformances changes with varrying ebeddings, like Contextual, Static and Domain Specific Embeddings.

## Install
[For detailed instructions refer to the NLU install documentation here](https://nlu.johnsnowlabs.com/docs/en/install)   
You need `Open JDK 8` installed and the following python packages
```bash
pip install nlu streamlit pyspark==3.0.1 sklearn plotly 
```
Problems? [Connect with us on Slack!](https://join.slack.com/t/spark-nlp/shared_invite/zt-lutct9gm-kuUazcyFKhuGY3_0AMkxqA)

## Impatient and want some action?
Just run this Streamlit app, you can use it to generate python code for each NLU-Streamlit building block
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/01_dashboard.py
```

## Quick Starter cheat sheet - All you need to know in 1 picture for NLU + Streamlit
For NLU models to load, see [the NLU Namespace](https://nlu.johnsnowlabs.com/docs/en/namespace) or the [John Snow Labs Modelshub](https://modelshub.johnsnowlabs.com/models)  or go [straight to the source](https://github.com/JohnSnowLabs/nlu/blob/master/nlu/namespace.py).
![NLU Streamlit Cheatsheet](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/img/NLU_Streamlit_Cheetsheet.png)


## Examples
Just try out any of these.
You can use the first example to generate python-code snippets which you can
recycle as building blocks in your streamlit apps!
### Example:  [`01_dashboard`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/01_dashboard.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/01_dashboard.py
```
### Example:  [`02_NER`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/02_NER.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/02_NER.py
```
### Example:  [`03_text_similarity_matrix`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/03_text_similarity_matrix.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/03_text_similarity_matrix.py
```

### Example:  [`04_dependency_tree`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/04_dependency_tree.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/04_dependency_tree.py
```

### Example:  [`05_classifiers`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/05_classifiers.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/05_classifiers.py
```

### Example:  [`06_token_features`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/06_token_features.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/06_token_features.py
```

### Example:  [`07_token_embedding_dimension_reduction`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/07_token_embedding_manifolds.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/07_token_embedding_manifolds.py
```

### Example:  [`08_token_embedding_dimension_reduction`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/08_sentence_embedding_manifolds.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/08_sentence_embedding_manifolds.py
```

### Example:  [`09_entity_embedding_dimension_reduction`](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/09_entity_embedding_manifolds.py)
```shell
streamlit run https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/examples/streamlit/09_entity_embedding_manifolds.py
```


## How to use NLU?
All you need to know about NLU is that there is the [`nlu.load()`](https://nlu.johnsnowlabs.com/docs/en/load_api) method which returns a `NLUPipeline` object
which has a [`.predict()`](https://nlu.johnsnowlabs.com/docs/en/predict_api) that works on most [common data types in the pydata stack like Pandas dataframes](https://nlu.johnsnowlabs.com/docs/en/predict_api#supported-data-types) .     
Ontop of that, there are various visualization methods a NLUPipeline provides easily integrate in Streamlit as re-usable components. [`viz() method`](https://nlu.johnsnowlabs.com/docs/en/viz_examples)





### Overview of NLU + Streamlit buildingblocks

|Method                                                         |               Description                 |
|---------------------------------------------------------------|-------------------------------------------|
| [`nlu.load('<Model>').predict(data)`](TODO.com)                                     | Load any of the [1000+ models](https://nlp.johnsnowlabs.com/models) by providing the model name any predict on most Pythontic [data strucutres like Pandas, strings, arrays of strings and more](https://nlu.johnsnowlabs.com/docs/en/predict_api#supported-data-types) |
| [`nlu.load('<Model>').viz_streamlit(data)`](TODO.com)                               | Display full NLU exploration dashboard, that showcases every feature avaiable with dropdown selectors for 1000+ models|
| [`nlu.load('<Model>').viz_streamlit_similarity([string1, string2])`](TODO.com)      | Display similarity matrix and scalar similarity for every word embedding loaded and 2 strings. |
| [`nlu.load('<Model>').viz_streamlit_ner(data)`](TODO.com)                           | Visualize predicted NER tags from Named Entity Recognizer model|
| [`nlu.load('<Model>').viz_streamlit_dep_tree(data)`](TODO.com)                      | Visualize Dependency Tree together with Part of Speech labels|
| [`nlu.load('<Model>').viz_streamlit_classes(data)`](TODO.com)                       | Display all extracted class features and confidences for every classifier loaded in pipeline|
| [`nlu.load('<Model>').viz_streamlit_token(data)`](TODO.com)                         | Display all detected token features and informations in Streamlit |
| [`nlu.load('<Model>').viz(data, write_to_streamlit=True)`](TODO.com)                | Display the raw visualization without any UI elements. See [viz docs for more info](https://nlu.johnsnowlabs.com/docs/en/viz_examples). By default all aplicable nlu model references will be shown. |
| [`nlu.enable_streamlit_caching()`](#test)  | Enable caching the `nlu.load()` call. Once enabled, the `nlu.load()` method will automatically cached. **This is recommended** to run first and for large peformance gans |


# Detailed visualizer information and API docs

## <kbd>function</kbd> `pipe.viz_streamlit`


Display a highly configurable UI that showcases almost every feature available for Streamlit visualization with model selection dropdowns in your applications.   
Ths includes :
- `Similarity Matrix` & `Scalars` & `Embedding Information` for any of the [100+ Word Embedding Models]()
- `NER visualizations` for any of the [200+ Named entity recognizers]()
- `Labled` & `Unlabled Dependency Trees visualizations` with `Part of Speech Tags` for any of the [100+ Part of Speech Models]()
- `Token informations`  predicted by any of the [1000+ models]()
- `Classification results`  predicted by any of the [100+ models classification models]()
- `Pipeline Configuration` & `Model Information` & `Link to John Snow Labs Modelshub` for all loaded pipelines
- `Auto generate Python code` that can be copy pasted to re-create the individual Streamlit visualization blocks.
  NlLU takes the first model specified as `nlu.load()` for the first visualization run.     
  Once the Streamlit app is running, additional models can easily be added via the UI.    
  It is recommended to run this first, since you can generate Python code snippets `to recreate individual Streamlit visualization blocks`

```python
nlu.load('ner').viz_streamlit(['I love NLU and Streamlit!','I hate buggy software'])
```



![NLU Streamlit UI Overview](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/gif/ui.gif)

### <kbd>function parameters</kbd> `pipe.viz_streamlit`

| Argument              | Type                                             |                                                            Default                     |Description |
|-----------------------|--------------------------------------------------|----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `text`                  |  `Union [str, List[str], pd.DataFrame, pd.Series]` | `'NLU and Streamlit go together like peanutbutter and jelly'`                            | Default text for the `Classification`, `Named Entitiy Recognizer`, `Token Information` and `Dependency Tree` visualizations
| `similarity_texts`      |  `Union[List[str],Tuple[str,str]]`                 | `('Donald Trump Likes to part', 'Angela Merkel likes to party')`                         | Default texts for the `Text similarity` visualization. Should contain `exactly 2 strings` which will be compared `token embedding wise`. For each embedding active, a `token wise similarity matrix` and a `similarity scalar`
| `model_selection`       |  `List[str]`                                       | `[]`                                                                                         | List of nlu references to display in the model selector, see [the NLU Namespace](https://nlu.johnsnowlabs.com/docs/en/namespace) or the [John Snow Labs Modelshub](https://modelshub.johnsnowlabs.com/models)  or go [straight to the source](https://github.com/JohnSnowLabs/nlu/blob/master/nlu/namespace.py) for more info
| `title`                 |  `str`                                             | `'NLU ❤️ Streamlit - Prototype your NLP startup in 0 lines of code🚀'`                      | Title of the Streamlit app
| `sub_title`             |  `str`                                             | `'Play with over 1000+ scalable enterprise NLP models'`                                  | Sub title of the Streamlit app
| `visualizers`           |  `List[str]`                                       | `( "dependency_tree", "ner",  "similarity", "token_information", 'classification')`      | Define which visualizations should be displayed. By default all visualizations are displayed.
| `show_models_info`      |  `bool`                                            | `True`                                                                                   | Show information for every model loaded in the bottom of the Streamlit app.
| `show_model_select`   |  `bool`                                          | `True`                                                                                 | Show a model selection dropdowns that makes any of the 1000+ models avaiable in 1 click
| `show_viz_selection`    |  `bool`                                            | `False`                                                                                  | Show a selector in the sidebar which lets you configure which visualizations are displayed.
| `show_logo`             |  `bool`                                            | `True`                                                                                   | Show logo
| `display_infos`         |  `bool`                                            | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.
| `set_wide_layout_CSS`     |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.
|     `key`                 |  `str`                                                              | `"NLU_streamlit"`    | Key for the Streamlit elements drawn
| `model_select_position`   |  `str`                                                             |   `'side'`            | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |
| `show_code_snippets`      |  `bool`                                                             |  `False`                                                                                 | Display Python code snippets above visualizations that can be used to re-create the visualization
|`num_similarity_cols`                               | `int`               |  `2`                            |  How many columns should for the layout in Streamlit when rendering the similarity matrixes.



## <kbd>function</kbd> `pipe.viz_streamlit_classes`

Visualize the predicted classes and their confidences and additional metadata to streamlit.
Aplicable with [any of the 100+ classifiers](https://nlp.johnsnowlabs.com/models?task=Text+Classification)

```python
nlu.load('sentiment').viz_streamlit_classes(['I love NLU and Streamlit!','I love buggy software', 'Sign up now get a chance to win 1000$ !', 'I am afraid of Snakes','Unicorns have been sighted on Mars!','Where is the next bus stop?'])
```
![text_class1](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/gif/class.gif)


### <kbd>function parameters</kbd> `pipe.viz_streamlit_classes`

| Argument    | Type        |                                                            Default         |Description |
|--------------------------- | ---------- |-----------------------------------------------------------| ------------------------------------------------------- |
| `text`                    | `Union[str,list,pd.DataFrame, pd.Series, pyspark.sql.DataFrame ]`   |     `'I love NLU and Streamlit and sunny days!'`                  | Text to predict classes for. Will predict on each input of the iteratable or dataframe if type is not str.|
| `output_level`            | `Optional[str]`                                                     |       `document`        | [Outputlevel of NLU pipeline, see `pipe.predict()` docsmore info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-level-parameter)|
| `include_text_col`        |  `bool`                                                              |`True`               | Whether to include a e text column in the output table or just the prediction data |
| `title`                   | `Optional[str]`                                                     |   `Text Classification`            | Title of the Streamlit building block that will be visualized to screen |
| `metadata`                | `bool`                                                              |  `False`             | [whether to output addition metadata or not, see `pipe.predict(meta=true)` docs for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-metadata) |
| `positions`               |  `bool`                                                             |   `False`            | [whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |
| `set_wide_layout_CSS`     |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.
|     `key`                 |  `str`                                                              | `"NLU_streamlit"`    | Key for the Streamlit elements drawn
| `model_select_position`   |  `str`                                                             |   `'side'`            | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |
| `generate_code_sample`      |  `bool`                                                             |  `False`                                                                                 | Display Python code snippets above visualizations that can be used to re-create the visualization
| `show_model_select`   |  `bool`                                          | `True`                                                                                 | Show a model selection dropdowns that makes any of the 1000+ models avaiable in 1 click
| `show_logo`             |  `bool`                                            | `True`                                                                                   | Show logo
| `display_infos`         |  `bool`                                            | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.



## <kbd>function</kbd> `pipe.viz_streamlit_ner`
Visualize the predicted classes and their confidences and additional metadata to Streamlit.
Aplicable with [any of the 250+ NER models](https://nlp.johnsnowlabs.com/models?task=Named+Entity+Recognition).    
You can filter which NER tags to highlight via the dropdown in the main window.

Basic usage
```python
nlu.load('ner').viz_streamlit_ner('Donald Trump from America and Angela Merkel from Germany dont share many views')
```

![NER visualization](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/gif/NER.gif)

Example for coloring
```python
# Color all entities of class GPE black
nlu.load('ner').viz_streamlit_ner('Donald Trump from America and Angela Merkel from Germany dont share many views',colors={'PERSON':'#6e992e', 'GPE':'#000000'})
```
![NER coloring](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/img/NER_colored.png)

### <kbd>function parameters</kbd> `pipe.viz_streamlit_ner`

| Argument    | Type        |                                                                                      Default                                        |Description                  |
|--------------------------- | -----------------------|-----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------ |
| `text`                     | `str`        # NLU & Streamlit visualizations          |     `'Donald Trump from America and Anegela Merkel from Germany do not share many views'`                 | Text to predict classes for.|
| `ner_tags`                 | `Optional[List[str]]`  |       `None`                                                                                               |Tags to display. By default all tags will be displayed|
| `show_label_select`        |  `bool`                |`True`                                                                                                      | Whether to include the label selector|
| `show_table`               | `bool`                 |   `True`                                                                                                   | Whether show to predicted pandas table or not|
| `title`                    | `Optional[str]`        |  `'Named Entities'`                                                                                        |  Title of the Streamlit building block that will be visualized to screen |
| `sub_title`                    | `Optional[str]`        |  `'"Recognize various Named Entities (NER) in text entered and filter them. You can select from over 100 languages in the dropdown. On the left side.",'`                                                                                        |  Sub-title of the Streamlit building block that will be visualized to screen |
| `colors`                   |  `Dict[str,str]`       |   `{}`                                                                                                     | Dict with `KEY=ENTITY_LABEL` and `VALUE=COLOR_AS_HEX_CODE`,which will change color of highlighted entities.[See custom color labels docs for more info.](https://nlu.johnsnowlabs.com/docs/en/viz_examples#define-custom-colors-for-labels) |
| `set_wide_layout_CSS`      |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.
|     `key`                  |  `str`                                                              | `"NLU_streamlit"`    | Key for the Streamlit elements drawn
| `generate_code_sample`       |  `bool`                                                             |  `False`                                                                                 | Display Python code snippets above visualizations that can be used to re-create the visualization
| `show_model_select`        |  `bool`                                          | `True`                                                                                 | Show a model selection dropdowns that makes any of the 1000+ models avaiable in 1 click
| `model_select_position`    |  `str`                                                             |   `'side'`            | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |
| `show_text_input`        |  `bool`                                                              | `True`                                                                                 | Show text input field to input text in
| `show_logo`             |  `bool`                                            | `True`                                                                                   | Show logo
| `display_infos`         |  `bool`                                            | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.




## <kbd>function</kbd> `pipe.viz_streamlit_dep_tree`
Visualize a typed dependency tree, the relations between tokens and part of speech tags predicted.
Aplicable with [any of the 100+ Part of Speech(POS) models and dep tree model](https://nlp.johnsnowlabs.com/models?task=Part+of+Speech+Tagging)

```python
nlu.load('dep.typed').viz_streamlit_dep_tree('POS tags define a grammatical label for each token and the Dependency Tree classifies Relations between the tokens')
```
![Dependency Tree](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/img/DEP.png)

### <kbd>function parameters</kbd> `pipe.viz_streamlit_dep_tree`

| Argument    | Type        |                                                            Default         |Description |
|--------------------------- | ---------- |-----------------------------------------------------------| ------------------------------------------------------- |
| `text`                    | `str`   |     `'Billy likes to swim'`                 | Text to predict classes for.|
| `title`                | `Optional[str]`                                                              |  `'Dependency Parse Tree & Part-of-speech tags'`             |  Title of the Streamlit building block that will be visualized to screen |
| `set_wide_layout_CSS`      |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.
|     `key`                  |  `str`                                                              | `"NLU_streamlit"`    | Key for the Streamlit elements drawn
| `generate_code_sample`       |  `bool`                                                             |  `False`                                                                                 | Display Python code snippets above visualizations that can be used to re-create the visualization
| `set_wide_layout_CSS`      |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.
|     `key`                  |  `str`                                                              | `"NLU_streamlit"`    | Key for the Streamlit elements drawn
| `generate_code_sample`       |  `bool`                                                             |  `False`                                                                                 | Display Python code snippets above visualizations that can be used to re-create the visualization
| `show_model_select`        |  `bool`                                          | `True`                                                                                 | Show a model selection dropdowns that makes any of the 1000+ models avaiable in 1 click
| `model_select_position`    |  `str`                                                             |   `'side'`            | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |
| `show_logo`             |  `bool`                                            | `True`                                                                                   | Show logo
| `display_infos`         |  `bool`                                            | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.

<img width="65%" align="right" src="https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/gif/start.gif">



## <kbd>function</kbd> `pipe.viz_streamlit_token`
Visualize predicted token and text features for every model loaded.
You can use this with [any of the 1000+ models](https://nlp.johnsnowlabs.com/models) and select them from the left dropdown.

```python
nlu.load('stemm pos spell').viz_streamlit_token('I liek pentut buttr and jelly !')
```
![text_class1](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/gif/token.gif)


### <kbd>function parameters</kbd> `pipe.viz_streamlit_token`

| Argument    | Type        |                                                            Default         |Description |
|--------------------------- | ---------- |-----------------------------------------------------------| ------------------------------------------------------- |
| `text`                    | `str`   |     `'NLU and Streamlit are great!'`                 | Text to predict token information for.|
| `title`                | `Optional[str]`                                                              |  `'Named Entities'`             |  Title of the Streamlit building block that will be visualized to screen |
| `show_feature_select`        |  `bool`                                                              |`True`               | Whether to include the token feature selector|
| `features`            | `Optional[List[str]]`                                                     |       `None`        |Features to to display. By default all Features will be displayed|
| `metadata`                | `bool`                                                              |  `False`             | [Whether to output addition metadata or not, see `pipe.predict(meta=true)` docs for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-metadata) |
| `output_level`            | `Optional[str]`                                                     |       `'token'`        | [Outputlevel of NLU pipeline, see `pipe.predict()` docsmore info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-level-parameter)|
| `positions`               |  `bool`                                                             |   `False`            | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |
| `set_wide_layout_CSS`      |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.
|     `key`                  |  `str`                                                              | `"NLU_streamlit"`    | Key for the Streamlit elements drawn
| `generate_code_sample`       |  `bool`                                                             |  `False`                                                                                 | Display Python code snippets above visualizations that can be used to re-create the visualization
| `show_model_select`        |  `bool`                                          | `True`                                                                                 | Show a model selection dropdowns that makes any of the 1000+ models avaiable in 1 click
| `model_select_position`    |  `str`                                                             |   `'side'`            | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |
| `show_logo`             |  `bool`                                            | `True`                                                                                   | Show logo
| `display_infos`         |  `bool`                                            | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.




## <kbd>function</kbd> `pipe.viz_streamlit_similarity`

- Displays a `similarity matrix`, where `x-axis` is every token in the first text and `y-axis` is every token in the second text.
- Index `i,j` in the matrix describes the similarity of `token-i` to `token-j` based on the loaded embeddings and distance metrics, based on [Sklearns Pariwise Metrics.](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics.pairwise). [See this article for more elaboration on similarities](https://medium.com/spark-nlp/easy-sentence-similarity-with-bert-sentence-embeddings-using-john-snow-labs-nlu-ea078deb6ebf)
- Displays  a dropdown selectors from which various similarity metrics and over 100 embeddings can be selected.
  -There will be one similarity matrix per `metric` and `embedding` pair selected. `num_plots = num_metric*num_embeddings`
  Also displays embedding vector information.
  Applicable with [any of the 100+ Word Embedding models](https://nlp.johnsnowlabs.com/models?task=Embeddings)



```python
nlu.load('bert').viz_streamlit_word_similarity(['I love love loooove NLU! <3','I also love love looove  Streamlit! <3'])
```
![text_class1](https://raw.githubusercontent.com/JohnSnowLabs/nlu/master/docs/assets/streamlit_docs_assets/gif/SIM.gif)

### <kbd>function parameters</kbd> `pipe.viz_streamlit_similarity`

| Argument    | Type        |                                                            Default         |Description |
|--------------------------- | ---------- |-----------------------------------------------------------| ------------------------------------------------------- |
| `texts`                                 | `str`               |     `'Donald Trump from America and Anegela Merkel from Germany do not share many views.'`                 | Text to predict token information for.|
| `title`                                 | `Optional[str]`     |  `'Named Entities'`             |  Title of the Streamlit building block that will be visualized to screen |
| `similarity_matrix`                     | `bool`              |       `None`                    |Whether to display similarity matrix or not|
| `show_algo_select`                      |  `bool`             |`True`                           | Whether to show dist algo select or not |
| `show_table`                            | `bool`              |   `True`                        | Whether show to predicted pandas table or not|
| `threshold`                             | `float`             |  `0.5`                          | Threshold for displaying result red on screen |
| `set_wide_layout_CSS`                   |  `bool`             |  `True`                         | Whether to inject custom CSS or not.
|     `key`                               |  `str`              | `"NLU_streamlit"`               | Key for the Streamlit elements drawn
| `generate_code_sample`                  |  `bool`             |  `False`                        | Display Python code snippets above visualizations that can be used to re-create the visualization
| `show_model_select`                     |  `bool`             | `True`                          | Show a model selection dropdowns that makes any of the 1000+ models avaiable in 1 click
| `model_select_position`                 |  `str`              |   `'side'`                      | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |
|`write_raw_pandas`                       | `bool`              |  `False`                        | Write the raw pandas similarity df to streamlit
|`display_embed_information`              | `bool`              |  `True`                         | Show additional embedding information like `dimension`, `nlu_reference`, `spark_nlp_reference`, `sotrage_reference`, `modelhub link` and more.
|`dist_metrics`                           | `List[str]`         |  `['cosine']`                   | Which distance metrics to apply. If multiple are selected, there will be multiple plots for each embedding and metric. `num_plots = num_metric*num_embeddings`. Can use multiple at the same time, any of of `cityblock`,`cosine`,`euclidean`,`l2`,`l1`,`manhattan`,`nan_euclidean`. Provided via [Sklearn `metrics.pairwise` package](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics.pairwise)
|`num_cols`                               | `int`               |  `2`                            |  How many columns should for the layout in streamlit when rendering the similarity matrixes.
|`display_scalar_similarities`            | `bool`              |  `False`                        | Display scalar simmilarities in an additional field.
|`display_similarity_summary`             | `bool`              |  `False`                        | Display summary of all similarities for all embeddings and metrics.
| `show_logo`             |  `bool`                             | `True`                                                                                   | Show logo
| `display_infos`         |  `bool`                             | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.



# Embedding visualization via Manifold and Matrix Decomposition algorithms

## <kbd>function</kbd> `pipe.viz_streamlit_word_embed_manifold`

Visualize Word Embeddings in `1-D`, `2-D`, or `3-D` by `Reducing Dimensionality` via 11 Supported methods from  [Manifold Algorithms](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.manifold)
and [Matrix Decomposition Algorithms](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.decomposition).
Additionally, you can color the lower dimensional points with a label that has been previously assigned to the text by specifying a list of nlu references in the `additional_classifiers_for_coloring` parameter.

- Reduces Dimensionality of high dimensional Word Embeddings to `1-D`, `2-D`, or `3-D` and plot the resulting data in an interactive `Plotly` plot
- Applicable with [any of the 100+ Word Embedding models](https://nlp.johnsnowlabs.com/models?task=Embeddings)
- Color points by classifying with any of the 100+ [Parts of Speech Classifiers](https://nlp.johnsnowlabs.com/models?task=Part+of+Speech+Tagging) or [Document Classifiers](https://nlp.johnsnowlabs.com/models?task=Text+Classification)
- Gemerates `NUM-DIMENSIONS` * `NUM-EMBEDDINGS` * `NUM-DIMENSION-REDUCTION-ALGOS` plots



```python
nlu.load('bert',verbose=True).viz_streamlit_word_embed_manifold(default_texts=['I love NLU <3',  'I love streamlit <3'],default_algos_to_apply=['TSNE'],MAX_DISPLAY_NUM=5)
```

<img  src="https://github.com/JohnSnowLabs/nlu/blob/master/docs/assets/streamlit_docs_assets/gif/word_embed_dimension_reduction/manifold_intro.gif?raw=true">




### <kbd>function parameters</kbd> `pipe.viz_streamlit_word_embed_manifold`

| Argument    | Type        |                                                            Default         |Description |
|----------------------------|------------|-----------------------------------------------------------|---------------------------------------------------------|
|`default_texts`|                    `List[str]`  | ("Donald Trump likes to party!", "Angela Merkel likes to party!", 'Peter HATES TO PARTTY!!!! :(') | List of strings to apply classifiers, embeddings, and manifolds to. |  
| `text`                                         | `Optional[str]`   |     `'Billy likes to swim'`                 | Text to predict classes for. |   
|`sub_title`|                    `Optional[str]` | "Apply any of the 11 `Manifold` or `Matrix Decomposition` algorithms to reduce the dimensionality of `Word Embeddings` to `1-D`, `2-D` and `3-D` " | Sub title of the Streamlit app |   
|`default_algos_to_apply`|           `List[str]` | `["TSNE", "PCA"]` | A list Manifold and Matrix Decomposition Algorithms to apply. Can be either `'TSNE'`,`'ISOMAP'`,`'LLE'`,`'Spectral Embedding'`, `'MDS'`,`'PCA'`,`'SVD aka LSA'`,`'DictionaryLearning'`,`'FactorAnalysis'`,`'FastICA'` or `'KernelPCA'`, |   
|`target_dimensions`|              `List[int]`   | `(1,2,3)` | Defines the target dimension embeddings will be reduced to |
|`show_algo_select`|               `bool`        | `True`  | Show selector for Manifold and Matrix Decomposition Algorithms |   
|`show_embed_select`|              `bool`        | `True` | Show selector for Embedding Selection |  
|`show_color_select`|              `bool`        | `True` | Show selector for coloring plots  |
|`MAX_DISPLAY_NUM`|                  `int`       |`100` | Cap maximum number of Tokens displayed  |
|`display_embed_information`                     | `bool`              |  `True`                         | Show additional embedding information like `dimension`, `nlu_reference`, `spark_nlp_reference`, `sotrage_reference`, `modelhub link` and more.|  
| `set_wide_layout_CSS`                          |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.|  
|`num_cols`                                      | `int`               |  `2`                            |  How many columns should for the layout in streamlit when rendering the similarity matrixes.|  
|     `key`                                      |  `str`              | `"NLU_streamlit"`               | Key for the Streamlit elements drawn  |
|`additional_classifiers_for_coloring`           |         `List[str]`|`['pos', 'sentiment.imdb']` | List of additional NLU references to load for generting hue colors  |
| `show_model_select`                            |  `bool`                                          | `True`                                                                                 | Show a model selection dropdowns that makes any of the 1000+ models avaiable in 1 click  |
| `model_select_position`                        |  `str`                                                             |   `'side'`            | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |   
| `show_logo`                                    |  `bool`                                            | `True`                                                                                   | Show logo  |
| `display_infos`                                |  `bool`                                            | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.|  
| `n_jobs`                                       |          `Optional[int]` | `3`|   `False` | How many cores to use for paralellzing when using Sklearn Dimension Reduction algorithms.  |  




### Larger Example showcasing more dimension reduction techniques on a larger corpus :

<img  src="https://github.com/JohnSnowLabs/nlu/blob/master/docs/assets/streamlit_docs_assets/gif/word_embed_dimension_reduction/big_example_word_embedding_dimension_reduction.gif?raw=true">




## <kbd>function</kbd> `pipe.viz_streamlit_sentence_embed_manifold`

Visualize Sentence Embeddings in `1-D`, `2-D`, or `3-D` by `Reducing Dimensionality` via 12 Supported methods from  [Manifold Algorithms](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.manifold)
and [Matrix Decomposition Algorithms](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.decomposition).
Additionally, you can color the lower dimensional points with a label that has been previously assigned to the text by specifying a list of nlu references in the `additional_classifiers_for_coloring` parameter.
You can also select additional classifiers via the GUI.

- Reduces Dimensionality of high dimensional Sentence Embeddings to `1-D`, `2-D`, or `3-D` and plot the resulting data in an interactive `Plotly` plot
- Applicable with [any of the 100+ Sentence Embedding models](https://nlp.johnsnowlabs.com/models?task=Embeddings)
- Color points by classifying with any of the 100+ [Document Classifiers](https://nlp.johnsnowlabs.com/models?task=Text+Classification)
- Gemerates `NUM-DIMENSIONS` * `NUM-EMBEDDINGS` * `NUM-DIMENSION-REDUCTION-ALGOS` plots

```python
nlu.load('embed_sentence.bert').viz_streamlit_sentence_embed_manifold(['text1','text2tdo'])
```

<img  src="https://github.com/JohnSnowLabs/nlu/blob/master/docs/assets/streamlit_docs_assets/gif/sentence_embedding_dimension_reduction/sentence_manifold_low_qual.gif?raw=true">

### <kbd>function parameters</kbd> `pipe.viz_streamlit_sentence_embed_manifold`
| Argument    | Type        |                                                            Default         |Description |
|----------------------------|------------|-----------------------------------------------------------|---------------------------------------------------------|
|`default_texts`|                    `List[str]`  | ("Donald Trump likes to party!", "Angela Merkel likes to party!", 'Peter HATES TO PARTTY!!!! :(') | List of strings to apply classifiers, embeddings, and manifolds to. |  
| `text`                                         | `Optional[str]`   |     `'Billy likes to swim'`                 | Text to predict classes for. |   
|`sub_title`|                    `Optional[str]` | "Apply any of the 11 `Manifold` or `Matrix Decomposition` algorithms to reduce the dimensionality of `Sentence Embeddings` to `1-D`, `2-D` and `3-D` " | Sub title of the Streamlit app |   
|`default_algos_to_apply`|           `List[str]` | `["TSNE", "PCA"]` | A list Manifold and Matrix Decomposition Algorithms to apply. Can be either `'TSNE'`,`'ISOMAP'`,`'LLE'`,`'Spectral Embedding'`, `'MDS'`,`'PCA'`,`'SVD aka LSA'`,`'DictionaryLearning'`,`'FactorAnalysis'`,`'FastICA'` or `'KernelPCA'`, |   
|`target_dimensions`|              `List[int]`   | `(1,2,3)` | Defines the target dimension embeddings will be reduced to |
|`show_algo_select`|               `bool`        | `True`  | Show selector for Manifold and Matrix Decomposition Algorithms |   
|`show_embed_select`|              `bool`        | `True` | Show selector for Embedding Selection |  
|`show_color_select`|              `bool`        | `True` | Show selector for coloring plots  |
|`display_embed_information`                     | `bool`              |  `True`                         | Show additional embedding information like `dimension`, `nlu_reference`, `spark_nlp_reference`, `sotrage_reference`, `modelhub link` and more.|  
| `set_wide_layout_CSS`                          |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.|  
|`num_cols`                                      | `int`               |  `2`                            |  How many columns should for the layout in streamlit when rendering the similarity matrixes.|  
|     `key`                                      |  `str`              | `"NLU_streamlit"`               | Key for the Streamlit elements drawn  |
|`additional_classifiers_for_coloring`           |         `List[str]`|`['sentiment.imdb']` | List of additional NLU references to load for generting hue colors  |
| `show_model_select`                            |  `bool`                                          | `True`                                                                                 | Show a model selection dropdowns that makes any of the 1000+ models avaiable in 1 click  |
| `model_select_position`                        |  `str`                                                             |   `'side'`            | [Whether to output the positions of predictions or not, see `pipe.predict(positions=true`) for more info](https://nlu.johnsnowlabs.com/docs/en/predict_api#output-positions-parameter)  |   
| `show_logo`                                    |  `bool`                                            | `True`                                                                                   | Show logo  |
| `display_infos`                                |  `bool`                                            | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.|  
| `n_jobs`                                       |          `Optional[int]` | `3`|   `False` | How many cores to use for paralellzing when using Sklearn Dimension Reduction algorithms.  |  




## Streamlit Entity Manifold visualization
## <kbd>function</kbd> `pipe.viz_streamlit_entity_embed_manifold`
Visualize recognized entities by NER models via their Entity Embeddings in `1-D`, `2-D`, or `3-D` by `Reducing Dimensionality` via 10+ Supported methods from  [Manifold Algorithms](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.manifold)
and [Matrix Decomposition Algorithms](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.decomposition).
You can pick additional NER models and compare them via the GUI dropdown on the left.


- Reduces Dimensionality of high dimensional Entity Embeddings to `1-D`, `2-D`, or `3-D` and plot the resulting data in an interactive `Plotly` plot
- Applicable with [any of the 330+ Named Entity Recognizer models](https://nlp.johnsnowlabs.com/models?task=Named+Entity+Recognition)
- Gemerates `NUM-DIMENSIONS` * `NUM-NER-MODELS` * `NUM-DIMENSION-REDUCTION-ALGOS` plots

```python
nlu.load('ner').viz_streamlit_sentence_embed_manifold(['Hello From John Snow Labs', 'Peter loves to visit New York'])
```
<img  src="https://github.com/JohnSnowLabs/nlu/blob/master/docs/assets/streamlit_docs_assets/gif/entity_embedding_dimension_reduction/low_quality.gif?raw=true">

### <kbd>function parameters</kbd> `pipe.viz_streamlit_sentence_embed_manifold`
| Argument    | Type        |                                                            Default         |Description |
|----------------------------|------------|-----------------------------------------------------------|---------------------------------------------------------|
|`default_texts`|                    `List[str]`  |"Donald Trump likes to visit New York", "Angela Merkel likes to visit Berlin!", 'Peter hates visiting Paris')| List of strings to apply classifiers, embeddings, and manifolds to. |  
| `title`                 |  `str`                                             | `'NLU ❤️ Streamlit - Prototype your NLP startup in 0 lines of code🚀'`                      | Title of the Streamlit app
|`sub_title`|                    `Optional[str]` | "Apply any of the 10+ `Manifold` or `Matrix Decomposition` algorithms to reduce the dimensionality of `Entity Embeddings` to `1-D`, `2-D` and `3-D` " | Sub title of the Streamlit app |   
|`default_algos_to_apply`|           `List[str]` | `["TSNE", "PCA"]` | A list Manifold and Matrix Decomposition Algorithms to apply. Can be either `'TSNE'`,`'ISOMAP'`,`'LLE'`,`'Spectral Embedding'`, `'MDS'`,`'PCA'`,`'SVD aka LSA'`,`'DictionaryLearning'`,`'FactorAnalysis'`,`'FastICA'` or `'KernelPCA'`, |   
|`target_dimensions`|              `List[int]`   | `(1,2,3)` | Defines the target dimension embeddings will be reduced to |
|`show_algo_select`|               `bool`        | `True`  | Show selector for Manifold and Matrix Decomposition Algorithms |   
| `set_wide_layout_CSS`                          |  `bool`                                                             |  `True`                                                                                   | Whether to inject custom CSS or not.|  
|`num_cols`                                      | `int`               |  `2`                            |  How many columns should for the layout in streamlit when rendering the similarity matrixes.|  
|     `key`                                      |  `str`              | `"NLU_streamlit"`               | Key for the Streamlit elements drawn  |
| `show_logo`                                    |  `bool`                                            | `True`                                                                                   | Show logo  |
| `display_infos`                                |  `bool`                                            | `False`                                                                                  | Display additonal information about ISO codes and the NLU namespace structure.|  
| `n_jobs`                                       |          `Optional[int]` | `3`|   `False` | How many cores to use for paralellzing when using Sklearn Dimension Reduction algorithms.  |  





### [Supported Manifold Algorithms for Word, Sentence and Entity Embeddings](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.manifold)
- [TSNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html#sklearn.manifold.TSNE)
- [ISOMAP](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.Isomap.html#sklearn.manifold.Isomap)
- [LLE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.LocallyLinearEmbedding.html#sklearn.manifold.LocallyLinearEmbedding)
- [Spectral Embedding](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.SpectralEmbedding.html#sklearn.manifold.SpectralEmbedding)
- [MDS](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.MDS.html#sklearn.manifold.MDS)

### [Supported Matrix Decomposition Algorithms for Word,Sentence and Entity Embeddings](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.decomposition)
- [PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html#sklearn.decomposition.PCA)
- [Truncated SVD aka LSA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html#sklearn.decomposition.TruncatedSVD)
- [DictionaryLearning](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.DictionaryLearning.html#sklearn.decomposition.DictionaryLearning)
- [FactorAnalysis](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.FactorAnalysis.html#sklearn.decomposition.FactorAnalysis)
- [FastICA](https://scikit-learn.org/stable/modules/generated/fastica-function.html#sklearn.decomposition.fastica)
- [KernelPCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.KernelPCA.html#sklearn.decomposition.KernelPCA)
- [Latent Dirichlet Allocation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html)

