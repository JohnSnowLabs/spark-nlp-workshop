## Docker Image for Interactive Streamlit Web App for running Spark NLP for Healthcare NER Models

The Image contains all the required libraries for installing and running Spark NLP for Healthcare. However, it does not contain the library itself, as it is licensed, and requires installation credentials. Make sure you have valid license for Spark NLP for Healthcare, and run the following command:

**docker run -v `/home/jsl_keys`.json:/content/sparknlp_keys.json -p `8501`:8501 -e USE_BERT=`false` -d johnsnowlabs/sparknlp:sparknlp_ner_playground**

Please replace values inside `tags`:
- Replace `/home/jsl_keys.json` with the correct license json absolute path.
- Replace `8501` with any other port if required.
- Replace the value of USE_BERT with `true` if you want to use BERT base models. By default, GLoVe models will be used.

You can connect to a web app via browser using this address: `http://0.0.0.0:8501`.

![explanation](https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/jupyter/docker_image_nlp_hc_playground/ner_playground_exp.png)


### Troubleshooting
- Make sure docker is installed on your system.
- Run `docker ps` to validate the container is running.
- If your container is not running, look at docker logs to identify issue.
- If the default port `8501` is already occupied by another process, please change the mapping. Only change values inside the `tags`.
