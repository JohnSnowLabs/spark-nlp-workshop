<a href="https://johnsnowlabs.com"><img src="https://media.licdn.com/dms/image/C510BAQFT1HLZor5NGA/company-logo_200_200/0?e=1585180800&v=beta&t=VXCxWGmVfq4qlS1Xs9VNl6fB-mI3wmO64IGwGlkVmik" width="125" height="125" align="right" /></a>

# Spark NLP Workshop

[![Build Status](https://travis-ci.org/JohnSnowLabs/spark-nlp.svg?branch=master)](https://travis-ci.org/JohnSnowLabs/spark-nlp) [![Maven Central](https://maven-badges.herokuapp.com/maven-central/com.johnsnowlabs.nlp/spark-nlp_2.11/badge.svg)](https://search.maven.org/artifact/com.johnsnowlabs.nlp/spark-nlp_2.11) [![PyPI version](https://badge.fury.io/py/spark-nlp.svg)](https://badge.fury.io/py/spark-nlp) [![Anaconda-Cloud](https://anaconda.org/johnsnowlabs/spark-nlp/badges/version.svg)](https://anaconda.org/JohnSnowLabs/spark-nlp) [![License](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://github.com/JohnSnowLabs/spark-nlp/blob/master/LICENSE)

Showcasing notebooks and codes of how to use Spark NLP in Python and Scala.

## Table of contents

* [Jupyter Notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter)
  * [annotation](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter/annotation)
  * [evalulation](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter/eval)
  * [training](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter/training)
* [Tutorial Notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/tutorials)
  * [Jupyter](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/tutorials/jupyter)
  * [Colab](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/tutorials/colab) (for Google Colab)
* [Databricks Notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/databricks)

## Docker setup

If you want to experience Spark NLP and run Jupyter exmaples without installing anything, you can simply use our [Docker image](https://hub.docker.com/r/johnsnowlabs/spark-nlp-workshop):

1- Get the docker image for spark-nlp-workshop:

```bash
docker pull johnsnowlabs/spark-nlp-workshop
```

2- Run the image locally with port binding.

```bash
 docker run -it --rm -p 8888:8888 -p 4040:4040 johnsnowlabs/spark-nlp-workshop
```

3- Open Jupyter notebooks inside your browser by using the token printed on the console.

```bash
http://localhost:8888/
```

* The password to Jupyter notebook is `sparknlp`
* The size of the image grows everytime you download a pretrained model or a pretrained pipeline. You can cleanup `~/cache_pretrained` if you don't need them.
* This docker image is only meant for testing/learning purposes and should not be used in production environments. Please install Spark NLP natively.

## Main repository

[https://github.com/JohnSnowLabs/spark-nlp](https://github.com/JohnSnowLabs/spark-nlp)

## Project's website

Take a look at our official spark-nlp page: [http://nlp.johnsnowlabs.com/](http://nlp.johnsnowlabs.com/) for user documentation and examples

## Slack community channel

[Join Slack](https://join.slack.com/t/spark-nlp/shared_invite/enQtNjA4MTE2MDI1MDkxLTM4ZDliMjU5OWZmMDE1ZGVkMjg0MWFjMjU3NjY4YThlMTJkNmNjNjM3NTMwYzlhMWY4MGMzODI2NDBkOWU4ZDE)

## Contributing

If you find any example that is no longer working, please create an [issue](https://github.com/JohnSnowLabs/spark-nlp-workshop/issues).

## License

Apache Licence 2.0
