import com.johnsnowlabs.nlp.DocumentAssembler;
import com.johnsnowlabs.nlp.annotators.Chunker;
import com.johnsnowlabs.nlp.annotators.Tokenizer;
import com.johnsnowlabs.nlp.annotators.chunker.ChunkFiltererApproach;
import com.johnsnowlabs.nlp.annotators.ner.NerConverterInternal;
import com.johnsnowlabs.nlp.annotators.ner.dl.NerDLModel;
import com.johnsnowlabs.nlp.annotators.pos.perceptron.PerceptronModel;
import com.johnsnowlabs.nlp.annotators.sbd.pragmatic.SentenceDetector;
import com.johnsnowlabs.nlp.embeddings.WordEmbeddings;
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
import java.util.LinkedList;

public class NerConverterInternalFiltererExample {



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

        text.add("My name is Jesus and Live in Spain.");

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

        WordEmbeddingsModel wordEmbeddings = WordEmbeddingsModel.pretrained();
        wordEmbeddings.setInputCols(new String[]{"sentence", "token"});
        wordEmbeddings.setOutputCol("embeddings");

        NerDLModel nerDlModel = NerDLModel.pretrained();
        nerDlModel.setInputCols(new String[]{"sentence", "token","embeddings"});
        nerDlModel.setOutputCol("pos");

        NerConverterInternal ner_chunk = new NerConverterInternal();
        ner_chunk.setInputCols(new String[]{"sentence", "token","ner"});
        ner_chunk.setOutputCol("chunk");
        ner_chunk.setPreservePosition(false);




        Pipeline pipeline = new Pipeline();
        pipeline.setStages(new PipelineStage[] {document, sentenceDetector,tokenizer,wordEmbeddings,nerDlModel,ner_chunk});

        PipelineModel pipelineModel = pipeline.fit(data);
        Dataset<Row> outputDf = pipelineModel.transform(data);
        outputDf.show();







    }





}
