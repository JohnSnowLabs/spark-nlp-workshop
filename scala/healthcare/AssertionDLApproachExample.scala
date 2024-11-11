import com.johnsnowlabs.nlp.DocumentAssembler
import com.johnsnowlabs.nlp.annotator.{PerceptronModel, WordEmbeddingsModel}
import com.johnsnowlabs.nlp.annotators.assertion.dl.AssertionDLApproach
import com.johnsnowlabs.nlp.annotators.assertion.logreg.NegexDatasetReader
import com.johnsnowlabs.nlp.annotators.sbd.pragmatic.SentenceDetector
import com.johnsnowlabs.nlp.annotators.{Chunker, Tokenizer}
import org.apache.spark.ml.Pipeline
import org.apache.spark.sql.SparkSession

object AssertionDLApproachExample extends App {

  val spark: SparkSession = SparkSession
    .builder()
    .appName("test")
    .master("local[*]")
    .config("spark.driver.memory", "6G")
    .config("spark.kryoserializer.buffer.max", "1G")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .getOrCreate()

  import spark.implicits._

  implicit val session = spark

  val testDS = Seq(
    "Has a past history of gastroenteritis and stomach pain, however patient shows no stomach pain now. " +
      "We don't care about gastroenteritis here, but we do care about heart failure. " +
      "Test for asma, no asma.").toDF("text")
  val reader = new NegexDatasetReader

  val datasetPath = "src/test/resources/rsAnnotations-1-120-random.txt"
  val trainDS = reader.readDataframe(datasetPath).withColumnRenamed("sentence", "text").cache


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

  val pubmed = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models")
    .setInputCols("sentence", "token")
    .setOutputCol("embeddings")
    .setCaseSensitive(false)


  val assertionStatus = new AssertionDLApproach()
    .setGraphFolder("src/main/resources/assertion_dl/")
    .setInputCols("sentence", "chunk", "embeddings")
    .setOutputCol("assertion")
    .setStartCol("start")
    .setEndCol("end")
    .setLabelCol("label")
    .setLearningRate(0.01f)
    .setDropout(0.15f)
    .setBatchSize(16)
    .setEpochs(3)
    .setValidationSplit(0.2f)

  val stages = Array(documentAssembler, sentenceDetector, tokenizer, POSTag, chunker, pubmed,
    assertionStatus)

  // train Assertion Status
  val pipeline = new Pipeline()
    .setStages(stages)

  val model = pipeline.fit(trainDS)
  val outDf = model.transform(testDS)
  outDf.show(truncate = false)


  spark.stop
}
