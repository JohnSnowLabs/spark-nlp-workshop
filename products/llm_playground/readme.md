# John Snow Labs LLM Workshop

This guide explains how to set up and test **John Snow Labs’ Large Language Models (LLMs)** using a **GPU-enabled environment**.  
You’ll learn how to prepare the environment, run the container, and test the available LLMs.

This workshop requires a **GPU-enabled machine**, such as an **AWS EC2 instance** equipped with **NVIDIA GPUs**.

## 1. Environment Setup

Clone the private repository (if you haven’t already):

```bash
git clone https://github.com/JohnSnowLabs/spark-nlp-workshop.git
```

Navigate to the `products/llm_playground` directory:

```bash
cd spark-nlp-workshop/products/llm_playground
```

## 2. GPU Environment Setup

Run the provided setup script to install all required GPU dependencies.

```bash
chmod +x infra-setup-for-ubuntu.sh
sudo ./infra-setup-for-ubuntu.sh
```

This script will:
- Install and configure the **NVIDIA Container Toolkit**
- Verify GPU visibility using `nvidia-smi`
- Ensure Docker is properly configured for GPU workloads

After installation, your machine may restart.

Once it’s back up, verify that your GPU is available:

```bash
nvidia-smi
```

You should see details about your GPU model and driver version.

## 3. Install Python Dependencies

Once your GPU environment is ready, install all Python dependencies required for the workshop. Make sure youre inside the correct directory `products/llm_playground`

```
cd spark-nlp-workshop/products/llm_playground
pip install -r requirements.txt
```

## 4. Add License File

Place a valid `license.json` file inside the `products/llm_playground` directory. This is the same `license.json` file that you got from JohnSnowLabs to use HealthCare NLP products. If you don't have it, you can download this license file from https://my.johnsnowlabs.com or contact us at info@johnsnowlabs.com.

```
products/llm_playground/
│
├── Dockerfile  
├── docker-compose.yaml                    
├── requirements.txt
├── app/         
├── infra-setup-for-ubuntu.sh  
├── requirements-with-cli.txt  
├── start.sh
└── license.json     ← place your license file here
```

## 5. Run the LLM Docker Container

Once the GPU environment is ready, run the LLM Workshop container from the project root (`products/llm_playground`):

```bash
docker run --name jsl-llms-workshop                 \
  -e CONTAINER_PORT=5001                            \
  -p 5001:5000                                      \
  -v $(pwd)/license.json:/app/secret/license.json   \
  johnsnowlabs/jsl-llms:workshop-v1
```

**Notes:**
- The container automatically starts the internal LLM API server on **port 5000**
- It is exposed externally on **port 5001**

To confirm the container is running:

```bash
docker ps
```

You should see something like:

```
CONTAINER ID   IMAGE                               COMMAND                  STATUS         PORTS
96126f4cd577   johnsnowlabs/jsl-llms:workshop-v1   "/opt/nvidia/nvidia_…"   Up 6 minutes   0.0.0.0:5001->5000/tcp
```

## 6. Test the API Endpoints

After the container is running, open your browser and visit:

```
http://<your-public-ip>:5001/docs
```

You can find your public IP with:

```bash
curl -4 ifconfig.me
```

Example:

```
http://13.48.22.115:5001/docs
```

This page provides an interactive Swagger UI for testing the available LLM APIs, including endpoints for model status, deployment, and available models. Happy experimenting!

## Need Help?

If you encounter any issues with setup, licensing, or running the container, please contact the John Snow Labs support team:

support@johnsnowlabs.com
