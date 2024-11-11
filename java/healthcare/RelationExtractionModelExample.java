import com.johnsnowlabs.nlp.DocumentAssembler;
import com.johnsnowlabs.nlp.Finisher;
import com.johnsnowlabs.nlp.annotators.Tokenizer;
import com.johnsnowlabs.nlp.annotators.deid.DeIdentification;
import com.johnsnowlabs.nlp.annotators.ner.MedicalNerModel;
import com.johnsnowlabs.nlp.annotators.ner.NerConverterInternal;
import com.johnsnowlabs.nlp.annotators.parser.dep.DependencyParserModel;
import com.johnsnowlabs.nlp.annotators.pos.perceptron.PerceptronModel;
import com.johnsnowlabs.nlp.annotators.re.RelationExtractionModel;
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
import java.util.LinkedList;

public class RelationExtractionModelExample {



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

        text.add("The patient was prescribed 1 unit of Advil for 5 days after meals. The patient was also " +
                "given 1 unit of Metformin daily." +
                "He was seen by the endocrinology service and she was discharged on 40 units of insulin glargine at night , " +
                "12 units of insulin lispro with meals , and metformin 1000 mg two times a day.");

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

        WordEmbeddingsModel wordEmbeddings = WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models");
        wordEmbeddings.setInputCols(new String[]{"sentence", "token"});
        wordEmbeddings.setOutputCol("embeddings");

        PerceptronModel posTagger = PerceptronModel.pretrained("pos_clinical","en","clinical/models");
        posTagger.setInputCols(new String[]{"sentence", "token"});
        posTagger.setOutputCol("pos_tags");


        MedicalNerModel nerDlModel = MedicalNerModel.pretrained("ner_posology", "en", "clinical/models");
        nerDlModel.setInputCols(new String[]{"sentence", "token","embeddings"});
        nerDlModel.setOutputCol("ner_tags");

        NerConverterInternal ner_chunk = new NerConverterInternal();
        ner_chunk.setInputCols(new String[]{"sentence", "token","ner_tags"});
        ner_chunk.setOutputCol("ner_chunk");
        ner_chunk.setPreservePosition(false);

        DependencyParserModel depencyParser = DependencyParserModel.pretrained("dependency_conllu", "en");
        depencyParser.setInputCols(new String[]{"document", "token","pos_tags"});
        depencyParser.setOutputCol("dependencies");


        RelationExtractionModel re = RelationExtractionModel.pretrained("posology_re", "en", "clinical/models");
        re.setInputCols(new String[]{"embeddings", "pos_tags", "ner_chunk", "dependencies"});
        re.setOutputCol("relations_t");
        re.setMaxSyntacticDistance(4);

        Finisher finisher = new Finisher();
        finisher.setInputCols(new String[]{"relations_t"});
        finisher.setOutputCols(new String[]{"relations"});
        finisher.setCleanAnnotations(false);
        finisher.setValueSplitSymbol(",");
        finisher.setAnnotationSplitSymbol(",");
        finisher.setOutputAsArray(false);

        Pipeline pipeline = new Pipeline();
        pipeline.setStages(new PipelineStage[] {document, sentenceDetector,tokenizer,wordEmbeddings,posTagger,nerDlModel,ner_chunk,depencyParser,re,finisher});

        PipelineModel pipelineModel = pipeline.fit(data);
        Dataset<Row> outputDf = pipelineModel.transform(data);
        outputDf.select("relations").show(200,false);







    }





}
