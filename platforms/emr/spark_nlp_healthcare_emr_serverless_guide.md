# Running Spark NLP and Healthcare NLP Jobs on Amazon EMR Serverless

## Scope

This guide explains how to set up **Spark NLP Healthcare/JSL** on **Amazon EMR Serverless** using a floating license. It is intended for customer environments and is AWS-account agnostic: replace the placeholders with your own AWS account, S3 bucket, IAM role, license, package secret, and model paths.

EMR Serverless is different from a regular EMR cluster: it does **not** run bootstrap actions. For Spark NLP Healthcare/JSL jobs, the Spark job must load all required runtime assets from S3, including:

- Spark NLP and Spark Healthcare NLP JAR files.
- A packed Python environment containing compatible `spark-nlp` and `spark-nlp-jsl` wheels.
- Healthcare model or pipeline artifacts.
- Optional pretrained/cache artifacts.

## 1. Target Architecture

A successful Spark NLP and Healthcare NLP EMR Serverless setup requires these components:

1. An **EMR Serverless Spark application** using an EMR release compatible with the Spark NLP/JSL versions you plan to run.
2. An **EMR Serverless job runtime role** with S3 permissions for scripts, JARs, Python environment archives, model artifacts, input data, output data, logs, and optional cache/checkpoint paths.
3. **Network egress** from the EMR Serverless application for floating license validation.
4. Compatible **Spark NLP assembly** and **Healthcare NLP** JAR files uploaded to S3.
5. A packed Python runtime archive containing compatible `spark-nlp` and `spark-nlp-jsl` Python packages.
6. A floating license passed securely to the driver and executors.
7. Correct S3A configuration for model loading and artifact access.
8. A model loading strategy: direct `s3a://` loading, archive-based local loading, or cache-based pretrained loading.

## 2. Version Alignment

Keep these versions aligned before submitting a job:

| Component | Requirement |
| --- | --- |
| EMR Serverless release | Must provide a Spark runtime compatible with your Spark NLP/JSL release. |
| Apache Spark / Scala | JAR coordinates and assembly artifacts must match the Spark/Scala runtime. Spark NLP 3.x+ deployments commonly use Scala 2.12 on Spark 3.x. |
| Spark NLP assembly JAR | Must match the `spark-nlp` Python package version. |
| Healthcare NLP JAR | Must match the `spark-nlp-jsl` Python package and licensed Healthcare model version. |
| Python version | Must match what you pack in the environment archive and what EMR Serverless can run. For EMR Serverless 7.x, Python 3.11 on Amazon Linux 2023 is a good baseline. |
| Healthcare model/pipeline | Should be compatible with the Healthcare NLP version. |

For example, for an EMR Serverless 7.x proof of concept, a common baseline is:

```text
EMR Serverless release: emr-7.x
Python: 3.11
Spark NLP: <spark-nlp-version>
Healthcare NLP: <spark-nlp-jsl-version>
Scala: 2.12
```

Do not mix arbitrary Spark NLP, Healthcare NLP, and model versions. If a model fails to load or deserialize, first validate version compatibility.

## 3. VPC and Outbound Connectivity

A floating license is designed for connected environments. The EMR Serverless runtime must be able to perform outbound license validation over HTTPS.

For private AWS networks, configure the EMR Serverless application with:

- VPC access enabled.
- Subnets that can reach an approved outbound path.
- Security groups allowing required outbound traffic.
- NAT gateway, proxy, firewall route, or other approved outbound network path.
- HTTPS egress allowed.

If the job can load the model but fails during inference with a timeout like the following, the issue is usually network/license validation, not S3 access:

```text
java.net.SocketTimeoutException: Connect timed out
com.johnsnowlabs.license.CheckBlockedLicense.isUserBlocked
com.johnsnowlabs.license.LicenseValidator.checkValidEnvironment
```

If your organization restricts outbound access, ask your network/security team to allow the license validation endpoints required by your John Snow Labs license. For license-related connectivity issues, contact `support@johnsnowlabs.com`.

