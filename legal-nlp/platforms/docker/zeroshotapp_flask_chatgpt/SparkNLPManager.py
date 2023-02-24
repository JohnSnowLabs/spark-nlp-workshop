import time

from johnsnowlabs import *
import logging
import os

import config


class SparkNLPManager:
    def __init__(self, domain):
        self.domain = domain
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

        logging.info(f"Building or getting the Spark Session...")
        start_time = time.time()
        self.spark = nlp.start(json_license_path='license.json', spark_conf=config.conf, master_url=f'local[{config.cores}]')
        end_time = time.time()
        logging.warning(f"- ELAPSED: {end_time - start_time}")

        self.pipelines = {}
        self.light_pipelines = {}
        self.load_pipelines()

    def restart_spark(self):
        logging.info(f"Restarting the Spark Session...")
        start_time = time.time()
        self.spark = nlp.start(json_license_path='license.json', spark_conf=config.conf, master_url=f'local[{config.cores}]')
        end_time = time.time()
        logging.warning(f"- ELAPSED: {end_time - start_time}")

    def load_pipelines(self, force=False):
        logging.info(f"Load pipelines called. Checking if we need to download models...")
        self.load_ner_pipeline(force)
        # self.load_re_pipeline(force)

    def load_ner_pipeline(self, force=False):

        if len(self.pipelines) == 0 or force:
            logging.info(f"Load `ner` pipeline called. Checking if we need to download models...")
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

            if self.domain == 'finance':
                zero_shot_ner = finance.ZeroShotNerModel.pretrained("finner_roberta_zeroshot", "en", "finance/models") \
                    .setInputCols(["sentence", "token"]) \
                    .setOutputCol("zero_shot_ner")
            elif self.domain == 'legal':
                zero_shot_ner = legal.ZeroShotNerModel.pretrained("legner_roberta_zeroshot", "en", "legal/models") \
                    .setInputCols(["sentence", "token"]) \
                    .setOutputCol("zero_shot_ner")
            else:
                zero_shot_ner = medical.ZeroShotNerModel.pretrained("zero_shot_ner_roberta", "en", "clincial/models") \
                    .setInputCols(["sentence", "token"]) \
                    .setOutputCol("zero_shot_ner")

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

            if self.spark is None:
                logging.warning("- Session not found, recreating...")
                self.restart_spark()

            fit_model = pipeline.fit(self.spark.createDataFrame([[""]]).toDF("text"))
            self.pipelines['ner'] = fit_model
            self.from_pipe_to_lp('ner')
            end_time = time.time()
            logging.info(f"- ELAPSED: {end_time - start_time}. Pipelines loaded: {len(self.pipelines)}")
        else:
            logging.info("Ner already loaded")

    def from_pipe_to_lp(self, pipe):
        pipeline = self.pipelines[pipe]
        self.light_pipelines[pipe] = nlp.LightPipeline(pipeline)

    def set_prompts(self, pipe, prompts):
        logging.info(f"Setting prompts.")
        if pipe not in self.pipelines:
            logging.warning(f"- Reloading pipes...")
            self.load_pipelines(force=True)
        self.pipelines[pipe].stages[-2].setEntityDefinitions(prompts)
        self.from_pipe_to_lp(pipe)

    def infer(self, pipe, text):
        logging.info("Inferring...")
        if pipe not in self.pipelines or pipe not in self.light_pipelines:
            logging.warning(f"Pipeline {pipe} not found. Recreating...")
            self.load_pipelines(pipe)
        return self.light_pipelines[pipe].fullAnnotate(text)

    def spark_stop(self):
        if self.spark is not None:
            self.spark.stop()
        else:
            logging.warning("Trying to stop Spark, but Spark was not found, so it may have already crashed...")
        return True

    def save(self, model, path=None):
        recognized = ['ner', 're']
        if model not in recognized:
            logging.error(f"Model should be one of these: {str(recognized)}")
        if path is None:
            path = model
        self.pipelines[model].stages[-2].write().overwrite().save(path)

