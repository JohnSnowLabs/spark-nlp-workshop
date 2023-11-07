## Docker Image for running Spark NLP for Healthcare Image

### Instructions
- Run the following commands to download the docker-compose.yml and the sparknlp_keys.txt files on your local machine:

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/jupyter/docker_enterprise/docker_image_nlp_hc/sparknlp_for_healthcare_image/docker-compose.yaml
curl -o sparknlp_keys.txt https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/jupyter/docker_enterprise/docker_image_nlp_hc/sparknlp_for_healthcare_image/sparknlp_keys.txt
```
- Download your license key in json format from [my.JohnSnowLabs.com](https://my.johnsnowlabs.com/)
- Populate License keys in sparknlp_keys.txt file
- Run the following command to run the container in detached mode:
```bash
docker-compose up -d
```
- By default, the jupyter notebook runs on `port 8888` - you can access it by typing `localhost:8888` in your browser

### Troubleshooting

- Make sure docker is installed on your system.
- If you face any error while importing the lib inside jupyter, make sure all the credentials are correct in the key files and restart the service again.
- If the default `port 8888` is already occupied by another process, please change the mapping.
- You can change/adjust volume and port mapping in the `docker-compose.yaml` file.
- You don’t have a license key? Ask for a trial license [here](https://www.johnsnowlabs.com/install/).
