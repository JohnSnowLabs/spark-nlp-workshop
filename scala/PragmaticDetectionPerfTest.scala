import com.johnsnowlabs.nlp.annotator.SentenceDetector
import com.johnsnowlabs.nlp.base.{DocumentAssembler, LightPipeline, RecursivePipeline}
import com.johnsnowlabs.nlp.util.io.ResourceHelper
import com.johnsnowlabs.util.Benchmark

class PragmaticDetectionPerfTest extends App {

  val spark = ResourceHelper.spark
  import spark.implicits._

  val documentAssembler = new DocumentAssembler().
    setInputCol("text").
    setOutputCol("document")

  val sentenceDetector = new SentenceDetector()
    .setInputCols("document")
    .setOutputCol("sentence")
    .setUseAbbreviations(true)

  val recursivePipeline = new RecursivePipeline().
    setStages(Array(
      documentAssembler,
      sentenceDetector
    ))

  val nermodel = recursivePipeline.fit(Seq.empty[String].toDF("text"))
  val nerlpmodel = new LightPipeline(nermodel)

  val data = spark.read.parquet("data/sentiment.parquet")
  val n = 50000

  val subdata = data.select("text").as[String].take(n)

  Benchmark.measure(s"annotate $n sentences") {nerlpmodel.annotate(subdata)}

  val r = nerlpmodel.annotate("Hello Ms. Laura Goldman, you are always welcome here")
  println(r("sentence").mkString("##"))

}
