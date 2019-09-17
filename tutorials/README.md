# Spark-NLP Tutorials

## Spark NLP Instructions

1.Install docker in your systems:

Go to site [https://docs.docker.com/install/](https://docs.docker.com/install/) to download based on your specific OS.

Note for windows user:
Use the stable channel for windows 10

[https://docs.docker.com/docker-for-windows/install/#what-to-know-before-you-install](https://docs.docker.com/docker-for-windows/install/#what-to-know-before-you-install)

2.Get the docker image for spark-nlp-workshop:

```bash
docker pull johnsnowlabs/spark-nlp-workshop
```

3.Run the image locally with port binding.

```bash
 docker run -it --rm -p 8888:8888 -p 4040:4040 johnsnowlabs/spark-nlp-workshop
```

4.Run the notebooks on your browser using the token printed on the console.

```bash
http://localhost:8888/
```

> NOTE: The password to Jupyter notebook is `sparknlp`

### Increase Docker memory

The total memory of the VM in which docker runs is 2GB by default. You can increase this in macOS and Windows via gui.

> Preferences -> Advanced:
![Databricks](docker_memory.png)
