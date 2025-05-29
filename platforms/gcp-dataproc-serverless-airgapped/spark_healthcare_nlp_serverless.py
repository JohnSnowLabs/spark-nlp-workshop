import json, os

import sparknlp
import sparknlp_jsl

from sparknlp.base import *
from sparknlp.annotator import *
from sparknlp_jsl.annotator import *

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.sql import SparkSession

import warnings
warnings.filterwarnings('ignore')


# Initialize Spark NLP Healthcare Session
params = {
    "spark.driver.memory": "16G",
    "spark.kryoserializer.buffer.max": "2000M",
    "spark.driver.maxResultSize": "2000M"
}


def start():
    builder = SparkSession.builder \
        .appName("Spark NLP Licensed") \
        .config("spark.driver.memory", "16G") \
        .config("spark.driver.maxResultSize", "2000M") \
        .config("spark.kryoserializer.buffer.max", "2000M") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.jars", 
                "gs://spark-healthcare-nlp-serverless/jars/spark-nlp-jsl-6.0.0.jar,"
                "gs://spark-healthcare-nlp-serverless/jars/spark-nlp-assembly-6.0.0.jar")

    return builder.getOrCreate()


print("**********************Starting Spark Session...***************************")
spark = start()
print("**********************Spark session ready! ***************************")



print("******************** Starting building the spark NLP Healthcare pipeline... ********************* ")
document_assembler = DocumentAssembler()\
      .setInputCol("text")\
      .setOutputCol("chunk")

chunkerMapper = ChunkMapperModel.load("gs://spark-healthcare-nlp-serverless/models/drug_brandname_ndc_mapper_en")\
      .setInputCols(["chunk"])\
      .setOutputCol("ndc")\
      .setRels(["Strength_NDC"])

pipeline = Pipeline().setStages([document_assembler,
                                 chunkerMapper])  

model = pipeline.fit(spark.createDataFrame([['']]).toDF('text')) 

print("******************** Pipeline ready! ********************* ")
lp = LightPipeline(model)

results = lp.fullAnnotate('ZYVOX')
     

print("************Pipline model is ready! *****************")


print("***************** showing results ! ***************")

print(results)


print("***************** Job completed successfully! *****************")
 