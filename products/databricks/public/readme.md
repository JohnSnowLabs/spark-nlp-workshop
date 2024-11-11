
Databricks Public notebooks have been updated to Spark NLP release v3.0.2 (28.04.2021)

Before running these notebooks in your Databricks cluster, please make sure that you setup your cluster according to instructions here:


## Automatic deployment of John Snow Labs NLP on Databricks

1. In order to get trial keys for Spark NLP for Healthcare, fill in the form available at https://www.johnsnowlabs.com/databricks/ using your company e-mail and your databricks instance details. 

2. You will receive an e-mail for validating the provided e-mail address. Please click on the validation button. 

3.a.  If you have a *Community Edition* Databricks instance, you will get a second email in a few minutes with a deployment script. Upload the script to your databricks workspace, attach it to a running cluster and run it for a frictionless installation of John Snow Labs NLP libraries. The deployment script will also install the TRIAL license key on your cluster. 

3.b. If you have an *Standard* or above Databricks subscriptions, John Snow Labs NLP libraries will be installed automatically on the cluster of your choice. 

You are ready to go!


## Manual deployment of John Snow Labs NLP on Databricks

1. In order to get trial keys for Spark NLP for Healthcare, fill the form at https://www.johnsnowlabs.com/spark-nlp-try-free/ and you will get your keys to your email in a few minutes.

2. On a new cluster or existing one

  - add the following to the `Advanced Options -> Spark` tab, in `Spark.Config` box:

    ```bash
    spark.local.dir /var
    spark.kryoserializer.buffer.max 1000M
    spark.serializer org.apache.spark.serializer.KryoSerializer
    spark.driver.extraJavaOptions -Dspark.jsl.settings.pretrained.credentials.secret_access_key=xxx -Dspark.jsl.settings.pretrained.credentials.access_key_id=yyy

    ```
  - add the following to the `Advanced Options -> Spark` tab, in `Environment Variables` box:

    ```bash
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

