# Spark-NLP Python

There are two directories: `training` and `annotation`. Inside `traning` you will find all the examples which help you to train Spark-NLP models and pipelines. On the other hand, the examples inside `annotation` demonstrate how to use Spark-NLP annotators, pre-trained models, and pre-trained pipelines.

## Setup Spark-NLP

## Python

### Pip

If you installed pyspark through pip, you can install `spark-nlp` through pip as well.

```bash
pip install spark-nlp==2.0.0
```

PyPI [spark-nlp package](https://pypi.org/project/spark-nlp/)

### Conda

If you are using Anaconda/Conda for managing Python packages, you can install `spark-nlp` as follow:

```bash
conda install -c johnsnowlabs spark-nlp
```

Anaconda [spark-nlp package](https://anaconda.org/JohnSnowLabs/spark-nlp)

Then you'll have to create a SparkSession manually, for example:

```bash
spark = SparkSession.builder \
    .appName("ner")\
    .master("local[*]")\
    .config("spark.driver.memory","6G")\
    .config("spark.driver.maxResultSize", "2G") \
    .config("spark.jars.packages", "JohnSnowLabs:spark-nlp:2.0.0")\
    .config("spark.kryoserializer.buffer.max", "500m")\
    .getOrCreate()
```

If using local jars, you can use `spark.jars` instead for a comma delimited jar files. For cluster setups, of course you'll have to put the jars in a reachable location for all driver and executor nodes

## Setup Jupyter Notebook

### Prerequisite: Python

While Jupyter runs code in many programming languages, Python is a requirement
(Python 3.3 or greater, or Python 2.7) for installing the Jupyter Notebook itself.

## Installing Jupyter using Anaconda

We **strongly recommend** installing Python and Jupyter using the [Anaconda Distribution](https://www.anaconda.com/downloads),
which includes Python, the Jupyter Notebook, and other commonly used packages for scientific computing and data science.

First, download [Anaconda](https://www.anaconda.com/downloads). We recommend downloading Anaconda’s latest Python 3 version.

Second, install the version of Anaconda which you downloaded, following the instructions on the download page.

Congratulations, you have installed Jupyter Notebook! To run the notebook, run the following command at the Terminal (Mac/Linux) or Command Prompt (Windows):

```bash
jupyter notebook
```

### Installing Jupyter with pip

As an existing or experienced Python user, you may wish to install Jupyter using Python’s package manager, pip, instead of Anaconda.

If you have Python 3 installed (which is recommended):

```bash
python3 -m pip install --upgrade pip
python3 -m pip install jupyter
```


Congratulations, you have installed Jupyter Notebook! To run the notebook, run
the following command at the Terminal (Mac/Linux) or Command Prompt (Windows):

```bash
jupyter notebook
```

Original reference: [https://jupyter.org/install](https://jupyter.org/install)
