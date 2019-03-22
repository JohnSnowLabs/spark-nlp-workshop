# Spark-NLP Workshop

Example notebooks and codes of how to use Spark-NLP in Python and Scala.

## Table of contents

* [Jupyter Notebooks](jupyter/)
* [Databricks Notebooks](databricks/)
* [Zeppelin Notes](zeppelin/)
* [Scala Files](scala/)

## Docker setup

1.Get the docker image for spark-nlp-workshop:

```bash
docker pull johnsnowlabs/spark-nlp-workshop
```

2.Run the image locally with port binding and local disk mapping
Note: Replace $local path$ with any local path in your disc

```bash
 docker run -it --rm -p 8888:8888 -p 4040:4040 -v 'pwd':/home/jovyan/strata johnsnowlabs/spark-nlp-workshop
```

3.Run the notebooks on your browser using the token printed on the console.

## Project's website

Take a look at our official spark-nlp page: [http://nlp.johnsnowlabs.com/](http://nlp.johnsnowlabs.com/) for user documentation and examples

## Slack community channel

Questions? Feedback? Request access sending an email to nlp@johnsnowlabs.com

## Contributing

If you find any example that is no longer working, please create an [issue](https://github.com/JohnSnowLabs/spark-nlp-workshop/issues).

## License

Apache Licence 2.0
