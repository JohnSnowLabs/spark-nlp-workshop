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
Make sure that you replace all the secret information(marked here as XYXYXYXYXY) by the appropriate values that you received with your license.<br/>
3. In "Step 2" choose the hardware and networking configuration you prefer, or just pick the defaults. Move to next step by clocking the "Next" blue button.<br/>
4. Now you are in "Step 3", in which you assign a name to your cluster, and you can change the location of the cluster logs. If the location of the logs is OK for you, take note of the path so you can debug potential problems by using the logs.<br/>
5. Still on "Step 3", go to the bottom of the page, and expand the "Bootstrap Actions" tab. We're gonna add an action to execute during bootstrap of the cluster. Select "Custom Action", then press on "Configure and add".<br/>
You need to provide a path to a script on S3. The path needs to be public. Keep this in mind, no secret information can be contained there.<br/>
The script we'll used for this setup is `emr_bootstrap.sh` contained in the same folder this tutorial is located.<br/>
This script will install Spark-NLP 3.1.0, and Spark-NLP Healthcare 3.1.1. You'll have to edit the script if you need different versions.<br/>
After you entered the route to S3 in which you place the `emr_bootstrap.sh` file, and before clicking "add" in the dialog box, you must pass an additional parameter containing the SECRET value you received with your license. Just paste the secret on the "Optional arguments" field in that dialog box.<br/>
6. There's not much additional setup you need to perform. So just start a notebook server, connect it to the cluster you just created(be patient, it takes a while), and test with the `NLP_EMR_Setup.ipynb` that we provide in this folder.<br/>
