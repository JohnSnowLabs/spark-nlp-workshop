# Deploy Spark Healthcare NLP on GCP Dataproc (Serverless way)

A detailed, step-by-step guide (with screenshots) to set up and run Healthcare NLP using Google Cloud Dataproc (Serverless way).

---


## Prerequisites

- **Google Cloud Project** with billing enabled.
- Enabled APIs (you may need to enable others):
  - Dataproc API
  - Cloud Storage API
  - Compute Engine API
- **Permissions** to manage buckets, clusters, and submit jobs. (You may need other permissions).
- Downloaded:
  - Spark NLP assembly & JSL JARs
  - Spark NLP & JSL wheel files
  - Pipeline code
  - Healthcare Model(s)

---

## Step 1: Create a new GCS 

Create a bew bucket from Cloud Storage Service (e.g., `spark-healthcare-nlp-serverless`).

![Creation of GCS](step1.png)

---

## Step 2: Uploading resources to the GCS

Organize your bucket by creating subfolders for jars, whls, and models, then upload the corresponding resources.


![GCS resources](step2.png)
![GCS resources](step2.2.png)

Upload also the py pipeline code to the root of the bucket.

The bucket should looks like showing in the following figure:

![GCS resources](step3.png)

---

## Step 3: Dataproc service

Search for dataproc in the Google Cloud Console to find the Dataproc service.


![Dataproc service](step4.png)

---


## Step 4: Submit Your Spark NLP Batch on serverless mode

Click on the Cloud Shell (top-right) to start a shell session:

![Starting a cloud shell session](step5.png)

Then submit your pipeline in serverless mode using the following command in Cloud Shell:

```bash
gcloud dataproc batches submit pyspark gs://spark-healthcare-nlp-serverless/spark_healthcare_nlp_serverless.py   --project=docusign-251217   --region=us-central1   --batch=jsl-batch   --jars=gs://spark-healthcare-nlp-serverless/jars/spark-nlp-assembly-6.0.0.jar,gs://spark-healthcare-nlp-serverless/jars/spark-nlp-jsl-6.0.0.jar   --py-files=gs://spark-healthcare-nlp-serverless/whls/spark_nlp-6.0.0-py2.py3-none-any.whl,gs://spark-healthcare-nlp-serverless/whls/spark_nlp_jsl-6.0.0-py3-none-any.whl   --properties="spark.serializer=org.apache.spark.serializer.KryoSerializer,\
spark.kryoserializer.buffer.max=2000M,\
spark.driver.extraJavaOptions=-Djsl.settings.license=<YOUR_LICENSE>,\
spark.executor.extraJavaOptions=-Djsl.settings.license=<YOUR_LICENSE>,\
--version=1.1
```
Please make sure to replace <YOUR_LICENSE> with your valide JSL license.		

![Step 4 - Submit Your Spark NLP Batch](step6.png)

---

## Step 5: Track Batch Progress

Monitor the Batch execution in the Dataproc Serverless Barches tab and in Cloud Shell logs.  
You can see the batch’s status (e.g., Running) and logs being printed in real-time.

![Step 5 - Track Batch Progress](step7.png)

---

## Step 6: View Results and Batch Completion

As the pipeline runs, logs and output will be displayed in the terminal.  
Once the Batch finishes, you’ll see confirmation of successful completion and model results.

![Step 6 - View Results and Batch Completion](step7.2.png)

---

## Step 7: Batch Succeeded - Check Outputs

When the batch is finished, the status in the Batch list changes to **Succeeded**.  
Check the logs and outputs to validate your Healthcare NLP job ran correctly.

![Step 7 - Job Succeeded - Check Outputs](step7.3.png)

---

