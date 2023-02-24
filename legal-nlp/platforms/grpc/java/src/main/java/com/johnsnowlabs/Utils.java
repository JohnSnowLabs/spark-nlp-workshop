package com.johnsnowlabs;

import java.util.Collections;
import java.util.Random;

public class Utils {
    public static String JAR_PATH = "D:\\IdeaProjects\\grpc\\jars\\spark-nlp-jsl-4.2.1.jar";

    public static boolean isFloatingLicense = true;

    public static String AWS_ACCESS_KEY_ID = "";

    public static String AWS_SECRET_ACCESS_KEY = "";

    public static String SPARK_NLP_LICENSE = "";

    public static String SECRET = "4.2.2-8fde8ce2327dce2fb89db1742eec8ca121eee0de";

    public static String JSL_VERSION = "4.2.2";
    public static String PUBLIC_VERSION = "4.2.2";

    public static int NUM_WORKERS = 2;
    public static int RANGE_START = 8000;
    public static String PARAGRAPH = "Indemnification. 4.1.1 The Company agrees to indemnify, to the extent permitted by law, each Holder of Registrable Securities, its officers and directors and each person who controls such Holder (within the meaning of the Securities Act) against all losses, claims, damages, liabilities and expenses (including attorneys’ fees) caused by any untrue or alleged untrue statement of material fact contained in any Registration Statement, Prospectus or preliminary Prospectus or any amendment thereof or supplement thereto or any omission or alleged omission of a material fact required to be stated therein or necessary to make the statements therein not misleading, except insofar as the same are caused by or contained in any information furnished in writing to the Company by such Holder expressly for use therein. The Company shall indemnify the Underwriters, their officers and directors and each person who controls such Underwriters (within the meaning of the Securities Act) to the same extent as provided in the foregoing with respect to the indemnification of the Holder.";

    public static String DOCUMENT = String.join("\n", Collections.nCopies(25, PARAGRAPH));

    public static int CALLS = 10;

    public static int NUM_MODELS = 10;

    public static int INITIALIZATION_TIMEOUT = 99999;

    public static int INFERENCE_TIMEOUT = 99999;

    public static String newParagraph() {
        String result = PARAGRAPH;
        String[] array = result.split(" ");
        for (int i=0;i<5;i++) {
            int rnd = new Random().nextInt(array.length);
            result = result.replace(array[rnd], "<MASK>");
        }
        return result;
    }


}
