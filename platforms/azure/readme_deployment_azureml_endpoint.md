# 🚀 Deploying Spark NLP for Healthcare (JSL) Pipeline on Azure ML as a REST API

## 🧩 Overview
This guide explains how to package, containerize, and deploy a **Spark NLP for Healthcare (JSL)** pretrained NER pipeline as a **Managed Online Endpoint** on **Azure Machine Learning (Azure ML)**.


## 📚 How this README and notebook work together

This README is the **deployment guide**. It explains the architecture, prerequisites, container image, scoring script, endpoint deployment, testing, and production security notes.

The companion notebook is the **executable walkthrough**:

- [`SparkNLP-JSL-AzureML-Endpoint-Demo.ipynb`](./SparkNLP-JSL-AzureML-Endpoint-Demo.ipynb)

Use the notebook when you want to run the Azure ML workflow interactively. Use this README when you want the clean deployment reference or need to reproduce the same flow outside the notebook.

### Notebook section map

| Notebook section | Purpose | Related README section |
| --- | --- | --- |
| 1. Install notebook dependencies | Prepare the notebook runtime | Prerequisites, Docker image |
| 2. Configure Spark NLP Healthcare license and validate Spark | Load local/private credentials and start Spark NLP Healthcare | Prerequisites, Managing Secrets Securely |
| 3. Load and test the medical NER pipeline | Validate `ner_jsl_pipeline` before deployment | Scoring script, Test the Endpoint |
| 4. Save the pipeline model locally | Create the model artifact | Register/deploy flow |
| 5. Register the model in Azure ML | Register model asset in Azure ML | Deploy the Endpoint |
| 6. Create the endpoint and deployment | Create Managed Online Endpoint and deployment | Deploy the Endpoint |
| 7. Get endpoint details | Retrieve scoring URI and deployment state | Test the Endpoint |
| 8. Route endpoint traffic | Configure blue/green traffic routing | Notes / production rollout |
| 9. Collect deployment logs | Troubleshoot failed provisioning or runtime errors | Notes / troubleshooting |

---

## ⚙️ 1. Prerequisites

### Tools Required
| Tool | Version | Purpose |
|------|----------|----------|
| Azure CLI | ≥ 2.79.0 | Manage Azure resources |
| Azure ML CLI extension | latest | Deploy and monitor ML endpoints |
| Docker | latest | Build custom containers |
| Python | ≥ 3.8 | Azure SDK and scripting |
| Spark NLP for Healthcare License | Active | Required for `spark-nlp-jsl` installation |

### Install Core Dependencies
We need to create a Docker image because `spark-nlp-jsl` cannot be installed using a standard `conda.yml` file.  
For this, it’s recommended to use the **Azure CLI** locally on your machine.

---

## 🧩 2. Installing Azure CLI

```bash
curl -sL https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo apt-add-repository https://packages.microsoft.com/repos/azure-cli/
sudo apt-get update
sudo apt-get install azure-cli -y
```

Login to Azure:
```bash
az login
```
This command will open Azure Login URL. Once you logged in you are ready to go

Find and set your ACR name:
```bash
az acr list -o table
export ACR_NAME=<NAME_FROM_ABOVE_OUTPUT>
```

---

## 🧩 3. Build the Custom Docker Image

### Dockerfile
```dockerfile
FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04

RUN apt-get update && apt-get install -y wget tar && \
    wget https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u432-b06/OpenJDK8U-jdk_x64_linux_hotspot_8u432b06.tar.gz && \
    mkdir -p /usr/lib/jvm && \
    tar -xzf OpenJDK8U-jdk_x64_linux_hotspot_8u432b06.tar.gz -C /usr/lib/jvm && \
    rm OpenJDK8U-jdk_x64_linux_hotspot_8u432b06.tar.gz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/jdk8u432-b06
ENV PATH=$JAVA_HOME/bin:$PATH

RUN pip install --upgrade pip
RUN pip install pyspark==3.5.0 spark-nlp==6.1.1
RUN pip install spark-nlp-jsl==6.1.0 --extra-index-url https://pypi.johnsnowlabs.com/6.1.0-<YOUR_LICENSE_TOKEN>
RUN pip install azureml-defaults

WORKDIR /app
COPY . /app
CMD ["python", "score-jsl.py"]
```

---

## 🧩 4. Push the Image to Azure Container Registry (ACR)

Build and push:
```bash
az acr build --registry $ACR_NAME --image spark-nlp-jsl:6.1.0 .
az acr repository show-tags --name $ACR_NAME --repository spark-nlp-jsl -o table
```

---

## 🧩 5. Create the Scoring Script (`score-jsl.py`)

In Azure ML Studio:

> **Path:** Notebooks → Files → Users → *YourUserName* → Create new file → *Python script*

Paste the following:

