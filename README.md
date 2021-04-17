<a href="https://johnsnowlabs.com"><img src="https://www.johnsnowlabs.com/wp-content/uploads/2020/03/johnsnowlabs-square.png" width="125" height="125" align="right" /></a>

# Spark NLP Workshop

[![Build Status](https://travis-ci.org/JohnSnowLabs/spark-nlp.svg?branch=master)](https://travis-ci.org/JohnSnowLabs/spark-nlp) [![Maven Central](https://maven-badges.herokuapp.com/maven-central/com.johnsnowlabs.nlp/spark-nlp_2.12/badge.svg)](https://search.maven.org/artifact/com.johnsnowlabs.nlp/spark-nlp_2.12) [![PyPI version](https://badge.fury.io/py/spark-nlp.svg)](https://badge.fury.io/py/spark-nlp) [![Anaconda-Cloud](https://anaconda.org/johnsnowlabs/spark-nlp/badges/version.svg)](https://anaconda.org/JohnSnowLabs/spark-nlp) [![License](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://github.com/JohnSnowLabs/spark-nlp/blob/master/LICENSE)

Showcasing notebooks and codes of how to use Spark NLP in Python and Scala.

## Table of contents

* [Jupyter Notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter)
  * [annotation](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter/annotation)
  * [evalulation](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter/enterprise/eval)
  * [training](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter/training)
* [Tutorial Notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/tutorials)
  * [Jupyter](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/tutorials/old_generation_notebooks/jupyter)
  * [Colab](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/tutorials/old_generation_notebooks/colab) (for Google Colab)
* [Databricks Notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/databricks)

## Python Setup

```bash
$ java -version
# should be Java 8 (Oracle or OpenJDK)
$ conda create -n sparknlp python=3.7 -y
$ conda activate sparknlp
# spark-nlp by default is based on pyspark 3.x
$ pip install spark-nlp pyspark
```

## Colab setup

```sh
# This is only to setup PySpark and Spark NLP on Colab
!wget http://setup.johnsnowlabs.com/colab.sh -O - | bash
```

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
