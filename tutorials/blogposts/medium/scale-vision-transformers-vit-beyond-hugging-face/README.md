# Scale Vision Transformers (ViT) Beyond Hugging Face
## Speed up sate-of-the-art ViT models in Hugging Face 🤗 up to 2300% (25x times faster ) with Databricks, Nvidia, and Spark NLP 🚀

### Article

This reporsitory contains everything needed to reproduce benchmarks used in this published article: 

["Scale Vision Transformers (ViT) Beyond Hugging Face"](https://hackernoon.com/scale-vision-transformers-vit-beyond-hugging-face) | HackerNoon

### Datasets

```sh
wget -q https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/resources/en/images/imagenet-mini-sample.zip && unzip imagenet-mini-sample.zip >/dev/null 2>&1
wget -q https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/resources/en/images/imagenet-mini.zip && unzip imagenet-mini.zip >/dev/null 2>&1
```


### Dell Server

| Hardware  | Lib  |  Notebook | 
|---|---|---|
| Dell Server  | Hugging Face  |  [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/blogposts/medium/scale-vision-transformers-vit-beyond-hugging-face/0-Dell%20-%20HuggingFace%20Image%20Classification.ipynb) | 
| Dell Server  | Spark NLP  |  [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/blogposts/medium/scale-vision-transformers-vit-beyond-hugging-face/0-Dell%20-%20Spark%20NLP%20Image%20Classification.ipynb) | 


### Databricks

| Hardware  | Lib  |  Notebook | 
|---|---|---|
| Databricks Single Node | Hugging Face  |  [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/blogposts/medium/scale-vision-transformers-vit-beyond-hugging-face/1-Databricks%20-%20HuggingFace%20Image%20Classification.ipynb) | 
| Databricks Single Node  | Spark NLP  |  [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/blogposts/medium/scale-vision-transformers-vit-beyond-hugging-face/1-Databricks%20-%20Spark%20NLP%20Image%20Classification.ipynb) | 
| Databricks Multi Node  | Spark NLP  |  [notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/tutorials/blogposts/medium/scale-vision-transformers-vit-beyond-hugging-face/2-Databricks%20-%20Spark%20NLP%20Image%20Classification%20at%20Scale.ipynb) | 
