import os

cores = os.getenv('cores', "1")

conf = {"spark.driver.memory": os.getenv('spark.driver.memory', "8G"),
        "spark.driver.maxResultSize": "1G",
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        "spark.kryoserializer.buffer.max": "2000M"}

FLASK_PORT = "8888"
