### Spark-NLP for Healthcare in AWS EMR

In this page we explain how to setup Spark-NLP + Spark-NLP Healthcare in AWS EMR, using the AWS console. This configuration is already ready-to-use for **EMR Notebooks**.

### Steps
## 1. Software

You must go to "EMR" on the UI. By doing that you will get directed to the "Create Cluster" page and click on orange Create Cluster button. Choose the EMR release as 6.5.0 and please pick the following selection in the checkboxes.



## 2. Hardware
Please choose the hardware and networking configuration you prefer, or just pick the defaults.

**Important:** Keep in mind that there should be only one master node if you want to use EMR Notebooks. However, cluster can be scaled with additional slave nodes - which can be modified under `Cluster Nodes and Instances` section.


Please set EBS Volume to `50 GiB to 100 GiB` and move to next step by clicking the "Next" blue button.<br/>




## 3. General Cluster Settings


In this part, we will make the necessary configurations of cluster settings. We're gonna add an script to be automatically executed after cluster created. This script will make changes on users part and download the some packages. We can click on add button of `Steps` and upload the `initialization_script.sh` from your s3 bucket. `initialization_script.sh` script can be found this folder and you can upload to your s3 bucket.


Go to the bottom of the page, and expand the `Bootstrap Actions` tab. We're gonna add an action to execute during bootstrap of the cluster. Press on `Add` button. You need to provide a path to a script on S3.


The script we'll used for this setup is `jsl_emr_bootstrap2.sh` which contained in this folder.


You need make change in the script and add your license key to med_license parameter in line 13 of the script. <br/>


This script will install johnsnowlabs 5.0.2, you can edit the script if you need different versions.<br/>



Also, expand the `Software Settings` tab, enter the following for configurations:

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
    "Classification": "spark-defaults",
    "Properties": {
      "spark.driver.maxResultSize": "0",
      "spark.driver.memory": "32G",
      "spark.jsl.settings.aws.region": "us-east-1",
      "spark.jsl.settings.pretrained.credentials.access_key_id": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY",
      "spark.jsl.settings.pretrained.credentials.secret_access_key": "XYXYXYXYXYXYXYXYXYXYXYXYXYXY",
      "spark.kryoserializer.buffer.max": "2000M",
      "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
      "spark.yarn.preserve.staging.files": "true",
      "spark.yarn.stagingDir": "hdfs:///tmp"
    }
  }
]
```
**__Important__**:
Make sure that you replace all the secret information(marked here as XYXYXYXYXY) by the appropriate values that you received with your license.<br/> 

If you are having issues with the license, please contact JSL team at support@johnsnowlabs.com


Under **Tags** section, please add a `KEY: VALUE` pair with `for-use-with-amazon-emr-managed-policies` `true`



## 4. Security
After selecting a `EC2 key pair` - to connect the master node with `SSH` and select the IAM roles, we can click on the orange `Create Cluster` button and Cluster will be created.

## 5. Start Notebooks Server

To open the Notebooks, you can create Workspaces from EMR Studio and attach the Cluster that you just created.

## 6. Any Doubt?
Write us to support@johnsnowlabs.com
