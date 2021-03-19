package example

import com.johnsnowlabs.nlp.SparkAccessor.spark
import com.johnsnowlabs.nlp.SparkAccessor.spark.implicits._
import com.johnsnowlabs.nlp._
import com.johnsnowlabs.nlp.annotator.{PerceptronModel, WordEmbeddingsModel}
import com.johnsnowlabs.nlp.annotators.assertion.dl.{AssertionDLApproach, AssertionDLModel}
import com.johnsnowlabs.nlp.annotators.assertion.logreg.NegexDatasetReader
import com.johnsnowlabs.nlp.annotators.chunker.{AssertionFilterer, ChunkFilterer}
import com.johnsnowlabs.nlp.annotators.sbd.pragmatic.SentenceDetector
import com.johnsnowlabs.nlp.annotators.{Chunker, Tokenizer}
import org.apache.spark.ml.Pipeline


object ChunkerFiltererExample extends App {

  implicit val session = spark

  val testDS = Seq(
    "Has a past history of gastroenteritis and stomach pain, however patient shows no stomach pain now. " +
      "We don't care about gastroenteritis here, but we do care about heart failure. " +
      "Test for asma, no asma.").toDF("text")
  val reader = new NegexDatasetReader

  val datasetPath = "src/test/resources/rsAnnotations-1-120-random.txt"

  val documentAssembler = new DocumentAssembler()
    .setInputCol("text")
    .setOutputCol("document")

  val sentenceDetector = new SentenceDetector()
    .setInputCols(Array("document"))
    .setOutputCol("sentence")

  val tokenizer = new Tokenizer()
    .setInputCols(Array("sentence"))
    .setOutputCol("token")

  val POSTag = PerceptronModel
    .pretrained()
    .setInputCols("sentence", "token")
    .setOutputCol("pos")

  val chunker = new Chunker()
    .setInputCols(Array("pos", "sentence"))
    .setOutputCol("chunk")
    .setRegexParsers(Array("(<NN>)+"))


  val chunkerFilter =new ChunkFilterer()
    .setInputCols("sentence","chunk")
    .setOutputCol("filtered")
    .setCriteria("isin")
    .setWhiteList("gastroenteritis","stomach pain","heart failure")




  val stages = Array(documentAssembler, sentenceDetector, tokenizer, POSTag, chunker, chunkerFilter)
  val pipeline = new Pipeline()
    .setStages(stages)
  val model = pipeline.fit(testDS)
  val outDf = model.transform(testDS)

  // train Assertion Status


  outDf.selectExpr("filtered").show(truncate = false)
  outDf.selectExpr("chunk").show(truncate = false)

}
