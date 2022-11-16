package com.johnsnowlabs.sparknlp;

import com.amazonaws.thirdparty.jackson.core.JsonProcessingException;
import com.amazonaws.thirdparty.jackson.databind.ObjectMapper;
import com.johnsnowlabs.SparkNLPClient;
import com.johnsnowlabs.legal.sequence_classification.LegalClassifierDLModel;
import com.johnsnowlabs.nlp.LightPipeline;
import com.johnsnowlabs.nlp.annotators.classifier.dl.ClassifierDLModel;
import com.johnsnowlabs.nlp.embeddings.BertSentenceEmbeddings;
import org.apache.spark.ml.Pipeline;
import org.apache.spark.ml.PipelineModel;
import org.apache.spark.ml.PipelineStage;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import com.johnsnowlabs.nlp.*;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;
import scala.collection.JavaConverters;
import scala.collection.Seq;

import java.lang.reflect.Field;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;

public class SparkNLPManager {
    SparkSession spark;
    HashMap<String, LightPipeline> pipelines = new HashMap<>();

    private static final Logger logger = Logger.getLogger(SparkNLPClient.class.getName());

    public SparkNLPManager() {
        try {
            this._setEnvVars();
        } catch (Exception e) {
            warning("Unable to set Env Vars. Error: " + e.getMessage());
        }

        this.spark = SparkSession.builder().
        appName("Spark NLP").
        master("local[*]").
        config("spark.driver.memory","4G").
        config("spark.kryoserializer.buffer.max", "2000M").
        config("spark.jars", "D:\\IdeaProjects\\grpc\\jars\\spark-nlp-jsl-4.2.1.jar").
        getOrCreate();

        this._load_pipelines();
    }

    private void _setEnvVars() throws Exception {
        HashMap<String,String> newvars = new HashMap<String, String>() {{
                put("AWS_ACCESS_KEY_ID", "");
                put("AWS_SECRET_ACCESS_KEY","");
                put("SPARK_NLP_LICENSE","");
                put("SECRET", "");
                put("JSL_VERSION", "");
                put("PUBLIC_VERSION", "");

        }};
        this._setEnv(newvars);
    }

    private void _setEnv(Map<String, String> newenv) throws Exception {
        try {
            Class<?> processEnvironmentClass = Class.forName("java.lang.ProcessEnvironment");
            Field theEnvironmentField = processEnvironmentClass.getDeclaredField("theEnvironment");
            theEnvironmentField.setAccessible(true);
            Map<String, String> env = (Map<String, String>) theEnvironmentField.get(null);
            env.putAll(newenv);
            Field theCaseInsensitiveEnvironmentField = processEnvironmentClass.getDeclaredField("theCaseInsensitiveEnvironment");
            theCaseInsensitiveEnvironmentField.setAccessible(true);
            Map<String, String> cienv = (Map<String, String>) theCaseInsensitiveEnvironmentField.get(null);
            cienv.putAll(newenv);
        } catch (NoSuchFieldException e) {
            Class[] classes = Collections.class.getDeclaredClasses();
            Map<String, String> env = System.getenv();
            for(Class cl : classes) {
                if("java.util.Collections$UnmodifiableMap".equals(cl.getName())) {
                    Field field = cl.getDeclaredField("m");
                    field.setAccessible(true);
                    Object obj = field.get(env);
                    Map<String, String> map = (Map<String, String>) obj;
                    map.clear();
                    map.putAll(newenv);
                }
            }
        }
    }
    private void _load_pipelines() {
        DocumentAssembler documentassembler = new DocumentAssembler();
        documentassembler.setInputCol("clause_text");
        documentassembler.setOutputCol("document");

        AnnotatorModel<BertSentenceEmbeddings> embedding = BertSentenceEmbeddings.pretrained("sent_bert_base_cased", "en");
        embedding.setInputCols(new String[]{"document"});
        embedding.setOutputCol("sentence_embeddings");

        AnnotatorModel<ClassifierDLModel> warranty = LegalClassifierDLModel.pretrained("legclf_cuad_warranty_clause", "en", "legal/models");
        warranty.setInputCols(new String[]{"sentence_embeddings"});
        warranty.setOutputCol("is_warranty");

        AnnotatorModel<ClassifierDLModel> indemnification = LegalClassifierDLModel.pretrained("legclf_cuad_indemnifications_clause", "en", "legal/models");
        indemnification.setInputCols(new String[]{"sentence_embeddings"});
        indemnification.setOutputCol("is_indemnification");

        AnnotatorModel<ClassifierDLModel> whereas = LegalClassifierDLModel.pretrained("legclf_whereas_clause", "en", "legal/models");
        whereas.setInputCols(new String[]{"sentence_embeddings"});
        whereas.setOutputCol("is_whereas");

        AnnotatorModel<ClassifierDLModel> confidentiality = LegalClassifierDLModel.pretrained("legclf_confidential_clause", "en", "legal/models");
        confidentiality.setInputCols(new String[]{"sentence_embeddings"});
        confidentiality.setOutputCol("is_confidentiality");

        Pipeline pipeline = new Pipeline().setStages(new PipelineStage[]{
                documentassembler,
                embedding,
                warranty,
                indemnification,
                whereas,
                confidentiality});
        // code
        StructType structType = new StructType();
        structType = structType.add("text", DataTypes.StringType, false);

        List<Row> nums = new ArrayList<Row>();
        nums.add(RowFactory.create(""));

        Dataset<Row> df = spark.createDataFrame(nums, structType);

        PipelineModel fit_model = pipeline.fit(df);
        LightPipeline lightpipeline = new LightPipeline(fit_model, false);
        this.pipelines.put("clf", lightpipeline);
    }

    public String clf(String text) {
        scala.collection.immutable.Map<String, Seq<String>>[] result =  this.pipelines.get("clf").annotate(new String[]{text});
        StringBuilder s = new StringBuilder();
        s.append("[");
        for(scala.collection.immutable.Map<String, Seq<String>> elem: result) {
            Map<String, Seq<String>> java_elem = JavaConverters
                    .mapAsJavaMapConverter(elem).asJava();
            s.append("{");
            for(String key: java_elem.keySet()) {
                s.append("\"");
                s.append(key);
                s.append("\": ");
                List<String> seq = JavaConverters.seqAsJavaList(java_elem.get(key));
                ObjectMapper mapper = new ObjectMapper();
                String res = null;
                try {
                    res = mapper.writeValueAsString(seq);
                } catch (JsonProcessingException e) {
                    throw new RuntimeException(e);
                }
                s.append(res);
                s.append(",");
            }
            s.append("},");
        }
        s.append("]");

        return s.toString();
    }

    private void info(String msg, Object... params) {
        logger.log(Level.INFO, msg, params);
    }

    private void warning(String msg, Object... params) {
        logger.log(Level.WARNING, msg, params);
    }

}
