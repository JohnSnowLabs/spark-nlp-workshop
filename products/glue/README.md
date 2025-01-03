### Spark-NLP for Healthcare in AWS Glue

On this page, we explain how to start a Glue session with Spark-NLP + Spark-NLP Healthcare in AWS Glue UI. This configuration is already ready-to-use for **Glue Notebooks**.

### Steps
## 1. Create Notebook

You must go to "Notebooks" section of AWS Glue on the UI. You need to click on Jupyter Notebook and upload existing notebooks or create new notebook. Once we choose, we can continue by clicking "Create" button.

![Screen Shot 2023-09-25 at 7 51 01 PM](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/5376beba-e8c6-4f3b-9a92-397ad21ea4a6)


Please give a job name and choose the IAM role. The chosen IAM role has to have access to s3 buckets.

Once we start the notebook, We need to make a configuration on the Glue session that will be started. We can make these configurations by using Glue interactive session magics.

![Screen Shot 2023-09-25 at 7 52 52 PM](https://github.com/JohnSnowLabs/spark-nlp-workshop/assets/72014272/a69c52e1-681e-405a-b650-9bd054a3d5d3)


## 2. Start Session

Once we start the notebook, We need to configure the Glue session that will be started. we can make these configurations by using Glue interactive session magics.


In the first cell of the notebook, enter the following for configurations:

```
%additional_python_modules tensorflow==2.11.0, tensorflow-addons, scikit-learn, johnsnowlabs==5.5.2, s3://<your_bucket_name>/assets/packages/spark_nlp-5.5.1-py2.py3-none-any.whl,s3://<your_bucket_name>/assets/packages/spark_nlp_jsl-5.5.1-py3-none-any.whl
%extra_jars s3://<your_bucket_name>/assets/jars/spark-nlp-assembly-5.5.1.jar,s3://<your_bucket_name>/assets/jars/spark-nlp-jsl-5.5.1.jar

%%configure
{
"--conf":"""spark.jsl.settings.pretrained.cache_folder=s3://<your_bucket_name>/cache_pretrained/
--conf spark.jars.packages=org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk:1.12.500
--conf spark.driver.memory=64G
--conf spark.executor.memory=32G
--conf spark.serializer=org.apache.spark.serializer.KryoSerializer
--conf spark.kryoserializer.buffer.max=2000M
--conf spark.driver.maxResultSize=2000M
--conf spark.yarn.am.memory=4G
--conf spark.hadoop.mapred.output.committer.class=org.apache.hadoop.mapred.DirectFileOutputCommitter
--conf spark.hadoop.fs.s3a.access.key=<aws_access_key>
--conf spark.hadoop.fs.s3a.secret.key=<aws_secret_key>
--conf spark.hadoop.fs.s3a.session.token=<aws_session_token>
--conf jsl.settings.license=<jsl_license>
--conf spark.jsl.settings.pretrained.credentials.access_key_id=<pretrained.credentials.access_key_id>
--conf spark.jsl.settings.pretrained.credentials.secret_access_key=<pretrained.credentials.secret_access_key>
--conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider
--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem
--conf spark.hadoop.fs.s3a.path.style.access=true
--conf spark.extraListeners=com.johnsnowlabs.license.LicenseLifeCycleManager
--conf spark.hadoop.fs.s3.canned.acl=BucketOwnerFullControl
--conf spark.hadoop.fs.s3a.endpoint=s3.us-east-1.amazonaws.com
--conf spark.hadoop.fs.defaultFS=s3a://aws-bundle-s3
--conf spark.jsl.settings.aws.region=us-east-1"""
}
```
**__Important__**:
You need to install the johnsnowlabs jars, .whl files and upload them to your s3 bucket.

Also, you need to enter the path of the bucket for spark.jsl.settings.pretrained.cache_folder.

Please create an s3 access key, secret key, and session token using AWS CLI. This is important to have access to the s3 bucket.

Make sure that you replace all the secret information (marked here as <jsl_license>, <pretrained.credentials.access_key_id>, <pretrained.credentials.secret_access_key> ) by the appropriate values that you received with your license.<br/> 

If you are having issues with the license, please contact JSL team at support@johnsnowlabs.com

Once you made changes to the configurations and run the first cell, you can start the `Glue Session` by running the following code in the second cell:

```
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
spark._jvm.com.johnsnowlabs.util.start.registerListenerAndStartRefresh()
job = Job(glueContext)
```

You can find the described configuration at the beginning of all example healthcare notebooks which is located in the healthcare folder of the repo.

## 3. Any Doubt?
Write us to support@johnsnowlabs.com
