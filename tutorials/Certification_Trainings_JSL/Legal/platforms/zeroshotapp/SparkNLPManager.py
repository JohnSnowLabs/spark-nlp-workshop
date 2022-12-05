import json
import time

from johnsnowlabs import *
import logging
import os

from pyspark.sql import SparkSession


class SparkNLPManager:

    def __init__(self, domain):
        # Managing logging level
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

        self.domain = domain

        self._start()

    @classmethod
    def install(cls):
        logging.warning("Installing Spark NLP ...")
        start_time = time.time()
        nlp.install(json_license_path='license.json')
        end_time = time.time()
        logging.warning(f"- ELAPSED: {end_time - start_time}")

    def _start(self):
        logging.info("Starting Spark NLP ...")
        start_time = time.time()
        self.spark = nlp.start(json_license_path='license.json')

        end_time = time.time()
        logging.warning(f"- ELAPSED: {end_time - start_time}")

        logging.warning(f"Using {self.domain} NLP")
        self._download()

    def _download(self):
        logging.warning("Downloading and loading pipelines into memory ...")
        self.pipelines = self._load_pipelines()
        self.light_pipelines = self._load_light_pipelines()

    def _load_pipelines(self):
        pipelines = dict()
        pipelines['ner'] = self._load_ner_pipeline()
        return pipelines

    def _load_light_pipelines(self):
        light_pipelines = dict()
        for k in self.pipelines:
            light_pipelines[k] = nlp.LightPipeline(self.pipelines[k])
        return light_pipelines

    def reload_pipeline(self, pipe, prompts):
        self.pipelines[pipe].stages[-2].setEntityDefinitions(prompts)
        self.light_pipelines[pipe] = nlp.LightPipeline(self.pipelines[pipe])

    def _load_zeroshotner(self):
        zero_shot_ner = None
        if self.domain == 'finance':
            zero_shot_ner = finance.ZeroShotNerModel.pretrained("finner_roberta_zeroshot", "en", "finance/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")
        elif self.domain == 'legal':
            zero_shot_ner = legal.ZeroShotNerModel.pretrained("legner_roberta_zeroshot", "en", "legal/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")
        elif self.domain == 'medical':
            zero_shot_ner = medical.ZeroShotNerModel.pretrained("zero_shot_ner_roberta", "en", "clincial/models") \
                .setInputCols(["sentence", "token"]) \
                .setOutputCol("zero_shot_ner")

        if zero_shot_ner is None:
            raise Exception(f"Unrecognized domain: {self.domain}")

        return zero_shot_ner

    def _load_ner_pipeline(self):
        document_assembler = nlp.DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")

        sentencizer = nlp.SentenceDetector() \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")

        spark_tokenizer = nlp.Tokenizer() \
            .setInputCols("sentence") \
            .setOutputCol("token")

        zero_shot_ner = self._load_zeroshotner()

        ner_converter = nlp.NerConverter() \
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

        fit_model = pipeline.fit(self.spark.createDataFrame([[""]]).toDF("text"))

        return fit_model

    def save(self, model, path=None):
        recognized = ['ner', 're']
        if model not in recognized:
            logging.error(f"Model should be one of these: {str(recognized)}")
        if path is None:
            path = model
        self.pipelines[model].stages[-1].write().overwrite().save(path)