## 4. Required S3 Artifacts

Create an S3 bucket or prefix that the EMR Serverless runtime role can read from. It should also be able to write logs, outputs, and optional cache files where needed.

Recommended layout:

```text
s3://<artifact-bucket>/spark-nlp-emr/
  scripts/
  envs/
  models/
  cache_pretrained/
  logs/
  output/

s3://<artifact-bucket>/jars/
```

Required artifacts:

```text
s3://<artifact-bucket>/jars/spark-nlp-assembly-<spark-nlp-version>.jar
s3://<artifact-bucket>/jars/spark-nlp-jsl-<spark-nlp-jsl-version>.jar
s3://<artifact-bucket>/spark-nlp-emr/envs/spark-nlp-hc-env.tar.gz
s3://<artifact-bucket>/spark-nlp-emr/scripts/<job-script>.py
s3://<artifact-bucket>/spark-nlp-emr/models/<model-or-pipeline-folder>/
```

For EMR Serverless, prefer `spark.jars` with S3 paths. Do not rely on Maven package resolution from the runtime unless you have explicitly validated outbound internet access and dependency resolution.

Upload the JAR files:

```bash
aws s3 cp spark-nlp-assembly-<spark-nlp-version>.jar \
  s3://<artifact-bucket>/jars/spark-nlp-assembly-<spark-nlp-version>.jar

aws s3 cp spark-nlp-jsl-<spark-nlp-jsl-version>.jar \
  s3://<artifact-bucket>/jars/spark-nlp-jsl-<spark-nlp-jsl-version>.jar
```

## 5. IAM Requirements

The EMR Serverless job runtime role must be able to access all artifacts used by the job.

At minimum, the role usually needs permissions for:

- `s3:GetObject` on scripts, JARs, Python archives, models, and input data.
- `s3:ListBucket` on buckets/prefixes used for model and pipeline folders.
- `s3:PutObject` on logs, outputs, temporary files, and cache prefixes.
- `secretsmanager:GetSecretValue` and `secretsmanager:DescribeSecret` if using AWS Secrets Manager for the floating license.
- KMS decrypt permissions if the S3 bucket or Secrets Manager secret uses a customer managed KMS key.

Validate S3 access before running the EMR Serverless job:

```bash
aws s3 ls s3://<artifact-bucket>/jars/
aws s3 ls s3://<artifact-bucket>/spark-nlp-emr/envs/
aws s3 ls s3://<artifact-bucket>/spark-nlp-emr/models/<model-or-pipeline-folder>/
```

If these fail from the AWS identity used by your job workflow, fix IAM or bucket policies before debugging Spark.

## 6. Build the Python Runtime Archive

Build the EMR Serverless Python environment in an OS compatible with the EMR runtime. For EMR Serverless 7.x, use Amazon Linux 2023 with Python 3.11.

Create a `Dockerfile`:

```dockerfile
FROM amazonlinux:2023

RUN dnf update -y && \
    dnf install -y \
      python3.11 \
      python3.11-pip \
      python3.11-devel \
      tar \
      gzip \
      findutils \
      shadow-utils && \
    dnf clean all

WORKDIR /work
CMD ["/bin/bash"]
```

Build and enter the container:

```bash
docker build -t emr-venv-builder -f Dockerfile .

docker run --rm -it \
  -u "$(id -u):$(id -g)" \
  -v "$PWD":/work \
  emr-venv-builder
```

Inside the container, create and pack the environment:

```bash
cd /work
rm -rf spark-nlp-hc-env spark-nlp-hc-env.tar.gz

python3.11 -m venv --copies spark-nlp-hc-env
source spark-nlp-hc-env/bin/activate

python -m pip install --upgrade pip
pip install "spark-nlp==<spark-nlp-version>" "numpy==1.26.4" venv-pack
pip install "spark-nlp-jsl==<spark-nlp-jsl-version>" \
  --extra-index-url "https://pypi.johnsnowlabs.com/<customer-package-secret>"

python -c "import numpy; print('numpy ok')"
python -c "import sparknlp; print('sparknlp ok')"
python -c "import sparknlp_jsl; print('sparknlp_jsl ok')"

venv-pack -o spark-nlp-hc-env.tar.gz
```

