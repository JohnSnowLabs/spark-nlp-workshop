## Airgapped Deployment of Spark-NLP for Healthcare on AWS EMR

### Overview

This page explains how to set up **Spark NLP** and **Spark NLP for Healthcare** on **AWS EMR** using the AWS Console, specifically for **air-gapped environments**.

The configuration is preconfigured and ready to use with **EMR Notebooks**.

### Steps
#### 1- Go to EMR service

![alt text](image-1.png)

#### 2- Click `create cluster` button, then select required applications:
Please select Amazon EMR 7.x release version to use spark-nlp. In lower EMR versions, ONNX base models do not work due to system requirements.
Discussion: https://github.com/JohnSnowLabs/spark-nlp/issues/14193
![alt text](image.png)


#### 3-  Select EC2 instances for master and worker nodes:

![alt text](image-2.png)

#### 4 - Specify the number of workers:

![alt text](image-3.png)

#### 5- Specify the VPC and Security Groups (Firewall)
It is recommended to use default configuration or have AWS create default configurations.

![alt text](image-4.png)


#### 6- Add bootstrap action:
We will have Johnsnowlabs Spark libraries installed via bootstrap action.

Go to the bottom of the page, and expand the `Bootstrap Actions` tab. Press on `Add` button. You need to provide a path to a script on S3.

![5](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/05c3931c-16f7-47ad-b135-2612e85b3de4)


The script we'll use for this setup is `emr_bootstrap.sh` which is contained in this folder.


You need to put your credentials into `emr_bootstrap.sh` file <br/>

#### 7. We will define spark parameters under Software settings tab:
Please investigate official documentation for more information about EMR Spark configuration
https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-spark-configure.html


```
[
  {
    "Classification": "spark",
    "Properties": {
      "maximizeResourceAllocation": "true"
    }
  },
  {
    "Classification": "spark-env",
    "Configurations": [
      {
        "Classification": "export",
        "Properties": {
          "JSL_EMR": "1",
          "PYSPARK_PYTHON": "/usr/bin/python3",
          "SPARK_NLP_LICENSE": "XYXYXYXYXY"
        }
      }
    ],
    "Properties": {}
  },
  {
    "Classification": "yarn-env",
    "Configurations": [
      {
        "Classification": "export",
        "Properties": {
          "JSL_EMR": "1",
          "SPARK_NLP_LICENSE": "XYXYXYXYXY"
        }
      }
    ],
    "Properties": {}
  },
  {
    "Classification": "spark-defaults",
    "Properties": {
      "spark.driver.maxResultSize": "0",
      "spark.dynamicAllocation.enabled": "true",
      "spark.executorEnv.SPARK_NLP_LICENSE": "XYXYXYXYXY",
      "spark.jsl.settings.aws.credentials.access_key_id": "XYXYXYXYXY",
      "spark.jsl.settings.aws.credentials.secret_access_key": "XYXYXYXYXY",
      "spark.jsl.settings.aws.region": "us-east-1",
      "spark.jsl.settings.pretrained.credentials.access_key_id": "XYXYXYXYXY",
      "spark.jsl.settings.pretrained.credentials.secret_access_key": "XYXYXYXYXY",
      "spark.kryoserializer.buffer.max": "2000M",
      "spark.rpc.message.maxSize": "1024",
      "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
      "spark.yarn.appMasterEnv.SPARK_NLP_LICENSE": "XYXYXYXYXY",
      "spark.yarn.preserve.staging.files": "true",
      "spark.jsl.settings.storage.cluster_tmp_dir": "hdfs:///tmp",
      "spark.yarn.stagingDir": "hdfs:///tmp"
    }
  }
]
```
**__Important__**  
Make sure to replace all placeholder values (marked as `XYXYXYXYXY`) with the actual credentials provided with your license.  
If your EMR cluster is truly **air-gapped**, you do **not** need to specify `access_key_id` or `secret_access_key` in the configuration — since the `pretrained()` function cannot be used to download models in an offline environment.

---

**Automatic Resource Allocation**  
We do not manually configure driver or executor memory settings. Instead, we enable the `maximizeResourceAllocation` feature, which allows EMR to automatically assign the maximum available resources to Spark.

If you are having issues with the license, please contact JSL team at support@johnsnowlabs.com

---

Under **Tags** section, please add a `KEY: VALUE` pair with `for-use-with-amazon-emr-managed-policies` `true`

![6](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/0f03d691-1681-4c94-a6f0-7a62ec4605f2)


#### 8 - Security
After selecting a `EC2 key pair` - to connect the master node with `SSH` and select the IAM roles, we can click on the orange `Create Cluster` button and a Cluster will be created.

#### 9 -
Make sure that you should use airgapped license type 

#### 10 - Start Notebooks Server

To open the Notebooks, you can create Workspaces from EMR Studio and attach the Cluster that you just created.

#### 11 - Any Doubt?
Write us to support@johnsnowlabs.com
