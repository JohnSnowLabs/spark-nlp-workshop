# Scale Vision Transformers (ViT) Beyond Hugging Face
## Speed up sate-of-the-art ViT models in Hugging Face 🤗 up to 2300% (25x times faster ) with Databricks, Nvidia, and Spark NLP 🚀

### Datasets

```sh
wget -q https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/resources/en/images/imagenet-mini-sample.zip && unzip /databricks/driver/imagenet-mini-sample.zip >/dev/null 2>&1
wget -q https://s3.amazonaws.com/auxdata.johnsnowlabs.com/public/resources/en/images/imagenet-mini.zip && unzip /databricks/driver/imagenet-mini.zip >/dev/null 2>&1
```


### Dell Server

| Hardware  | Lib  |  Notebook | 
|---|---|---|
| Dell Server  | Hugging Face  |  [nobteook](0-Dell - HuggingFace Image Classification.ipynb) | 
| Dell Server  | Spark NLP  |  [nobteook](0-Dell - Spark NLP Image Classification.ipynb) | 