Use `--copies` when creating the virtual environment. Without it, the packed archive can contain symlinks to the build machine and fail on EMR Serverless with errors such as `./environment/bin/python` not found.

Verify the packed interpreter before uploading:

```bash
rm -rf /tmp/check-hc-env
mkdir -p /tmp/check-hc-env
tar -xzf spark-nlp-hc-env.tar.gz -C /tmp/check-hc-env
ls -l /tmp/check-hc-env/bin/python
file /tmp/check-hc-env/bin/python
```

The Python binary should be a real executable. If you see GLIBC or native library errors at runtime, rebuild the archive in Amazon Linux 2023.

Upload the archive:

```bash
aws s3 cp spark-nlp-hc-env.tar.gz \
  s3://<artifact-bucket>/spark-nlp-emr/envs/spark-nlp-hc-env.tar.gz
```

## 7. Prepare Healthcare Models or Pipelines

There are three common model loading approaches.

### 7.1 Direct S3 Loading

Direct S3 loading is the recommended default for Healthcare pipelines and larger models.

Upload the extracted saved model or pipeline directory to S3:

```text
s3://<artifact-bucket>/spark-nlp-emr/models/<model-or-pipeline-folder>/
```

For a saved pipeline, the target folder should directly contain Spark ML files such as:

```text
metadata/
stages/
```

Then load it from the job script:

```python
import sparknlp
import sparknlp_jsl
from sparknlp.pretrained import PretrainedPipeline

pipeline = PretrainedPipeline.from_disk(
    "s3a://<artifact-bucket>/spark-nlp-emr/models/<model-or-pipeline-folder>/"
)
```

This approach requires `s3:GetObject` and usually `s3:ListBucket` on the model prefix.

### 7.2 Archive-Based Local Loading

For smaller models or proof-of-concept runs, you can distribute a model archive with `spark.archives`:

```bash
--conf spark.archives=s3://<artifact-bucket>/spark-nlp-emr/envs/spark-nlp-hc-env.tar.gz#environment,s3://<artifact-bucket>/spark-nlp-emr/models/<model-archive>.tar.gz#clinical_model
```

Load it locally:

```python
import sparknlp
import sparknlp_jsl
from sparknlp.pretrained import PretrainedPipeline

pipeline = PretrainedPipeline.from_disk("./clinical_model")
```

Create archives from the **contents** of the saved model or pipeline directory, not from the parent folder. After extraction, the target directory should directly contain Spark ML files such as `metadata/` and `stages/` when loading a pipeline.

Very large archives can fail during Spark file distribution or extraction. Based on EMR Serverless experiments, treat `spark.archives` as a small-model convenience path. For multi-GB Healthcare models, prefer direct S3 loading or a custom EMR image with the model pre-baked.

### 7.3 Cache-Based Pretrained Loading

If your EMR Serverless application has outbound access to the required model repository and you want the runtime to download resources, configure an S3 cache path:

```bash
--conf spark.jsl.settings.pretrained.cache_folder=s3a://<artifact-bucket>/spark-nlp-emr/cache_pretrained/
```

Use this only when:

- The runtime can reach the required model repository.
- The job role can write to the cache prefix.
- Your Spark NLP/JSL version supports the cache settings you are using.

For controlled production deployments, direct S3 loading of pre-approved model artifacts is usually easier to audit and reproduce.

## 8. EMR Serverless Application Setup

Create a Spark EMR Serverless application compatible with your Spark NLP Healthcare/JSL version.

Example:

```bash
aws emr-serverless create-application \
  --name spark-nlp-healthcare \
  --type SPARK \
  --release-label <emr-release-label>
```

