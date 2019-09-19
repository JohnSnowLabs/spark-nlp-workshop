package services.ml.ner

import com.johnsnowlabs.nlp.RecursivePipeline
import com.johnsnowlabs.nlp.annotator.Tokenizer
import com.johnsnowlabs.nlp.annotators.ner.dl.NerDLApproach
import com.johnsnowlabs.nlp.annotators.ner.{NerConverter, Verbose}
import com.johnsnowlabs.nlp.base.{DocumentAssembler, Finisher}
import com.johnsnowlabs.nlp.embeddings.{WordEmbeddings, WordEmbeddingsFormat}
import com.johnsnowlabs.nlp.training.CoNLL
import org.apache.log4j.{Level, Logger}
import org.apache.spark.ml.PipelineModel
import org.apache.spark.sql.SparkSession

object CustomForNerDLPipelineForTwoDotTwoDotOne {

  val ENABLE_TRAINING = true
  val EMBEDDING_DIMENSIONS = 300
  val PATH_TO_GRAPH_FOLDER = "C:\\OpenSourceData\\GRAPH_FOLDER"
  val PATH_TO_EXTERAL_EMBEDDINGS_SOURCE = "file:///C:/OpenSourceData/REFERENTIAL_DATA/glove.6B.300d.txt"
  val TRAINED_PIPELINE_NAME = "file:///C:/OpenSourceData/SAVED_MODELS/PreprocessedDummyEmailsData.pipeline"
  val PATH_TO_EXTERNAL_DATA__TO_BE_USED_FOR_TRAINING = "file:///C:/OpenSourceData/input/spark-nlp/TaggedPreprocessedDummyDataOfEmails.conll"


  def main(args: Array[String]): Unit = {
    Logger.getLogger("org").setLevel(Level.OFF)
    Logger.getLogger("akka").setLevel(Level.OFF)
    Logger.getRootLogger.setLevel(Level.INFO)

    val spark: SparkSession = SparkSession.builder().appName("test").master("local[*]")
      .config("spark.driver.memory", "12G").config("spark.kryoserializer.buffer.max", "200M")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer").getOrCreate()

    import spark.implicits._
    spark.sparkContext.setLogLevel("FATAL")

    val document = new DocumentAssembler().setInputCol("text").setOutputCol("document")

    val token = new Tokenizer().setInputCols("document").setOutputCol("token")

    val word_embeddings = new WordEmbeddings().setInputCols(Array("document", "token")).setOutputCol("word_embeddings")
      .setEmbeddingsSource(PATH_TO_EXTERAL_EMBEDDINGS_SOURCE, EMBEDDING_DIMENSIONS, WordEmbeddingsFormat.TEXT)

    val trainingConll = CoNLL().readDataset(spark, PATH_TO_EXTERNAL_DATA__TO_BE_USED_FOR_TRAINING)

    val ner = new NerDLApproach()
      .setInputCols("document", "token", "word_embeddings")
      .setOutputCol("ner")
      .setLabelColumn("label")
      .setMaxEpochs(120)
      .setRandomSeed(0)
      .setPo(0.03f)
      .setLr(0.2f)
      .setDropout(0.5f)
      .setBatchSize(9)
      .setGraphFolder(PATH_TO_GRAPH_FOLDER)
      .setVerbose(Verbose.Epochs)


    val nerConverter = new NerConverter().setInputCols("document", "token", "ner").setOutputCol("ner_converter")

    val finisher = new Finisher().setInputCols("ner", "ner_converter").setIncludeMetadata(true).setOutputAsArray(false)
      .setCleanAnnotations(false).setAnnotationSplitSymbol("@").setValueSplitSymbol("#")

    val pipeline = new RecursivePipeline()
      .setStages(Array(document, token, word_embeddings, ner, nerConverter, finisher))

    val testingForTop10Carriers = Seq(
      (1, "Google has announced the release of a beta version of the popular TensorFlow machine learning library"),
      (2, "The Paris metro will soon enter the 21st century, ditching single-use paper tickets for rechargeable electronic cards.")
    ).toDS.toDF("_id", "text")

    val testing = testingForTop10Carriers
    var pipelineModel: PipelineModel = null
    if (ENABLE_TRAINING) {
      println("Training started.......")
      pipelineModel = pipeline.fit(trainingConll)
      pipelineModel.write.save(TRAINED_PIPELINE_NAME)
      println(s"Pipeline Model saved '$TRAINED_PIPELINE_NAME'.........")
    }
    else {
      println(s"Loading the already built model from '$TRAINED_PIPELINE_NAME'.........")
      pipelineModel = PipelineModel.load(TRAINED_PIPELINE_NAME)
    }

    val result = pipelineModel.transform(testing)

    result.select("ner_converter") show (truncate = false)

    val actualListOfNamedEntitiesMap = result.select("finished_ner").collectAsList().toArray
      .map(x => x.toString.drop(1).dropRight(1).split("@")).map(keyValuePair => keyValuePair
      .map(x => (x.split("->").lastOption.get, x.slice(x.indexOf("->") + 2, x.indexOf("#")))).filter(!_._1.equals("O"))
      .groupBy(_._1).mapValues(_.map(_._2).toList))


    val length = actualListOfNamedEntitiesMap.length
    for (index <- 0 until length) {
      println("Keys present in actualOutputMap but not in actualOutputMap:  %s"
        .format(actualListOfNamedEntitiesMap(index)))
    }

  }
}
