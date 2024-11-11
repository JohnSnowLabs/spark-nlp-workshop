
import com.johnsnowlabs.nlp.AnnotatorModel;
import com.johnsnowlabs.nlp.DocumentAssembler;
import com.johnsnowlabs.nlp.annotators.Chunker;
import com.johnsnowlabs.nlp.annotators.Tokenizer;
import com.johnsnowlabs.nlp.annotators.assertion.dl.AssertionDLApproach;
import com.johnsnowlabs.nlp.annotators.assertion.dl.AssertionDLModel;
import com.johnsnowlabs.nlp.annotators.assertion.logreg.Datapoint;
import com.johnsnowlabs.nlp.annotators.assertion.logreg.NegexDatasetReader;
import com.johnsnowlabs.nlp.annotators.pos.perceptron.PerceptronModel;
import com.johnsnowlabs.nlp.annotators.sbd.pragmatic.SentenceDetector;
import com.johnsnowlabs.nlp.embeddings.WordEmbeddingsModel;
import lombok.val;
import org.apache.spark.ml.PipelineModel;
import org.apache.spark.ml.PipelineStage;
import org.apache.spark.sql.*;
import scala.collection.Seq;
import org.apache.spark.ml.Pipeline;
import java.util.LinkedList;

public class AssertionDLExample {



    public static void main(String args[]) {
        SparkSession spark = SparkSession
                .builder()
                .appName("PipelineExample")
                .config("spark.master", "local")
                .config("spark.driver.memory", "6G")
                .config("spark.kryoserializer.buffer.max", "1G")
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
                .getOrCreate();
        LinkedList<String> text = new java.util.LinkedList<String>();

        text.add("Has a past history of gastroenteritis and stomach pain, however patient shows no stomach pain now." +
        "We don't care about gastroenteritis here, but we do care about heart failure.");

        Dataset<Row> data = spark.createDataset(text, Encoders.STRING()).toDF("text");

        DocumentAssembler document = new DocumentAssembler();
        document.setInputCol("text");
        document.setOutputCol("document");

        SentenceDetector sentenceDetector = new SentenceDetector();
        sentenceDetector.setInputCols(new String[]{"document"});
        sentenceDetector.setOutputCol("sentence");

        Tokenizer tokenizer = new Tokenizer();
        tokenizer.setInputCols(new String[]{"sentence"});
        tokenizer.setOutputCol("token");

        PerceptronModel POSTag = PerceptronModel.pretrained();
        POSTag.setInputCols(new String[]{"sentence", "token"});
        POSTag.setOutputCol("pos");

        Chunker chunker = new Chunker();
        chunker.setInputCols(new String[]{"pos", "sentence"});
        chunker.setOutputCol("chunk");
        chunker.setRegexParsers(new String[]{"(<NN>)+"});

        WordEmbeddingsModel wordEmbeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models");
        wordEmbeddings.setInputCols(new String[]{"sentence", "token"});
        wordEmbeddings.setOutputCol("embeddings");
        wordEmbeddings.setCaseSensitive(false);


        AssertionDLModel assertionStatus = com.johnsnowlabs.nlp.annotators.assertion.dl.AssertionDLModel.pretrained("assertion_dl", "en", "clinical/models");
        assertionStatus.setInputCols(new String[]{"sentence", "chunk", "embeddings"});
        assertionStatus.setOutputCol("assertion");
        assertionStatus.setIncludeConfidence(true);

     Pipeline pipeline = new Pipeline();
     pipeline.setStages(new PipelineStage[] {document, sentenceDetector,tokenizer,POSTag,chunker,wordEmbeddings,assertionStatus});

     PipelineModel pipelineModel = pipeline.fit(data);
     Dataset<Row> outputDf = pipelineModel.transform(data);
     outputDf.show();







    }





}