Recommended first proof-of-concept settings:

```text
Application type: Spark
Release label: <emr-release-label-compatible-with-your-runtime>
Mode: Batch jobs
Serverless storage: Disabled for the first smoke test
VPC access: Enabled when using a floating license
Outbound HTTPS: Allowed through NAT, proxy, firewall, or approved route
```

Start the application before submitting jobs:

```bash
aws emr-serverless start-application \
  --application-id <application-id>
```

## 9. License Configuration

Pass the floating license securely. Avoid hardcoding the raw license in source code, notebooks, or shell history.

Required Spark configuration:

```bash
--conf spark.extraListeners=com.johnsnowlabs.license.LicenseLifeCycleManager \
--conf spark.emr-serverless.driverEnv.JSL_NLP_LICENSE=<license-value-or-secret-reference> \
--conf spark.executorEnv.JSL_NLP_LICENSE=<license-value-or-secret-reference> \
--conf spark.jsl.settings.license=<license-value-or-secret-reference>
```

For EMR Serverless, a common pattern is to store the full license value in AWS Secrets Manager and reference it with:

```text
EMR.secret@<secret-name>
```

If using AWS Secrets Manager:

- Allow the EMR Serverless service and job runtime role to read the secret.
- If the secret uses a customer managed KMS key, allow decrypt access through Secrets Manager.
- Keep the secret in the same region as the EMR Serverless application unless your security design explicitly handles cross-region access.

