object NerConverterInternalExample extends App{

        val data=ResourceHelper.spark.createDataFrame(Seq(Tuple1("My name is Andres and I live in Colombia"))).toDF("text")

        val documentAssembler=new DocumentAssembler()
        .setInputCol("text")
        .setOutputCol("document")

        val sentenceDetector=new SentenceDetector()
        .setInputCols("document")
        .setOutputCol("sentence")
        .setUseAbbreviations(false)

        val tokenizer=new Tokenizer()
        .setInputCols(Array("sentence"))
        .setOutputCol("token")

        val embeddings=WordEmbeddingsModel.pretrained()
        .setInputCols("document","token")
        .setOutputCol("embeddings")
        .setCaseSensitive(false)

        val ner=NerDLModel.pretrained()
        .setInputCols("sentence","token","embeddings")
        .setOutputCol("ner")
        .setIncludeConfidence(true)

        val converter=new NerConverterInternal()
        .setInputCols("sentence","token","ner")
        .setOutputCol("entities")
        .setPreservePosition(false)
        .setThreshold(9900e-4f)

        val recursivePipeline=new RecursivePipeline()
        .setStages(Array(
        documentAssembler,
        sentenceDetector,
        tokenizer,
        embeddings,
        ner,
        converter
        ))

        val nermodel=recursivePipeline.fit(data).transform(data)

        nermodel.select("token.result").show(1,false)
        nermodel.select("embeddings.result").show(1,false)
        nermodel.select("entities.result").show(1,false)
        nermodel.select("entities").show(1,false)
        }
