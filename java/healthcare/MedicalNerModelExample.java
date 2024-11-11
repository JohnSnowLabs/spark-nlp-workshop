import com.johnsnowlabs.nlp.DocumentAssembler;
import com.johnsnowlabs.nlp.Finisher;
import com.johnsnowlabs.nlp.annotators.Tokenizer;
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

import java.util.LinkedList;

public class MedicalNerModelExample {



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

        text.add("The human KCNJ9 (Kir 3.3, GIRK3) is a member of the G-protein-activated inwardly rectifying potassium (GIRK) " +
                "channel family. Here we describe the genomic organization of the KCNJ9 locus on chromosome 1q21-23 as a candidate " +
                "gene for Type II diabetes mellitus in the Pima Indian population. The gene spans approximately 7.6 kb and contains one" +
                " noncoding and two coding exons separated by approximately 2.2 and approximately 2.6 kb introns, respectively. We identified 14 single " +
                "nucleotide polymorphisms (SNPs), including one that predicts a Val366Ala substitution, and an 8 base-pair (bp) insertion/deletion. " +
                "Our expression studies revealed the presence of the transcript in various human tissues including pancreas, and two major insulin-responsive tissues: fat and skeletal muscle. The characterization of the KCNJ9 gene should facilitate further studies on the function of the KCNJ9 protein and allow evaluation of the potential role of the locus in Type II diabetes..");

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



        MedicalNerModel nerDlModel = MedicalNerModel.pretrained("ner_clinical_large", "en", "clinical/models");
        nerDlModel.setInputCols(new String[]{"sentence", "token","embeddings"});
        nerDlModel.setOutputCol("ner_tags");



        Pipeline pipeline = new Pipeline();
        pipeline.setStages(new PipelineStage[] {document, sentenceDetector,tokenizer,wordEmbeddings,nerDlModel});

        PipelineModel pipelineModel = pipeline.fit(data);
        Dataset<Row> outputDf = pipelineModel.transform(data);
        outputDf.select("ner_tags.result").show(200,false);







    }





}