```python
import os
import json
import traceback
import sparknlp_jsl
from sparknlp.pretrained import PretrainedPipeline

# Globals reused across requests
medical_ner_pipeline = None
initialized = False


def init():
    global medical_ner_pipeline, initialized
    try:
        print("🚀 Starting Spark NLP for Healthcare...")

        # ✅ Only fallback to file if vars are missing
        required_keys = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "SPARK_NLP_LICENSE"]
        missing = [k for k in required_keys if k not in os.environ]

        if missing and os.path.exists("license_keys.json"):
            print(f"⚠️ Missing {missing}, loading from license_keys.json...")
            with open("license_keys.json") as f:
                os.environ.update(json.load(f))

        print("🔐 License keys configured. Starting Spark session...")
        spark = sparknlp_jsl.start(secret=os.environ.get("SPARK_NLP_LICENSE"))

        print("Initializing PretrainedPipeline ner_jsl_pipeline...")
        medical_ner_pipeline = PretrainedPipeline("ner_jsl_pipeline", "en", "clinical/models")
        initialized = True
        print("✅ Model ready for inference!")
    except Exception as e:
        print("❌ Initialization failed:", e)
        traceback.print_exc()
        raise e


def run(raw_data):
    """
    Called for each REST request.
    Processes text input and returns extracted entities.
    """
    global medical_ner_pipeline, initialized

    try:
        if not initialized or medical_ner_pipeline is None:
            print("⚠️ Pipeline not initialized, reinitializing...")
            init()

        # Parse incoming JSON
        data = json.loads(raw_data)
        text = data.get("text", "").strip()

        if not text:
            return {"error": "Missing 'text' field in request JSON."}

        print(f"🔍 Processing text: {text[:80]}...")

        # Run inference
        result = medical_ner_pipeline.annotate(text)
        entities = result.get("ner_chunk", [])

        print("✅ Extraction complete. Entities:", entities)
        return {"entities": entities}

    except json.JSONDecodeError:
        return {"error": "Invalid JSON format. Expected: {'text': 'your text'}"}

    except Exception as e:
        print("❌ ERROR during processing:")
        print(traceback.format_exc())
        return {"error": f"Processing failed: {str(e)}"}
```

---

## 🧩 6. Deploy the Endpoint

Create a new **Notebook** in Azure ML Studio:  
> Notebooks → Files → Users → *YourUserName* → New Notebook

Copy the steps or import the attached notebook `SparkNLP-JSL-AzureML-Endpoint-Demo.ipynb`.


**Important:** Include a file named `license_keys.json` 
> Notebooks > Files > Users > YourUserName > ... > Create new file > JSON file

```json
{
  "AWS_ACCESS_KEY_ID": "YOUR_AWS_ACCESS_KEY_ID",
  "AWS_SECRET_ACCESS_KEY": "YOUR_AWS_SECRET_ACCESS_KEY",
  "SPARK_NLP_LICENSE": "YOUR_SPARK_NLP_LICENSE"
}
```

---

## 🧩 7. Test the Endpoint

After deployment, note the endpoint URI (shown in the notebook step 4 or in **Azure ML Studio → Endpoints**).
Here you can check the endpoint URI, how to make requests and the Token required to make requests.

Example request:
```bash
curl -X POST "https://jsl-medical-ner-endpoint.eastus.inference.ml.azure.com/score" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token-here>" \
  -d '{
        "text": "Patient is taking 5mg of prednisone daily for asthma."
      }'
```

✅ **Example of Expected output:**
```json
{"entities": ["prednisone", "asthma"]}
```

> The first request may take longer or timeout as the container warms up. Just retry!
> If you get an initialization error, retry or check the deployment logs.

---

## 🗂️ Repository files

After this cleanup, the Azure ML deployment example is organized around these files:

```text
platforms/azure/
├── readme_deployment_azureml_endpoint.md           # Deployment guide
└── SparkNLP-JSL-AzureML-Endpoint-Demo.ipynb        # Executable notebook walkthrough
```

The scoring script is included above as a code snippet so the README remains self-contained. If you build the Docker image from this guide, create `score-jsl.py` from that snippet in the Azure ML build context before running `az acr build`.

---

## ✅ Final Result

You now have:
- A **custom Docker image** with Spark NLP + Spark NLP JSL + JDK 8  
- A **Managed Online Endpoint** deployed on Azure ML  
- A secure **REST API** for medical entity extraction  

---

## 🧠 Notes

- Use `Standard_F2s_v2` for lightweight inference and to stay within your quota.
- For production, increase replicas:
  ```python
  deployment.instance_count = 2
  ml_client.begin_create_or_update(deployment)
  ```
- Retrieve logs via CLI:
  ```bash
  az ml online-deployment get-logs --name blue --endpoint-name jsl-medical-ner-endpoint --lines 200
  ```

---

## 🔐 Managing Secrets Securely (Recommended)

Storing credentials such as AWS keys or Spark NLP license strings directly in files or environment variables is not ideal for production environments.  
Instead, use **Azure Key Vault** to securely manage and inject secrets into your Azure ML deployments.

### Steps:
1. **Create a Key Vault**
   ```bash
   az keyvault create --name <your-keyvault-name> --resource-group <your-resource-group> --location <region>
   ```

2. **Add your secrets**
   ```bash
   az keyvault secret set --vault-name <your-keyvault-name> --name "SPARK_NLP_LICENSE" --value "<your-license>"
   az keyvault secret set --vault-name <your-keyvault-name> --name "AWS_ACCESS_KEY_ID" --value "<your-aws-key>"
   az keyvault secret set --vault-name <your-keyvault-name> --name "AWS_SECRET_ACCESS_KEY" --value "<your-aws-secret>"
   ```

3. **Reference secrets in your Azure ML endpoint environment**
   ```python
   environment_variables={
       "SPARK_NLP_LICENSE": "${{secrets.SPARK_NLP_LICENSE}}",
       "AWS_ACCESS_KEY_ID": "${{secrets.AWS_ACCESS_KEY_ID}}",
       "AWS_SECRET_ACCESS_KEY": "${{secrets.AWS_SECRET_ACCESS_KEY}}"
   }
   ```

📘 **Official documentation:**  
👉 [Use Azure Key Vault secrets in Azure Machine Learning](https://learn.microsoft.com/azure/machine-learning/how-to-use-secrets-in-runs?tabs=python)

---