Example secret resource policy shape:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEMRServerlessReadSecret",
      "Effect": "Allow",
      "Principal": {
        "Service": "emr-serverless.amazonaws.com"
      },
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "*"
    }
  ]
}
```

Use the least permissive policy that works in your environment.

## 10. Baseline Spark Submit Properties

Use these properties as the starting point for a Healthcare/JSL EMR Serverless job:

```bash
--conf spark.archives=s3://<artifact-bucket>/spark-nlp-emr/envs/spark-nlp-hc-env.tar.gz#environment \
--conf spark.emr-serverless.driverEnv.PYSPARK_DRIVER_PYTHON=./environment/bin/python \
--conf spark.emr-serverless.driverEnv.PYSPARK_PYTHON=./environment/bin/python \
--conf spark.executorEnv.PYSPARK_PYTHON=./environment/bin/python \
--conf spark.jars=s3://<artifact-bucket>/jars/spark-nlp-assembly-<spark-nlp-version>.jar,s3://<artifact-bucket>/jars/spark-nlp-jsl-<spark-nlp-jsl-version>.jar \
--conf spark.extraListeners=com.johnsnowlabs.license.LicenseLifeCycleManager \
--conf spark.emr-serverless.driverEnv.JSL_NLP_LICENSE=<license-value-or-secret-reference> \
--conf spark.executorEnv.JSL_NLP_LICENSE=<license-value-or-secret-reference> \
--conf spark.jsl.settings.license=<license-value-or-secret-reference> \
--conf spark.jsl.settings.aws.region=<aws-region> \
--conf spark.jsl.settings.aws.s3_bucket=<artifact-bucket> \
--conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
--conf spark.hadoop.fs.s3a.endpoint=s3.<aws-region>.amazonaws.com \
--conf spark.serializer=org.apache.spark.serializer.KryoSerializer \
--conf spark.kryoserializer.buffer.max=2000M \
--conf spark.driver.maxResultSize=0
```

If the EMR Serverless job runtime role has all required S3 permissions, prefer the default credential chain instead of embedding access keys:

```bash
--conf spark.hadoop.fs.s3a.aws.credentials.provider=software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
```

Some Hadoop/AWS SDK versions may use the older AWS SDK v1 provider instead:

```bash
--conf spark.hadoop.fs.s3a.aws.credentials.provider=com.amazonaws.auth.DefaultAWSCredentialsProviderChain
```

Only add explicit credentials when the runtime role is not sufficient or when using a cross-account access pattern that requires them.

## 11. Static AWS Credentials

For long-lived access key and secret key credentials, configure S3A with `SimpleAWSCredentialsProvider`:

```bash
--conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider \
--conf spark.hadoop.fs.s3a.access.key=<AWS_ACCESS_KEY_ID> \
--conf spark.hadoop.fs.s3a.secret.key=<AWS_SECRET_ACCESS_KEY>
```

For Spark NLP/JSL S3 access settings:

```bash
--conf spark.jsl.settings.aws.region=<aws-region> \
--conf spark.jsl.settings.aws.s3_bucket=<artifact-bucket> \
--conf spark.jsl.settings.aws.credentials.access_key_id=<AWS_ACCESS_KEY_ID> \
--conf spark.jsl.settings.aws.credentials.secret_access_key=<AWS_SECRET_ACCESS_KEY>
```

Do not set a session token for static credentials.

## 12. Temporary AWS Credentials

For STS credentials, always pass all three values: access key, secret key, and session token.

```bash
--conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.TemporaryAWSCredentialsProvider \
--conf spark.hadoop.fs.s3a.access.key=<AWS_ACCESS_KEY_ID> \
--conf spark.hadoop.fs.s3a.secret.key=<AWS_SECRET_ACCESS_KEY> \
--conf spark.hadoop.fs.s3a.session.token=<AWS_SESSION_TOKEN>
```

For Spark NLP/JSL S3 access settings:

```bash
--conf spark.jsl.settings.aws.credentials.access_key_id=<AWS_ACCESS_KEY_ID> \
--conf spark.jsl.settings.aws.credentials.secret_access_key=<AWS_SECRET_ACCESS_KEY> \
--conf spark.jsl.settings.aws.credentials.session_token=<AWS_SESSION_TOKEN>
```

Do **not** use `SimpleAWSCredentialsProvider` with assumed-role or other STS credentials. Temporary credentials require the session token.

Avoid setting these values as driver environment variables unless tested and required:

```bash
--conf spark.emr-serverless.driverEnv.AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
--conf spark.emr-serverless.driverEnv.AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
--conf spark.emr-serverless.driverEnv.AWS_SESSION_TOKEN=<AWS_SESSION_TOKEN>
```

In some environments, driver environment AWS variables can override credentials used by internal AWS SDK calls. Prefer `spark.hadoop.fs.s3a.*` and `spark.jsl.settings.aws.credentials.*` unless you have validated a different pattern.

## 13. Minimal Healthcare Test Script

Save the following as `healthcare_emr_serverless_test.py`:

```python
import sparknlp
import sparknlp_jsl
from sparknlp.pretrained import PretrainedPipeline


def main():
    print("Spark NLP version:", sparknlp.version())
    print("spark-nlp-jsl imported successfully")

    pipeline = PretrainedPipeline.from_disk(
        "s3a://<artifact-bucket>/spark-nlp-emr/models/<model-or-pipeline-folder>/"
    )

    text = "John Smith visited the clinic in Boston on 2024-01-20."
    result = pipeline.annotate(text)

    print("=== INPUT ===")
    print(text)
    print("=== OUTPUT ===")
    print(result)


if __name__ == "__main__":
    main()
```

The `import sparknlp_jsl` line is required. It makes the Python wrappers for Healthcare/JSL stages available during model or pipeline deserialization.

Upload the script:

```bash
aws s3 cp healthcare_emr_serverless_test.py \
  s3://<artifact-bucket>/spark-nlp-emr/scripts/healthcare_emr_serverless_test.py
