## Docker Image for running Spark OCR (with Spark NLP) inside Jupyter Notebook

The Image contains all the required libraries for installing and running Spark OCR. However, it does not contain the library itself, as it is licensed, and requires installation credentials. 

**Make sure you have valid license for Spark OCR, and follow the instructions below**


### Instructions
- Copy `docker-compose.yml` and `sparkocr_keys.txt` files to your host machine.
- Populate License keys in `sparkocr_keys.txt`.
- If you don't want to run spark nlp with spark ocr, you can skip `PUBLIC_VERSION` variable in the `sparkocr_keys.txt` file.
- Run command `docker-compose up -d` to run the container in detached mode.
- By default, the jupyter notebook would run at port `8888` - you can access the notebook by typing `localhost:8888` in your browser.

#### Running Spark NLP with Spark OCR
- Populate the `PUBLIC_VERSION` variable in the `sparkocr_keys.txt` file with a Spark NLP version that is compatible with your version of Spark OCR by refering to this [table](https://nlp.johnsnowlabs.com/docs/en/version_compatibility)
- Run command `docker-compose up -d` to run the container in detached mode.

#### Running Spark NLP for Healthcare with Spark OCR
- Please make sure that your Spark NLP for Healthcare and Spark OCR versions are compatible with each other by refering to this [table](https://nlp.johnsnowlabs.com/docs/en/version_compatibility)
- Copy this [file](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/jupyter/docker_image_nlp_hc/sparknlp_keys.txt), and populate it.
- Uncomment line # 11 in `docker-compose.yml` to include `sparknlp_keys.txt`.
- Run command `docker-compose up -d` to run the container in detached mode.


### Troubleshooting
- Make sure docker is installed on your system.
- If you face any error while importing the lib inside jupyter, make sure all the credentials are correct in the key files and restart the service again.
- If the default port `8888` is already occupied by another process, please change the mapping.
- You can change/adjust volume and port mapping in the `docker-compose.yml` file.