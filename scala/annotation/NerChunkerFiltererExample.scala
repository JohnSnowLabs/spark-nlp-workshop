package example

import com.johnsnowlabs.nlp.SparkAccessor.spark
import com.johnsnowlabs.nlp.SparkAccessor.spark.implicits._
import com.johnsnowlabs.nlp._
import com.johnsnowlabs.nlp.annotator.{NerDLModel, PerceptronModel, SentenceDetector, Tokenizer}
import com.johnsnowlabs.nlp.annotators.assertion.dl.AssertionDLApproach
import com.johnsnowlabs.nlp.annotators.assertion.logreg.NegexDatasetReader
import com.johnsnowlabs.nlp.annotators.chunker.ChunkFilterer
import com.johnsnowlabs.nlp.annotators.ner.NerChunker
import com.johnsnowlabs.nlp.annotators.sbd.pragmatic.SentenceDetector
import com.johnsnowlabs.nlp.annotators.{Chunker, Tokenizer}
import com.johnsnowlabs.nlp.base.{DocumentAssembler, RecursivePipeline}
import com.johnsnowlabs.nlp.embeddings.WordEmbeddingsModel
import com.johnsnowlabs.nlp.util.io.ResourceHelper
import org.apache.spark.ml.Pipeline


object NerChunkerFiltererExample extends App {

  val data = ResourceHelper.spark.createDataFrame(Seq(Tuple1("My name  Andres and I live in Colombia"))).toDF("text")

  val documentAssembler = new DocumentAssembler()
    .setInputCol("text")
    .setOutputCol("document")

  val sentenceDetector = new SentenceDetector()
    .setInputCols("document")
    .setOutputCol("sentence")
    .setUseAbbreviations(false)

  val tokenizer = new Tokenizer()
    .setInputCols(Array("sentence"))
    .setOutputCol("token")

  val embeddings = WordEmbeddingsModel.pretrained()
    .setInputCols("sentence", "token")
    .setOutputCol("embeddings")
    .setCaseSensitive(false)

  val ner = NerDLModel.pretrained()
    .setInputCols("sentence", "token", "embeddings")
    .setOutputCol("ner")
    .setIncludeConfidence(true)
  ner.getClasses

  val chunker = new NerChunker()
    .setInputCols(Array("sentence", "ner"))
    .setOutputCol("ner_chunk")
    .setRegexParsers(Array("<PER>.*<LOC>"))


  val recursivePipeline = new RecursivePipeline()
    .setStages(Array(
      documentAssembler,
      sentenceDetector,
      tokenizer,
      embeddings,
      ner,
      chunker
    ))

  val nermodel = recursivePipeline.fit(data).transform(data)


  val dataframe = nermodel.select("ner_chunk.result")
  dataframe.show(truncate = false)
}
