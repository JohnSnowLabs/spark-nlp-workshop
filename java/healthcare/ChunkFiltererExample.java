import com.johnsnowlabs.nlp.DocumentAssembler;
import com.johnsnowlabs.nlp.annotators.Chunker;
import com.johnsnowlabs.nlp.annotators.Tokenizer;
import com.johnsnowlabs.nlp.annotators.assertion.dl.AssertionDLModel;
import com.johnsnowlabs.nlp.annotators.chunker.ChunkFiltererApproach;
import com.johnsnowlabs.nlp.annotators.pos.perceptron.PerceptronModel;
import com.johnsnowlabs.nlp.annotators.sbd.pragmatic.SentenceDetector;
import com.johnsnowlabs.nlp.embeddings.WordEmbeddingsModel;
import org.apache.spark.ml.Pipeline;
import org.apache.spark.ml.PipelineModel;
import org.apache.spark.ml.PipelineStage;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import scala.collection.JavaConverters;

import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedList;

public class ChunkFiltererExample {



    public static void main(String args[]) {
        SparkSession spark = SparkSession
                .builder()
                .appName("PipelineExample")
                .config("spark.master", "local")
                .config("spark.driver.memory", "6G")
                .config("spark.kryoserializer.buffer.max", "1G")
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
                .getOrCreate();
        LinkedList<String> text = new LinkedList<String>();

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

        ChunkFiltererApproach chunkerFilter = new ChunkFiltererApproach();
        chunkerFilter.setInputCols(new String[]{"sentence", "chunk"});
        chunkerFilter.setOutputCol("filtered");
        chunkerFilter.setCriteria("isin");
        chunkerFilter.setWhiteList(JavaConverters.asScalaBuffer(Arrays.asList("gastroenteritis", "stomach pain", "stomach pain")));


        Pipeline pipeline = new Pipeline();
        pipeline.setStages(new PipelineStage[] {document, sentenceDetector,tokenizer,POSTag,chunker,chunkerFilter});

        PipelineModel pipelineModel = pipeline.fit(data);
        Dataset<Row> outputDf = pipelineModel.transform(data);
        outputDf.show();







    }





}
