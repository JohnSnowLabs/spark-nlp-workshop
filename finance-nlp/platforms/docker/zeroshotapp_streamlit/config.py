import os

cores = os.getenv('cores', "1",)

conf = {"spark.driver.memory": os.getenv('spark.driver.memory', "8G"),
        #"spark.executor.heartbeatInterval": "60s",
        #"spark.executor.memory": os.getenv('spark.executor.memory', "4G"),
        "spark.driver.maxResultSize": "1G",
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        "spark.kryoserializer.buffer.max": "2000M"}

HEALTHCHECK_PORT = "8888"
