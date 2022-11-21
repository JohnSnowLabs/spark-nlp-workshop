# Legal NLP Pipelines on java grpc
This is the code used to reproduce the results given [here](https://medium.com/@jjmcarrascosa/low-latency-real-time-legal-ai-with-spark-nlp-on-grpc-a2f9b899de92).

With gRPC on java, we can add at least 50 models to a LightPipeline and get an inference time of 0.5s per 1024 characters.
If you run gRPC on a cluster, you can scale the number of LightPipelines you can serve via, for example, and API.

To run this:
1) Put the licensed Legal NLP jar somewhere in the project, for example, in src/jars.
2) Change the path in Utils (JAR_PATH) to reflect that path;
3) In Spark NLP Manager class, `_setEnvVars()` function, add your license info, from the license json you got from John Snow Labs. Please, don't use this method for authentication in production, use it just for testing purposes.

To benchmark:
1) Change the number of models you want to load in a pipeline. Possible values: 1, 10, 100, 200, 300;
2) Change the number of calls you want to do to average the time;
3) Change the number of workers you want to deploy in your machine to attend the petition;
