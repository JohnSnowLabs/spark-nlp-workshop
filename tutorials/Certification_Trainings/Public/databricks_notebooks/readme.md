
Databricks Public notebooks have been updated to Spark NLP release v3.0.2 (28.04.2021)

Before running these notebooks in your Databricks cluster, please make sure that you setup your cluster according to instructions here:


## Getting the keys and installation

1. In order to get trial keys for Spark NLP for Healthcare
, fill the form at https://www.johnsnowlabs.com/spark-nlp-try-free/ and you will get your keys to your email in a few minutes.

2. On a new cluster or existing one

  - add the following to the `Advanced Options -> Spark` tab, in `Spark.Config` box:

    ```bash
    spark.local.dir /var
    spark.kryoserializer.buffer.max 1000M
    spark.serializer org.apache.spark.serializer.KryoSerializer
    ```
  - add the following to the `Advanced Options -> Spark` tab, in `Environment Variables` box:

    ```bash
    AWS_ACCESS_KEY_ID=xxx
    AWS_SECRET_ACCESS_KEY=yyy
    SPARK_NLP_LICENSE=zzz
    ```

3. Download the followings with AWS CLI to your local computer

    `$ aws s3 cp --region us-east-2 s3://pypi.johnsnowlabs.com/$jsl_secret/spark-nlp-jsl-3.0.2.jar spark-nlp-jsl-3.0.2.jar`

    `$ aws s3 cp --region us-east-2 s3://pypi.johnsnowlabs.com/$jsl_secret/spark-nlp-jsl/spark_nlp_jsl-3.0.2-py3-none-any.whl spark_nlp_jsl-3.0.2-py3-none-any.whl`

4. In `Libraries` tab inside your cluster:

 - Install New -> PyPI -> `spark-nlp==3.0.2` -> Install
 - Install New -> Maven -> Coordinates -> `com.johnsnowlabs.nlp:spark-nlp_2.12:3.0.2` -> Install

 - add following jars for the Healthcare library that you downloaded above:
        - Install New -> Python Whl -> upload `spark_nlp_jsl-3.0.2-py3-none-any.whl`

        - Install New -> Jar -> upload `spark-nlp-jsl-3.0.2.jar`

5. Now you can attach your notebook to the cluster and use Spark NLP!

For more information, see 

  https://nlp.johnsnowlabs.com/docs/en/install#databricks-support

  https://nlp.johnsnowlabs.com/docs/en/licensed_install#install-spark-nlp-for-healthcare-on-databricks
  
The follwing notebook is prepared and tested on **r2.2xlarge at 8.0 (includes Apache Spark 3.1.1, Scala 2.12)** on Databricks
