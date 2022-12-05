import logging

import streamlit as st
from johnsnowlabs import *


class StreamlitManager:
    html_widget = ""

    def __init__(self, spark_manager):
        self.spark_manager = spark_manager
        pipe = st.sidebar.selectbox("Select ZeroShot model:", self.spark_manager.light_pipelines.keys(), key='selectbox')

        # Get text input
        text = st.sidebar.text_area(placeholder="Enter the text to predict on", label="Text", label_visibility="collapsed", key='inputarea')

        # Get other inputs
        tags_count = st.sidebar.slider('Number of tags:', min_value=1, max_value=10, value=2, step=1, key='slider_tags')

        st.sidebar.markdown("---")
        tags = {}
        counter = 0
        cols = st.sidebar.columns(tags_count)
        for i in range(tags_count):
            with cols[i]:
                st.sidebar.text(f"Tag {i+1}:")
                tag = st.sidebar.text_input(placeholder=f"Tag {i+1}", label=f"tag{i}", label_visibility="collapsed", key=f"tag{i}")
                tag = tag.strip()

                questions_count = st.sidebar.slider('Number of questions:', min_value=1, max_value=10, value=2, step=1, key=f"qc{i}")
                tags[tag] = []
                st.sidebar.text("Questions:")
                for j in range(questions_count):
                    tags[tag].append(st.sidebar.text_input(placeholder=f"{tag} Question {j+1}", label=f"question{counter}", label_visibility="collapsed", key=f"question{counter}"))
                    counter += 1
                st.sidebar.markdown("---")

        # I remove all empty NER tags
        tags_keys = filter(lambda x: x.strip() != '', tags.keys())
        tags = {k: v for k, v in tags.items() if k in tags_keys}

        # I remove all NER tags without questions
        to_remove_no_questions = []
        for t in tags:
            tags[t] = list(filter(lambda x: x.strip() != '', tags[t]))
            if len(tags[t]) < 1:
                to_remove_no_questions.append(t)

        tags = {k: v for k, v in tags.items() if k not in to_remove_no_questions}

        logging.info(tags)

        st.button('Predict', key='predict_btn', on_click=self.predict, args=(pipe, tags, text,))

        # Show the HTML widget
        st.markdown(StreamlitManager.html_widget, unsafe_allow_html=True)

    def predict(self, pipe, tags, text):
        self.spark_manager.reload_pipeline(pipe, tags)

        annotation = self.spark_manager.light_pipelines[pipe].fullAnnotate(text)
        logging.info(annotation[0]['ner_chunk'])

        # Create an HTML widget with the inputs
        if pipe == 'ner':
            ner_viz = viz.NerVisualizer()
            StreamlitManager.html_widget = ner_viz.display(result=annotation[0], label_col='ner_chunk',
                                                           document_col='document', raw_text=text, return_html=True)
            StreamlitManager.html_widget = StreamlitManager.html_widget.replace("$", "\\$")
            logging.info(StreamlitManager.html_widget)

