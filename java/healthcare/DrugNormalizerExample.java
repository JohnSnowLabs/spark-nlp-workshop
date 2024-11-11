import com.johnsnowlabs.nlp.DocumentAssembler;
import com.johnsnowlabs.nlp.annotators.DrugNormalizer;
import org.apache.spark.ml.Pipeline;
import org.apache.spark.ml.PipelineModel;
import org.apache.spark.ml.PipelineStage;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Encoders;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.util.LinkedList;

public class DrugNormalizerExample {



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

        text.add("Sodium Chloride/Potassium Chloride 13bag");
        text.add("interferon alfa-2b 10 million unit ( 1 ml ) injec");
        text.add("aspirin 2 meq/ml oral solution");

        Dataset<Row> data = spark.createDataset(text, Encoders.STRING()).toDF("text");

        DocumentAssembler document = new DocumentAssembler();
        document.setInputCol("text");
        document.setOutputCol("document");

        DrugNormalizer drugNormalizer = new DrugNormalizer();
        drugNormalizer.setInputCols(new String[]{"document"});
        drugNormalizer.setOutputCol("document_normalized");
        drugNormalizer.setPolicy("all");




        Pipeline pipeline = new Pipeline();
        pipeline.setStages(new PipelineStage[] {document, drugNormalizer});

        PipelineModel pipelineModel = pipeline.fit(data);
        Dataset<Row> outputDf = pipelineModel.transform(data);
        outputDf.select("document_normalized").show(200,false);







    }





}
