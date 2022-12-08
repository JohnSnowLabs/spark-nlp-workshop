from johnsnowlabs import *
import streamlit as st
import json
import logging
import re

from pathlib import Path
from time import sleep

from SparkNLPManager import set_prompts, pipe_to_lp, infer, start_healthcheck_listener, spark_stop, \
    force_load_pipelines, pipelines


class StreamlitManager:
    html_widget = ""
    FILE_REGEX = r'[a-zA-Z0-9]+'
    file_compiled_regex = re.compile(FILE_REGEX)

    def __init__(self, domain, _pipelines):
        if len(_pipelines) < 1:
            logging.info("Reloading pipelines...")
            if len(pipelines) < 1:
                logging.info("- Forcing reloading pipelines in spark...")
                force_load_pipelines(domain)
            logging.info("- Done!")
            _pipelines = pipelines

        self.domain = domain
        pipe = st.sidebar.selectbox("Select ZeroShot pipeline:", _pipelines.keys(), key='selectbox')

        # Get text input
        text = st.sidebar.text_area(placeholder="Enter the text to predict on", label="Text",
                                    label_visibility="collapsed", key='inputarea', max_chars=1000)

        # Get other inputs
        tags_count = st.sidebar.slider('Number of tags:', min_value=1, max_value=10, value=2, step=1, key='slider_tags')

        st.sidebar.markdown("---")
        tags = {}
        confidences = {}
        counter = 0
        cols = st.sidebar.columns(tags_count)

        for i in range(tags_count):
            with cols[i]:
                # Tags
                st.sidebar.text(f"Tag {i+1}:")
                tag = st.sidebar.text_input(placeholder=f"Tag {i+1}", label=f"tag{i}", label_visibility="collapsed",
                                            key=f"tag{i}")
                tag = tag.strip()

                # Confidences
                tag_confidence = st.sidebar.slider('Minimum Confidence:', min_value=0.0, max_value=1.0, value=0.5,
                                                   step=0.05, key=f"tc{i}")
                confidences[tag] = [tag_confidence]

                # Questions
                tags[tag] = []
                questions_count = st.sidebar.slider('Number of questions:', min_value=1, max_value=10, value=2, step=1,
                                                    key=f"qc{i}")
                st.sidebar.text("Questions:")
                for j in range(questions_count):
                    tags[tag].append(st.sidebar.text_input(placeholder=f"Question {j+1}", label=f"question{counter}",
                                                           label_visibility="collapsed", key=f"question{counter}"))
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

        cols_btn = st.columns(2)
        with cols_btn[0]:
            st.button('Predict', key='predict_btn', on_click=self.predict, args=(pipe, tags, text, confidences))
            st.button('Crash', key='crash_btn', on_click=self.crash)
        with cols_btn[1]:
            filename = st.text_input(placeholder="Enter the file name", label="Filename",
                                     label_visibility="collapsed", key='filename')
            st.button('Save', key='save_btn', on_click=self.save, args=(filename, tags, pipe))

        # Show the HTML widget
        st.markdown(StreamlitManager.html_widget, unsafe_allow_html=True)

        start_healthcheck_listener()

    def predict(self, pipe, tags, text, confidences):
        set_prompts(pipe, tags, self.domain)

        pipe_to_lp(pipe)

        annotations = infer(pipe, text)
        annotation = annotations[0]

        filtered_by_conf = []
        annotation['ner_chunk'] = filter(lambda an: confidences[an['metadata']['entity']] <= an['metadata']['confidence'], annotation['ner_chunk'])

        #logging.info(annotation)

        # Create an HTML widget with the inputs
        if pipe == 'ner':
            ner_viz = viz.NerVisualizer()
            StreamlitManager.html_widget = ner_viz.display(result=annotation, label_col='ner_chunk',
                                                           document_col='document', raw_text=text, return_html=True)
            StreamlitManager.html_widget = StreamlitManager.html_widget.replace("$", "\\$")
            # logging.info(StreamlitManager.html_widget)

    def save(self, filename, tags, pipe):
        try:
            if not self.file_compiled_regex.match(filename):
                raise ValueError(f"Value not in [a-zA-Z0-9]: {filename}")
        except ValueError as e:
            self.show_error("Filename should not contain symbols, only characters and numbers.", e)
            return

        final = f"{filename}_{self.domain}_{pipe}.json"

        data_folder = Path("prompts")

        try:
            with open(data_folder / final, 'w') as f:
                f.write(json.dumps(tags))
                self.show_success(f"Prompts saved at {final}")
        except Exception as e:
            self.show_error(f"Unable to save to {final}.", e)

    @staticmethod
    def show_success(text):
        msg = st.success(text, icon="✅")
        sleep(3)
        msg.empty()

    @staticmethod
    def show_error(text, e):
        msg = st.error(text)
        sleep(3)
        msg.empty()
        logging.error(f"{text}. Cause: {e}")

    @staticmethod
    def crash():
        spark_stop()