```

## 14. Submit an EMR Serverless Job

Set common variables:

```bash
export APPLICATION_ID="<application-id>"
export EXECUTION_ROLE_ARN="<emr-serverless-runtime-role-arn>"
export AWS_REGION="<aws-region>"
export ARTIFACT_BUCKET="<artifact-bucket>"
export SPARK_NLP_VERSION="<spark-nlp-version>"
export SPARK_NLP_JSL_VERSION="<spark-nlp-jsl-version>"
export LICENSE_REF="<license-value-or-secret-reference>"
```

Example `start-job-run` command using the runtime role/default AWS credential chain:

```bash
aws emr-serverless start-job-run \
  --application-id "$APPLICATION_ID" \
  --execution-role-arn "$EXECUTION_ROLE_ARN" \
  --job-driver "{
    \"sparkSubmit\": {
      \"entryPoint\": \"s3://$ARTIFACT_BUCKET/spark-nlp-emr/scripts/healthcare_emr_serverless_test.py\",
      \"sparkSubmitParameters\": \"--conf spark.archives=s3://$ARTIFACT_BUCKET/spark-nlp-emr/envs/spark-nlp-hc-env.tar.gz#environment --conf spark.emr-serverless.driverEnv.PYSPARK_DRIVER_PYTHON=./environment/bin/python --conf spark.emr-serverless.driverEnv.PYSPARK_PYTHON=./environment/bin/python --conf spark.executorEnv.PYSPARK_PYTHON=./environment/bin/python --conf spark.jars=s3://$ARTIFACT_BUCKET/jars/spark-nlp-assembly-$SPARK_NLP_VERSION.jar,s3://$ARTIFACT_BUCKET/jars/spark-nlp-jsl-$SPARK_NLP_JSL_VERSION.jar --conf spark.extraListeners=com.johnsnowlabs.license.LicenseLifeCycleManager --conf spark.emr-serverless.driverEnv.JSL_NLP_LICENSE=$LICENSE_REF --conf spark.executorEnv.JSL_NLP_LICENSE=$LICENSE_REF --conf spark.jsl.settings.license=$LICENSE_REF --conf spark.jsl.settings.aws.region=$AWS_REGION --conf spark.jsl.settings.aws.s3_bucket=$ARTIFACT_BUCKET --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem --conf spark.hadoop.fs.s3a.endpoint=s3.$AWS_REGION.amazonaws.com --conf spark.hadoop.fs.s3a.aws.credentials.provider=software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider --conf spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.kryoserializer.buffer.max=2000M --conf spark.driver.maxResultSize=0\"
    }
  }" \
  --configuration-overrides "{
    \"monitoringConfiguration\": {
      \"s3MonitoringConfiguration\": {
        \"logUri\": \"s3://$ARTIFACT_BUCKET/spark-nlp-emr/logs/\"
      }
    }
  }"
```

If using temporary STS credentials, add the `TemporaryAWSCredentialsProvider` and Spark NLP/JSL credential properties from [Temporary AWS Credentials](#12-temporary-aws-credentials) to the `sparkSubmitParameters` string.

## 15. Property Reference

| Property | Purpose |
| --- | --- |
| `spark.archives` | Extracts the packed Python environment as `./environment`. Can also distribute small model archives. |
| `spark.emr-serverless.driverEnv.PYSPARK_DRIVER_PYTHON` | Forces the driver to use the packed Python interpreter. |
| `spark.emr-serverless.driverEnv.PYSPARK_PYTHON` | Sets the driver-side PySpark Python interpreter. |
| `spark.executorEnv.PYSPARK_PYTHON` | Sets executor-side PySpark Python interpreter. |
| `spark.jars` | Loads Spark NLP and Spark NLP Healthcare/JSL JARs from S3 without Maven resolution. |
| `spark.extraListeners` | Enables the JSL license lifecycle manager. |
| `spark.emr-serverless.driverEnv.JSL_NLP_LICENSE` | Provides the license to the driver environment. |
| `spark.executorEnv.JSL_NLP_LICENSE` | Provides the license to executor environments. |
| `spark.jsl.settings.license` | Provides the license to Spark NLP/JSL settings. |
| `spark.jsl.settings.aws.region` | AWS region used by Spark NLP/JSL cloud operations. |
| `spark.jsl.settings.aws.s3_bucket` | S3 bucket used by Spark NLP/JSL cloud operations. |
| `spark.jsl.settings.aws.credentials.*` | Explicit credentials used by Spark NLP/JSL cloud operations when the runtime role/default chain is not enough. |
| `spark.jsl.settings.pretrained.cache_folder` | Optional S3 cache path for pretrained resources. |
| `spark.hadoop.fs.s3a.impl` | Enables Hadoop S3A paths such as `s3a://...`. |
| `spark.hadoop.fs.s3a.endpoint` | Points S3A to the regional S3 endpoint. |
| `spark.hadoop.fs.s3a.aws.credentials.provider` | Selects the S3A credential provider. |
| `spark.hadoop.fs.s3a.access.key` | Explicit AWS access key for S3A. Omit when using runtime role/default chain. |
| `spark.hadoop.fs.s3a.secret.key` | Explicit AWS secret key for S3A. Omit when using runtime role/default chain. |
| `spark.hadoop.fs.s3a.session.token` | Required for STS/temporary S3A credentials. |
| `spark.serializer` | Uses Kryo serializer, recommended for Spark NLP workloads. |
| `spark.kryoserializer.buffer.max` | Prevents serialization buffer issues with large NLP models. |
| `spark.driver.maxResultSize` | Allows large driver-side results when needed. Keep production output sizes controlled. |

