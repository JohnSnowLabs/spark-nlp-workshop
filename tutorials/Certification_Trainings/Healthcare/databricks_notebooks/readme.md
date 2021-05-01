
Databricks Spark NLP Healthcare notebooks have been updated to latest release v2.7.0 (03.11.2020)

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

    `$ aws s3 cp --region us-east-2 s3://pypi.johnsnowlabs.com/$jsl_secret/spark-nlp-jsl-2.7.0.jar spark-nlp-jsl-2.7.0.jar`

    `$ aws s3 cp --region us-east-2 s3://pypi.johnsnowlabs.com/$jsl_secret/spark-nlp-jsl/spark_nlp_jsl-2.7.0-py3-none-any.whl spark_nlp_jsl-2.7.0-py3-none-any.whl`

4. In `Libraries` tab inside your cluster:

 - Install New -> PyPI -> `spark-nlp==2.6.5` -> Install
 - Install New -> Maven -> Coordinates -> `com.johnsnowlabs.nlp:spark-nlp_2.11:2.6.5` -> Install

 - add following jars:
        - Install New -> Python Whl -> upload `spark_nlp_jsl-2.7.0-py3-none-any.whl`

        - Install New -> Jar -> upload `spark-nlp-jsl-2.7.0.jar`

5. Now you can attach your notebook to the cluster and use Spark NLP!

For more information, see 

  https://nlp.johnsnowlabs.com/docs/en/install#databricks-support

  https://nlp.johnsnowlabs.com/docs/en/licensed_install#install-spark-nlp-for-healthcare-on-databricks
  
The follwing notebook is prepared and tested on **r2.2xlarge at 6.4 (includes Apache Spark 2.4.4, Scala 2.11)** on Databricks
