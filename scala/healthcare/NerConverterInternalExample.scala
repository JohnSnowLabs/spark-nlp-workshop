import AssertionDLApproachExample.spark
import com.johnsnowlabs.nlp.DocumentAssembler
import com.johnsnowlabs.nlp.annotator.{NerDLModel, SentenceDetector, WordEmbeddingsModel}
import com.johnsnowlabs.nlp.annotators.Tokenizer
import com.johnsnowlabs.nlp.annotators.ner.NerConverterInternal
import com.johnsnowlabs.nlp.util.io.ResourceHelper
import org.apache.spark.sql.SparkSession
import org.apache.spark.ml.Pipeline

object NerConverterInternalExample extends App {

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


  val data = ResourceHelper.spark.createDataFrame(Seq(Tuple1("My name is Andres and I live in Colombia"))).toDF("text")

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
    .setInputCols("document", "token")
    .setOutputCol("embeddings")
    .setCaseSensitive(false)

  val ner = NerDLModel.pretrained()
    .setInputCols("sentence", "token", "embeddings")
    .setOutputCol("ner")
    .setIncludeConfidence(true)

  val converter = new NerConverterInternal()
    .setInputCols("sentence", "token", "ner")
    .setOutputCol("entities")
    .setPreservePosition(false)
    .setThreshold(9900e-4f)

  val pipeline = new Pipeline()
    .setStages(Array(
      documentAssembler,
      sentenceDetector,
      tokenizer,
      embeddings,
      ner,
      converter
    ))

  val nermodel = pipeline.fit(data).transform(data)

  nermodel.select("token.result").show(1, false)
  nermodel.select("embeddings.result").show(1, false)
  nermodel.select("entities.result").show(1, false)
  nermodel.select("entities").show(1, false)
  spark.stop
}
