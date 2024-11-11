package com.johnsnowlabs.sparknlp_manager;

import com.amazonaws.thirdparty.jackson.core.JsonProcessingException;
import com.amazonaws.thirdparty.jackson.databind.ObjectMapper;
import com.google.gson.Gson;
import com.google.gson.internal.LinkedTreeMap;
import com.johnsnowlabs.Utils;
import com.johnsnowlabs.legal.sequence_classification.LegalClassifierDLModel;
import com.johnsnowlabs.nlp.AnnotatorModel;
import com.johnsnowlabs.nlp.DocumentAssembler;
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
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;
import scala.collection.JavaConverters;
import scala.collection.Seq;

import java.io.*;
import java.lang.reflect.Field;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.*;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.stream.Collectors;

public class SparkNLPManager {
    SparkSession spark;
    int models;
    HashMap<String, LightPipeline> pipelines = new HashMap<>();

    private static final Logger logger = Logger.getLogger(SparkNLPManager.class.getName());

    public SparkNLPManager() {
        try {
            this._setEnvVars();
        } catch (Exception e) {
            logger.warning("Unable to set Env Vars. Error: " + e.getMessage());
        }
        this.spark = SparkSession.builder().
        appName("Spark NLP").
        master("local[*]").
        config("spark.driver.memory","16G").
        config("spark.kryoserializer.buffer.max", "2000M").
        config("spark.jars", Utils.JAR_PATH).
        getOrCreate();

        if (Utils.isFloatingLicense) {
            com.johnsnowlabs.util.start.registerListenerAndStartRefresh();
        }
    }

    public void loadPipelines(int numModels) {
        this._load_pipelines(numModels);
    }

    private void _setEnvVars() throws Exception {
        HashMap<String,String> newvars = new HashMap<String, String>() {{
            if (!Utils.isFloatingLicense) {
                put("AWS_ACCESS_KEY_ID", Utils.AWS_ACCESS_KEY_ID);
                put("AWS_SECRET_ACCESS_KEY",Utils.AWS_SECRET_ACCESS_KEY);
            }
                put("SPARK_NLP_LICENSE",Utils.SPARK_NLP_LICENSE);
                put("SECRET", Utils.SECRET);
                put("JSL_VERSION", Utils.JSL_VERSION);
                put("PUBLIC_VERSION", Utils.PUBLIC_VERSION);
        }};
        this._setEnv(newvars);
        System.out.println("AWS_ACCESS_KEY_ID: " + System.getenv("AWS_ACCESS_KEY_ID"));
        System.out.println("AWS_SECRET_ACCESS_KEY: " + System.getenv("AWS_SECRET_ACCESS_KEY"));
        System.out.println("SPARK_NLP_LICENSE: " + System.getenv("SPARK_NLP_LICENSE"));
        System.out.println("SECRET: " + System.getenv("SECRET"));
        System.out.println("JSL_VERSION: " + System.getenv("JSL_VERSION"));
        System.out.println("PUBLIC_VERSION: " + System.getenv("PUBLIC_VERSION"));
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
    private void _load_pipelines(int numModels) {
        // I do first one call for the initial latency
        long start = System.currentTimeMillis();
        int size = this._load_classification_pipeline(numModels);
        long end = System.currentTimeMillis();
        float sec = (end - start) / 1000F;
        logger.warning(String.format("\n--Initial Server for pipeline with %s components: %s", size, sec));
    }

    private int _load_classification_pipeline(int numModels) {
        List<String> models = this._get_legal_clf();
        //logger.info("Found models:" + models.size());
        models = models.subList(0, numModels);
        //logger.info("Used models:" + models.size());

        DocumentAssembler documentassembler = new DocumentAssembler();
        documentassembler.setInputCol("clause_text");
        documentassembler.setOutputCol("document");

        AnnotatorModel<BertSentenceEmbeddings> embedding = BertSentenceEmbeddings.pretrained("sent_bert_base_cased", "en");
        embedding.setInputCols(new String[]{"document"});
        embedding.setOutputCol("sentence_embeddings");

        PipelineStage[] arr = new PipelineStage[numModels + 2];
        arr[0] = documentassembler;
        arr[1] = embedding;
        int i = 2;
        for(String name: models) {
            AnnotatorModel<ClassifierDLModel> m = LegalClassifierDLModel.pretrained(name, "en", "legal/models");
            m.setInputCols(new String[]{"sentence_embeddings"});
            m.setOutputCol("is_" + name);
            arr[i] = m;
            i++;
        }
        Pipeline pipeline = new Pipeline().setStages(arr);

        // code
        StructType structType = new StructType();
        structType = structType.add("text", DataTypes.StringType, false);

        List<Row> nums = new ArrayList<Row>();
        nums.add(RowFactory.create(""));

        Dataset<Row> df = spark.createDataFrame(nums, structType);

        PipelineModel fit_model = pipeline.fit(df);
        LightPipeline lightpipeline = new LightPipeline(fit_model, false);
        this.pipelines.put("clf", lightpipeline);

        return pipeline.getStages().length;
    }
    public List<String>     _get_legal_clf() {
        Gson gson = new Gson();

        // 1. JSON file to Java object
        BufferedReader bf = this._getFileFromResourceAsStream("models.json");
        ArrayList<LinkedTreeMap<String,String>> object = (ArrayList<LinkedTreeMap<String,String>>) gson.fromJson(bf, Object.class);
        return object.stream()
                .filter(elem -> elem.get("name").startsWith("legclf") && elem.get("name").contains("clause"))
                .map(elem -> elem.get("name"))
                .collect(Collectors.toList());
    }

    // get a file from the resources folder
    // works everywhere, IDEA, unit test and JAR file.
    private BufferedReader _getFileFromResourceAsStream(String fileName) {

        // The class loader that loaded the class
        ClassLoader classLoader = getClass().getClassLoader();
        URL resource = classLoader.getResource(fileName);
        File file;
        try {
            file = new File(Objects.requireNonNull(resource).toURI());
        } catch (URISyntaxException e) {
            throw new RuntimeException(e);
        }
        FileInputStream fileStream;
        try {
            fileStream = new FileInputStream(file);
        } catch (FileNotFoundException e) {
            throw new RuntimeException(e);
        }
        //return fileStream;
        return new BufferedReader(new InputStreamReader(fileStream));
    }

    public String clf(String text) {
        scala.collection.immutable.Map<String, Seq<String>>[] result =  this.pipelines.get("clf").annotate(new String[]{text});
        return this._return_json(result);
    }

    private String _return_json(scala.collection.immutable.Map<String, Seq<String>>[] result) {
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
                String res;
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
