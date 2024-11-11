import AssertionDLApproachExample.spark
import com.johnsnowlabs.nlp.DocumentAssembler
import com.johnsnowlabs.nlp.annotator.{NerDLModel, SentenceDetector, WordEmbeddingsModel}
import com.johnsnowlabs.nlp.annotators.Tokenizer
import com.johnsnowlabs.nlp.annotators.ner.NerChunker
import com.johnsnowlabs.nlp.util.io.ResourceHelper
import org.apache.spark.sql.SparkSession
import org.apache.spark.ml.Pipeline

object NerChunkerFiltererExample extends App {

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


  val pipeline = new Pipeline()
    .setStages(Array(
      documentAssembler,
      sentenceDetector,
      tokenizer,
      embeddings,
      ner,
      chunker
    ))

  val nermodel = pipeline.fit(data).transform(data)


  val dataframe = nermodel.select("ner_chunk.result")
  dataframe.show(truncate = false)
  spark.stop
}
