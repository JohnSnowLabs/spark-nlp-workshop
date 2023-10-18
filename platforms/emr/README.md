### Spark-NLP for Healthcare in AWS EMR

In this page, we explain how to setup Spark-NLP + Spark-NLP Healthcare in AWS EMR, using the AWS console. Also, You can create an EMR cluster automatically, you should follow [`this tutorial`](https://github.com/JohnSnowLabs/johnsnowlabs/blob/main/notebooks/create_emr_cluster.ipynb) to create EMR cluster automatically.

You can find example healthcare notebooks for EMR clusters in [`this folder`](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/products/emr/healthcare)

This configuration is already ready-to-use for **EMR Notebooks**.

### Steps
## 1. Software

You must go to "EMR" on the UI. By doing that you will get directed to the "Create Cluster" page and click on the orange Create Cluster button. Choose the EMR release as 6.5.0 and please pick the following selection in the checkboxes.

![1](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/e495e6ba-d519-464c-a08f-8d350a15354c)


## 2. Hardware
Please choose the hardware and networking configuration you prefer, or just pick the defaults.

**Important:** Keep in mind that there should be only one master node if you want to use EMR Notebooks. However, the cluster can be scaled with additional slave nodes - which can be modified under `Cluster Nodes and Instances` section.

![2](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/357544ca-19a9-46d4-8099-c0ae65882d27)


Please set EBS Volume to `50 GiB to 100 GiB` and move to the next step by clicking the "Next" blue button.<br/>

![3](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/45b2287e-6aa6-413d-ad59-85ac7d19d75f)



## 3. General Cluster Settings


In this part, we will make the necessary configurations of cluster settings. We're gonna add a script to be automatically executed after the cluster is created. This script will make changes on user's part and download some packages. We can click on the add button of `Steps` and upload the `initialization_script.sh` from your s3 bucket. `initialization_script.sh` script can be found in this folder and you can upload it to your s3 bucket.

![4](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/b4c4ca6d-120e-411c-b0bf-cd71c33dbfdf)


Go to the bottom of the page, and expand the `Bootstrap Actions` tab. We're gonna add an action to execute during the bootstrap of the cluster. Press on `Add` button. You need to provide a path to a script on S3.

![5](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/05c3931c-16f7-47ad-b135-2612e85b3de4)


The script we'll use for this setup is `jsl_emr_bootstrap2.sh` which is contained in this folder.


You need to make a change in the script and add your license key to the med_license parameter in line 13 of the script. <br/>


This script will install johnsnowlabs 5.0.2, you can edit the script if you need different versions.<br/>



Also, expand the `Software Settings` tab, and enter the following for configurations:

```
[
  {
    "Classification": "spark-env",
    "Configurations": [
      {
        "Classification": "export",
        "Properties": {
          "JSL_EMR": "1",
          "PYSPARK_PYTHON": "/usr/bin/python3",
          "SPARK_NLP_LICENSE": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY"
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
          "SPARK_NLP_LICENSE": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY"
        }
      }
    ],
    "Properties": {}
  },
  {
    "Classification": "spark-defaults",
    "Properties": {
      "spark.driver.maxResultSize": "0",
      "spark.driver.memory": "32G",
      "spark.jsl.settings.aws.region": "us-east-1",
      "spark.jsl.settings.pretrained.credentials.access_key_id": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY",
      "spark.jsl.settings.pretrained.credentials.secret_access_key": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY",
      "spark.yarn.appMasterEnv.SPARK_NLP_LICENSE": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY",
      "spark.executorEnv.SPARK_NLP_LICENSE": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY",
      "spark.kryoserializer.buffer.max": "2000M",
      "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
      "spark.yarn.preserve.staging.files": "true",
      "spark.yarn.stagingDir": "hdfs:///tmp"
    }
  }
]
```
**__Important__**:
Make sure that you replace all the secret information(marked here as XYXYXYXYXY) with the appropriate values that you received with your license.<br/> 

If you are having issues with the license, please contact JSL team at support@johnsnowlabs.com


Under **Tags** section, please add a `KEY: VALUE` pair with `for-use-with-amazon-emr-managed-policies` `true`

![6](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/0f03d691-1681-4c94-a6f0-7a62ec4605f2)


## 4. Security
After selecting a `EC2 key pair` - to connect the master node with `SSH` and select the IAM roles, we can click on the orange `Create Cluster` button and a Cluster will be created.

## 5.
Make sure that license.johnsnowlabs.com and licensecheck.johnsnowlabs.com are on whitelist domains. If they are not, please whitelist these domains.

## 6. Start Notebooks Server

To open the Notebooks, you can create Workspaces from EMR Studio and attach the Cluster that you just created.

## 7. Any Doubt?
Write us to support@johnsnowlabs.com
