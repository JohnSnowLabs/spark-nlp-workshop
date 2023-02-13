# Docker version of johnsnowlabs library with FastAPI

## LEGAL NLP
`johnsnowlabs` version can be installed in a Docker container with Spark+Java+Python. We provide that image
for you in this folder, and also some extra code: a FastAPI sample app with one endpoint to serve a pipeline.

Feel free to create other endpoints in that template and leverage the power and speed of Spark NLP!

- NOTE 1: The Docker image is configured to run Spark in `1-node mode (driver)`
- NOTE 2: Use `LightPipelines` to speed up inference if you are running in 1-node / driver mode.

Steps:
```
- sudo docker-compose up -d .
- sudo docker exec -it johnsnowlabs /bin/bash
- source jslenv/bin/activate
- python fastapi_app.py
- Open in a browser: http://localhost:8515/legpipe_deid
```

## FINANCIAL NLP
In fastapi_app.py, modify the pretrained pipeline so that it is a Financial Pipeline available in Spark NLP for Finance in Models Hub.

## CLINICAL NLP
In fastapi_app.py, modify the pretrained pipeline so that it is a Healthcare Pipeline available in Spark NLP for Healthcare in Models Hub.
