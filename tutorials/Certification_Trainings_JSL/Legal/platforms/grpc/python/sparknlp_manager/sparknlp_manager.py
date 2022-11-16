import time

from johnsnowlabs import *
import logging
import os


class SparkNLPManager:

    def __init__(self):
        # Managing logging level
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)

        logging.info("Starting Spark NLP ...")
        start_time = time.time()
        self.spark = jsl.start(aws_key_id="",
                               aws_access_key="",
                               hc_license="",
                               enterprise_nlp_secret="",
                               exclude_ocr=True)
        end_time = time.time()
        logging.info(f"- ELAPSED: {end_time - start_time}")

        self._download()

    def _download(self):
        logging.info("Downloading and loading pipelines into memory ...")
        self.pipelines = self._load_pipelines()

    def _load_pipelines(self):
        pipelines = dict()
        pipelines['clf'] = self._load_clf_pipeline()
        return pipelines

    def _load_clf_pipeline(self):
        documentassembler = nlp.DocumentAssembler() \
            .setInputCol("clause_text") \
            .setOutputCol("document")

        embedding = nlp.BertSentenceEmbeddings.pretrained("sent_bert_base_cased", "en") \
            .setInputCols("document") \
            .setOutputCol("sentence_embeddings")

        warranty = nlp.ClassifierDLModel.pretrained("legclf_cuad_warranty_clause", "en", "legal/models") \
            .setInputCols("sentence_embeddings") \
            .setOutputCol("is_warranty")

        indemnification = nlp.ClassifierDLModel.pretrained("legclf_cuad_indemnifications_clause", "en", "legal/models") \
            .setInputCols("sentence_embeddings") \
            .setOutputCol("is_indemnification")

        whereas = nlp.ClassifierDLModel.pretrained("legclf_whereas_clause", "en", "legal/models") \
            .setInputCols("sentence_embeddings") \
            .setOutputCol("is_whereas")

        confidentiality = nlp.ClassifierDLModel.pretrained("legclf_confidential_clause", "en", "legal/models") \
            .setInputCols("sentence_embeddings") \
            .setOutputCol("is_confidentiality")

        pipeline = Pipeline(stages=[
            documentassembler,
            embedding,
            warranty,
            indemnification,
            whereas,
            confidentiality])

        fit_model = pipeline.fit(self.spark.createDataFrame([[""]]).toDF("text"))
        lightpipeline = LightPipeline(fit_model)

        return lightpipeline
