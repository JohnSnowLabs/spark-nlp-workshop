# Spark-NLP Databricks

## Databricks Scala Notebooks

You can view all the Databricks notebooks from this address in HTML format:

[https://johnsnowlabs.github.io/spark-nlp-workshop/databricks/index.html](https://johnsnowlabs.github.io/spark-nlp-workshop/databricks/index.html)

Note: You can import these notebooks by using their URLs.

## How to use Spark-NLP library in Databricks

1- Right-click the Workspace folder where you want to store the library.

2- Select Create > Library.

3- Select where you would like to create the library in the Workspace, and open the Create Library dialog:

![Databricks](https://databricks.com/wp-content/uploads/2015/07/create-lib.png)

4- From the Source drop-down menu, select **Maven Coordinate:**
![Databricks](https://databricks.com/wp-content/uploads/2015/07/select-maven-1024x711.png)

5- Now, all available **Maven** are at your fingertips! Just search for **com.johnsnowlabs.nlp:spark-nlp_2.11: 2.4.2**

6- Select **spark-nlp** package and we are good to go!

More info about how to use 3rd [Party Libraries in Databricks](https://databricks.com/blog/2015/07/28/using-3rd-party-libraries-in-databricks-apache-spark-packages-and-maven-libraries.html)

## Compatibility

Spark NLP 2.4.5 has been tested and is compatible with the following runtimes:

* 6.2
* 6.2 ML
* 6.3
* 6.3 ML
* 6.4
* 6.4 ML
* 6.5
* 6.5 ML
