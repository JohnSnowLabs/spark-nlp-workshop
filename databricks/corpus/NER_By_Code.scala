// Databricks notebook source
import com.johnsnowlabs.nlp._
import com.johnsnowlabs.nlp.annotator._
import com.johnsnowlabs.nlp.annotators._
import com.johnsnowlabs.nlp.annotators.ner._
import com.johnsnowlabs.nlp.DocumentAssembler

import org.apache.spark.ml._
import org.apache.spark.sql.functions.{col, lower}

// COMMAND ----------

//NER Entityes Vocabulary for ICD10 (prioritize on count)
//Find exact matches UMLS

// COMMAND ----------

val data = spark.read.format("csv")
  .option("header", "true")
  .load("/andres/icd10/icd10cm.csv")

// COMMAND ----------

val docAssembler = new DocumentAssembler()
  .setInputCol("description")
  .setOutputCol("document")

val tokenizer = new Tokenizer()
  .setInputCols("document")
  .setOutputCol("token")

// COMMAND ----------

val embeddings = WordEmbeddingsModel.load("/andres/pretrained/clinical_embeddings")
//val embeddings = WordEmbeddingsModel.load("/andres/pretrained/embeddings_clinical_en_2.0.2_2.4_1558454742956/")
.setInputCols("document", "token")
.setOutputCol("embeddings")

// COMMAND ----------

val ner = NerDLModel.load("/andres/pretrained/clinical_ner")
//val ner = NerDLModel.load("/andres/pretrained/ner_clinical_en_2.0.2_2.4_1556659769638")
  .setInputCols("document","token","embeddings")
  .setOutputCol("ner")

// COMMAND ----------

//embeddings.save("/andres/pretrained/clinical_embeddings")
//ner.save("/andres/pretrained/clinical_ner")

// COMMAND ----------

val ner_converter = new NerConverter()
    .setInputCols(Array("document", "token", "ner"))
    .setOutputCol("ner_chunk")

// COMMAND ----------

val concept_pipeline = new Pipeline().setStages(Array(
  docAssembler,
  tokenizer,
  embeddings,
  ner,
  ner_converter
))

// COMMAND ----------

val nered = concept_pipeline.fit(data).transform(data)

// COMMAND ----------

val ner_by_code = nered.select(col("code"), lower(col("ner_chunk.result")).alias("ner")).distinct()

// COMMAND ----------

ner_by_code.write.format("parquet").saveAsTable("icd10.ners_by_code")

// COMMAND ----------