## 16. Troubleshooting Checklist

### Python environment fails to start

Symptoms:

```text
./environment/bin/python: No such file or directory
```

Checks:

- Build the virtual environment with `python3.11 -m venv --copies`.
- Verify `bin/python` after extracting the tarball locally.
- Build on Amazon Linux 2023 for EMR Serverless 7.x compatibility.

### `sparknlp_jsl` import fails

Checks:

- Confirm `spark-nlp-jsl==<version>` was installed in the packed environment.
- Confirm the JSL package secret/extra index URL was valid during environment build.
- Run `python -c "import sparknlp_jsl"` before packing.

### Model or pipeline fails to deserialize

Checks:

- Ensure `import sparknlp_jsl` exists before loading the pipeline.
- Verify Spark NLP, Spark NLP Healthcare/JSL, and model versions are compatible.
- Confirm both JARs are included in `spark.jars`.
- Confirm the saved pipeline directory contains `metadata/` and `stages/` at the expected path.

### S3 model loading fails

Checks:

- Validate `s3:GetObject` and `s3:ListBucket` permissions on the model prefix.
- Confirm `spark.hadoop.fs.s3a.impl` and `spark.hadoop.fs.s3a.endpoint` are configured.
- Use `TemporaryAWSCredentialsProvider` when passing STS credentials.
- Include `spark.hadoop.fs.s3a.session.token` for temporary credentials.

### License validation times out

Checks:

- Confirm VPC access is configured on the EMR Serverless application.
- Confirm subnets have a route to NAT, proxy, firewall, or approved outbound HTTPS path.
- Confirm security groups and network ACLs allow outbound HTTPS.
- Confirm the license secret/value is passed to driver, executors, and `spark.jsl.settings.license`.

### Large model archive fails with `spark.archives`

Checks:

- Try direct S3 loading with `PretrainedPipeline.from_disk("s3a://...")`.
- Test first with a smaller model or fewer executors.
- Consider baking large models into a custom runtime image if your deployment requires local loading.

## 17. References

- Amazon EMR Serverless job runtime roles: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/security-iam-runtime-role.html
- Amazon EMR Serverless VPC access: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/vpc-access.html
- Amazon EMR Serverless cross-account S3 access: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/jobs-s3-access.html
- Amazon EMR Serverless Spark jobs: https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/jobs-spark.html
- Hadoop AWS S3A authentication: https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html
- John Snow Labs floating license information: https://nlp.johnsnowlabs.com/docs/en/alab/byol
- Spark NLP Models Hub: https://nlp.johnsnowlabs.com/models
