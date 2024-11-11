import json
import threading
import time

from flask import Flask
from johnsnowlabs import *
import logging
import os

import streamlit as st

import config

spark = None
pipelines = dict()
lightpipelines = dict()
is_healthcheck_on = False


@st.experimental_singleton()
def start_spark():
    global spark
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

    logging.info(f"Building or getting the Spark Session...")
    start_time = time.time()
    spark = nlp.start(json_license_path='license.json', spark_conf=config.conf, master_url=f'local[{config.cores}]')
    end_time = time.time()
    logging.warning(f"- ELAPSED: {end_time - start_time}")
    return True


def force_start_spark():
    global spark
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

    logging.info(f"Building or getting the Spark Session...")
    start_time = time.time()
    spark = nlp.start(json_license_path='license.json', spark_conf=config.conf, master_url=f'local[{config.cores}]')
    end_time = time.time()
    logging.warning(f"- ELAPSED: {end_time - start_time}")
    return True


@st.experimental_singleton()
def load_pipelines(domain):
    global pipelines, spark
    if len(pipelines) == 0:
        logging.info(f"Checking if we need to download models...")
        start_time = time.time()
        document_assembler = nlp.DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")

        sentencizer = nlp.SentenceDetector() \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")

        spark_tokenizer = nlp.Tokenizer() \
            .setInputCols("sentence") \
            .setOutputCol("token")

        if domain == 'finance':
            zero_shot_ner = finance.ZeroShotNerModel.pretrained("finner_roberta_zeroshot", "en", "finance/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")
        elif domain == 'legal':
            zero_shot_ner = legal.ZeroShotNerModel.pretrained("legner_roberta_zeroshot", "en", "legal/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")
        else:
            zero_shot_ner = medical.ZeroShotNerModel.pretrained("zero_shot_ner_roberta", "en", "clincial/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")

        ner_converter = nlp.NerConverterInternal() \
            .setInputCols(["sentence", "token", "zero_shot_ner"]) \
            .setOutputCol("ner_chunk")

        pipeline = nlp.Pipeline(stages=[
            document_assembler,
            sentencizer,
            spark_tokenizer,
            zero_shot_ner,
            ner_converter,
        ]
        )

        if spark is None:
            logging.warning("Session not found, recreating...")
            force_start_spark()

        pipelines['ner'] = pipeline.fit(spark.createDataFrame([[""]]).toDF("text"))
        end_time = time.time()
        logging.warning(f"- ELAPSED: {end_time - start_time}. Pipelines loaded: {len(pipelines)}")
    else:
        logging.info("Pipeline already loaded")
    return True


def force_load_pipelines(domain):
    global pipelines, spark
    if len(pipelines) == 0:
        logging.info(f"Checking if we need to download models...")
        start_time = time.time()
        document_assembler = nlp.DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")

        sentencizer = nlp.SentenceDetector() \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")

        spark_tokenizer = nlp.Tokenizer() \
            .setInputCols("sentence") \
            .setOutputCol("token")

        if domain == 'finance':
            zero_shot_ner = finance.ZeroShotNerModel.pretrained("finner_roberta_zeroshot", "en", "finance/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")
        elif domain == 'legal':
            zero_shot_ner = legal.ZeroShotNerModel.pretrained("legner_roberta_zeroshot", "en", "legal/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")
        else:
            zero_shot_ner = medical.ZeroShotNerModel.pretrained("zero_shot_ner_roberta", "en", "clincial/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")

        ner_converter = nlp.NerConverterInternal() \
            .setInputCols(["sentence", "token", "zero_shot_ner"]) \
            .setOutputCol("ner_chunk")

        pipeline = nlp.Pipeline(stages=[
            document_assembler,
            sentencizer,
            spark_tokenizer,
            zero_shot_ner,
            ner_converter,
        ]
        )

        if spark is None:
            logging.warning("Session not found, recreating...")
            force_start_spark()

        pipelines['ner'] = pipeline.fit(spark.createDataFrame([[""]]).toDF("text"))
        end_time = time.time()
        logging.warning(f"- ELAPSED: {end_time - start_time}. Pipelines loaded: {len(pipelines)}")
    else:
        logging.info("Pipeline already loaded")
    return True


@st.experimental_singleton()
def set_prompts(pipe, prompts, domain):
    global pipelines
    if pipe in pipelines:
        pipelines[pipe].stages[-2].setEntityDefinitions(prompts)
    else:
        logging.error(f"Reloading pipes...")
        force_load_pipelines(domain)
        pipelines[pipe].stages[-2].setEntityDefinitions(prompts)
    return True


@st.experimental_singleton()
def pipe_to_lp(pipe):
    global lightpipelines, pipelines
    if pipe in lightpipelines:
        return
    else:
        if pipe in pipelines:
            lightpipelines[pipe] = nlp.LightPipeline(pipelines[pipe])
        else:
            logging.error(f"Unable to set create LightPipeline. Pipeline {pipe} not found.")
    return True


def force_pipe_to_lp(pipe):
    global lightpipelines, pipelines
    if pipe in lightpipelines:
        return
    else:
        if pipe in pipelines:
            lightpipelines[pipe] = nlp.LightPipeline(pipelines[pipe])
        else:
            logging.error(f"Unable to set create LightPipeline. Pipeline {pipe} not found.")
    return True


def infer(pipe, text):
    global lightpipelines
    if pipe in lightpipelines:
        return lightpipelines[pipe].fullAnnotate(text)
    else:
        logging.error(f"LightPipeline {pipe} not found. Recreating...")
        force_pipe_to_lp(pipe)
        return lightpipelines[pipe].fullAnnotate(text)


@st.experimental_singleton
def start_healthcheck_listener():
    global is_healthcheck_on, spark
    if not is_healthcheck_on:
        is_healthcheck_on = True
        app = Flask(__name__)

        @app.route('/healthcheck')
        def check_jvm_spark():
            try:
                if spark is None:
                    logging.warning("Session not found, recreating...")
                    force_start_spark()
                spark.createDataFrame([[""]])
                return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
            except Exception as e:
                logging.error(f"[Healthcheck] Spark NLP or java are not running. Cause: {e}")
                return json.dumps({'success': False}), 503, {'ContentType': 'application/json'}

        threading.Thread(target=lambda: app.run(host="0.0.0.0", port=config.HEALTHCHECK_PORT, debug=True,
                                                use_reloader=False)).start()

        with open('/tmp/spark_status', 'w') as f:
            f.write('READY')


@st.experimental_singleton
def spark_stop():
    global spark
    if spark is not None:
        spark.stop()
    else:
        logging.warning("Spark not found, so it may have already crashed...")
    return True

"""
    def save(self, model, path=None):
        recognized = ['ner', 're']
        if model not in recognized:
            logging.error(f"Model should be one of these: {str(recognized)}")
        if path is None:
            path = model
        self.pipelines[model].stages[-1].write().overwrite().save(path)
"""
