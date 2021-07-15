## Spark-NLP for Healthcare in AWS EMR

In this page we explain how to setup Spark-NLP + Spark-NLP Healthcare in AWS EMR, using the AWS console.

### Steps
1. You must go to the blue button "Create Cluster" on the UI. By doing that you will get directed to the "Create Cluster - Quick Options" page. Don't use the quick options, click on "Go to advanced options" instead.
2. Now in Advanced Options, on Step 1, "Software and Steps", please pick the following selection in the checkboxes,
![software config](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/platforms/emr/software_configs.png?raw=true)
Also in the "Edit Software Settings" page, enter the following,

```
[{
  "Classification": "spark-env",
  "Configurations": [{
    "Classification": "export",
    "Properties": {
      "PYSPARK_PYTHON": "/usr/bin/python3",
      "AWS_ACCESS_KEY_ID": "XYXYXYXYXYXYXYXYXYXY",
      "AWS_SECRET_ACCESS_KEY": "XYXYXYXYXYXYXYXYXYXY", 
      "SPARK_NLP_LICENSE": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY"
    }
  }]
},
{
  "Classification": "spark-defaults",
    "Properties": {
      "spark.yarn.stagingDir": "hdfs:///tmp",
      "spark.yarn.preserve.staging.files": "true",
      "spark.kryoserializer.buffer.max": "2000M",
      "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
      "spark.driver.maxResultSize": "0",
      "spark.driver.memory": "32G"
    }
}]
```
