# Spark NLP Workshop

Showcasing notebooks and codes of how to use Spark NLP in Python and Scala.

## Table of contents

* [Jupyter Notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/jupyter)
* [Strata conference](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/strata)
* [Databricks Notebooks](https://github.com/JohnSnowLabs/spark-nlp-workshop/tree/master/databricks)

## Docker setup

If you want to experience Spark NLP and run Jupyter exmaples without installing anything, you can simply use our [Docker image](https://hub.docker.com/r/johnsnowlabs/spark-nlp-workshop):

1. Get the docker image for spark-nlp-workshop:

```bash
docker pull johnsnowlabs/spark-nlp-workshop
```

2. Run the image locally with port binding.

```bash
 docker run -it --rm -p 8888:8888 -p 4040:4040 johnsnowlabs/spark-nlp-workshop
```

3. Open Jupyter notebooks inside your browser by using the token printed on the console.

```bash
http://localhost:8888/?token=LOOK_INSIDE_YOUR_CONSOLE
```

## Main repository

[https://github.com/JohnSnowLabs/spark-nlp](https://github.com/JohnSnowLabs/spark-nlp)

## Project's website

Take a look at our official spark-nlp page: [http://nlp.johnsnowlabs.com/](http://nlp.johnsnowlabs.com/) for user documentation and examples

## Slack community channel

Questions? Feedback? Request access sending an email to nlp@johnsnowlabs.com

## Contributing

If you find any example that is no longer working, please create an [issue](https://github.com/JohnSnowLabs/spark-nlp-workshop/issues).

## License

Apache Licence 2.0
