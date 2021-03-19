object DeidentificationExample extends App{

        val trainDataSet=CoNLL().readDataset(SparkAccessor.spark,"src/test/resources/de-identification/train_dataset_main_small.csv")
        var nerDlModel=NerDLModel.pretrained().setOutputCol("ner").setInputCols("sentence","token","glove")
        var nerCrfModel=NerCrfModel.pretrained().setOutputCol("ner").setInputCols("sentence","token","pos","glove")
        val embeddingsFile="src/test/resources/ner-corpus/embeddings.100d.test.txt"

        val emptyDataset=Seq(
        ""
        ).toDS.toDF("text")

        val documentAssembler=new DocumentAssembler()
        .setInputCol("text")
        .setOutputCol("document")

        val sentenceDetector=new SentenceDetector()
        .setInputCols(Array("document"))
        .setOutputCol("sentence")
        .setUseAbbreviations(true)

        val tokenizer=new Tokenizer()
        .setInputCols(Array("sentence"))
        .setOutputCol("token")


        val embeddings=WordEmbeddingsModel
        .pretrained("embeddings_clinical","en","clinical/models")
        .setInputCols(Array("sentence","token"))
        .setOutputCol("embeddings")

        val clinical_sensitive_entities=NerDLModel.pretrained("ner_deid_synthetic","en","clinical/models")
        .setInputCols(Array("sentence","token","embeddings")).setOutputCol("ner")

        val nerConverter=new NerConverter()
        .setInputCols(Array("sentence","token","ner"))
        .setOutputCol("ner_chunk")

        val deIdentification=new DeIdentification()
        .setInputCols(Array("ner_chunk","token","sentence"))
        .setOutputCol("dei")
        .setConsistentObfuscation(true)
        .setMode("obfuscate")
        .setObfuscateRefSource("faker")


        val pipeline=new Pipeline()
        .setStages(Array(
        documentAssembler,
        sentenceDetector,
        tokenizer,
        embeddings,
        clinical_sensitive_entities,
        nerConverter,
        deIdentification
        )).fit(emptyDataset)

        val testDataset=Seq(
        "Record date : 2093-01-13 , David Hale , M.D . , Name : Hendrickson , Ora MR . # 7194334 Date : 01/13/93 PCP : "+
        "Oliveira , 25 years-old , Record date : 2079-11-09 . Cocke County Baptist Hospital . 0295 Keats Street"
        ).toDS.toDF("text")

        val deIdentificationDataFrame=pipeline.transform(testDataset)
        val dataframe=deIdentificationDataFrame.select("dei.result")
        dataframe.show(truncate=false)
        }
