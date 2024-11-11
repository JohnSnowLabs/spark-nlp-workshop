# Spark-NLP Databricks

## Databricks Scala Notebooks

You can view all the Databricks notebooks from this address in HTML format:

[https://johnsnowlabs.github.io/spark-nlp-workshop/databricks/index.html](https://johnsnowlabs.github.io/spark-nlp-workshop/databricks/index.html)

Note: You can import these notebooks by using their URLs.

## How to use Spark-NLP library in Databricks

1- Right-click the Workspace folder where you want to store the library.

2- Select Create > Library.

3- Select where you would like to create the library in the Workspace, and open the Create Library dialog:

![Databricks](https://databricks.com/wp-content/uploads/2015/07/create-lib.png)

4- From the Source drop-down menu, select **Maven Coordinate:**
![Databricks](https://databricks.com/wp-content/uploads/2015/07/select-maven-1024x711.png)

5- Now, all available **Maven** are at your fingertips! Just search for **com.johnsnowlabs.nlp:spark-nlp_2.12: 3.X.X**

6- Select **spark-nlp** package and we are good to go!

More info about how to use 3rd [Party Libraries in Databricks](https://databricks.com/blog/2015/07/28/using-3rd-party-libraries-in-databricks-apache-spark-packages-and-maven-libraries.html)

## Compatibility

Spark NLP 3.1.0 has been tested and is compatible with the following runtimes:

- 5.5 LTS
- 5.5 LTS ML & GPU
- 6.4
- 6.4 ML & GPU
- 7.3
- 7.3 ML & GPU
- 7.4
- 7.4 ML & GPU
- 7.5
- 7.5 ML & GPU
- 7.6
- 7.6 ML & GPU
- 8.0
- 8.0 ML
- 8.1
- 8.1 ML & GPU
- 8.2
- 8.2 ML & GPU
- 8.3
- 8.3 ML & GPU

## Getting the keys and installation

1. In order to get trial keys for Spark NLP for Healthcare
, fill the form at https://www.johnsnowlabs.com/spark-nlp-try-free/ and you will get your keys to your email in a few minutes.

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

    `$ aws s3 cp --region us-east-2 s3://pypi.johnsnowlabs.com/$jsl_secret/spark-nlp-jsl-$jsl_version.jar spark-nlp-jsl-$jsl_version.jar`

    `$ aws s3 cp --region us-east-2 s3://pypi.johnsnowlabs.com/$jsl_secret/spark-nlp-jsl/spark_nlp_jsl-$jsl_version-py3-none-any.whl spark_nlp_jsl-$jsl_version-py3-none-any.whl` 

4. In `Libraries` tab inside your cluster:

 - Install New -> PyPI -> `spark-nlp==$public_version` -> Install
 - Install New -> Maven -> Coordinates -> `com.johnsnowlabs.nlp:spark-nlp_2.12:$public_version` -> Install

 - add following jars for the Healthcare library that you downloaded above:
        - Install New -> Python Whl -> upload `spark_nlp_jsl-$jsl_version-py3-none-any.whl`

        - Install New -> Jar -> upload `spark-nlp-jsl-$jsl_version.jar`

5. Now you can attach your notebook to the cluster and use Spark NLP!

For more information, see 

  https://nlp.johnsnowlabs.com/docs/en/install#databricks-support

  https://nlp.johnsnowlabs.com/docs/en/licensed_install#install-spark-nlp-for-healthcare-on-databricks
  

In order to get more detailed examples, please check this repository : https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/tutorials/Certification_Trainings/Healthcare/databricks_notebooks
