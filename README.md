<a href="https://johnsnowlabs.com"><img src="https://www.johnsnowlabs.com/wp-content/uploads/2020/03/johnsnowlabs-square.png" width="125" height="125" align="right" /></a>

# Spark NLP Workshop

<p align="center">
    <a href="https://github.com/JohnSnowLabs/spark-nlp/actions" alt="build">
        <img src="https://github.com/JohnSnowLabs/spark-nlp/workflows/build/badge.svg" /></a>
    <a href="https://github.com/JohnSnowLabs/spark-nlp/releases" alt="Current Release Version">
        <img src="https://img.shields.io/github/v/release/JohnSnowLabs/spark-nlp.svg?style=flat-square&logo=github" /></a>
    <a href="https://search.maven.org/artifact/com.johnsnowlabs.nlp/spark-nlp_2.12" alt="Maven Central">
        <img src="https://maven-badges.herokuapp.com/maven-central/com.johnsnowlabs.nlp/spark-nlp_2.12/badge.svg" /></a>
    <a href="https://badge.fury.io/py/spark-nlp" alt="PyPI version">
        <img src="https://badge.fury.io/py/spark-nlp.svg" /></a>
    <a href="https://anaconda.org/JohnSnowLabs/spark-nlp" alt="Anaconda-Cloud">
        <img src="https://anaconda.org/johnsnowlabs/spark-nlp/badges/version.svg" /></a>
    <a href="https://github.com/JohnSnowLabs/spark-nlp/blob/master/LICENSE" alt="License">
        <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" /></a>
    <a href="https://pypi.org/project/spark-nlp/" alt="PyPi downloads">
        <img src="https://static.pepy.tech/personalized-badge/spark-nlp?period=total&units=international_system&left_color=grey&right_color=orange&left_text=pip%20downloads" /></a>
</p>

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
$ python3 -m venv .sparknlp-env
$ source .sparknlp-env/bin/activate
# spark-nlp by default is based on pyspark 3.x
$ pip install pyspark==3.1.2
$ pip install spark-nlp
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
