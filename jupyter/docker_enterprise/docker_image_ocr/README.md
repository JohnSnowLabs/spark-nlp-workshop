## Docker Image for running Spark OCR (with Spark NLP) inside Jupyter Notebook

The Image contains all the required libraries for installing and running Spark OCR. However, it does not contain the library itself, as it is licensed, and requires installation credentials. 

**docker run -v `/home/jsl_keys.json`:/notebooks/sparknlp_keys.json -p `8888`:8888 -d johnsnowlabs/sparknlp:sparkocr_jupyter**

Please replace values inside `tags`. For instance, replace `/home/jsl_keys.json` with the correct license json absolute path.

### Troubleshooting
- Make sure docker is installed on your system.
- Run `docker ps` to validate the container is running.
- If your container is not running, look at docker logs to identify issue.
- If the default port `8888` is already occupied by another process, please change the mapping. Only change values inside the `tags`.
