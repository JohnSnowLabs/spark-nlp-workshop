## Docker Image for running Spark NLP for Healthcare inside Jupyter Notebook

The Image contains all the required libraries for installing and running Spark NLP for Healthcare. However, it does not contain the library itself, as it is licensed, and requires installation credentials. 

**Make sure you have valid license for Spark NLP for Healthcare, and follow the instructions below**


### Instructions
- Copy `docker-compose.yml` and `sparknlp_keys.txt` files to your host machine.
- Populate License keys in `sparknlp_keys.txt`.
- Run command `docker-compose up -d` to run the container in detached mode.
- By default, the jupyter notebook would run at port `8888` - you can access the notebook by typing `localhost:8888` in your browser.

### Troubleshooting
- Make sure docker is installed on your system.
- If you face any error while importing the lib inside jupyter, make sure all the credentials are correct in the key files and restart the service again.
- If the default port `8888` is already occupied by another process, please change the mapping.
- You can change/adjust volume and port mapping in the `docker-compose.yml` file.