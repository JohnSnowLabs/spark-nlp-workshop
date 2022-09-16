# Databricks notebook source
# MAGIC %md
# MAGIC # Spark OCR in Healthcare
# MAGIC 
# MAGIC Spark OCR is a commercial extension of Spark NLP for optical character recognition from images, scanned PDF documents, Microsoft DOCX and DICOM files. 
# MAGIC 
# MAGIC In this notebook we will:
# MAGIC   - Import clinical notes in pdf format and store in delta
# MAGIC   - Convert pdfs to imgage and improve mage quality
# MAGIC   - Extract text from pdfs and store resulting text data in delta 

# COMMAND ----------

import os
import json
import string
#import sys
#import base64
import numpy as np
import pandas as pd

import sparknlp
import sparknlp_jsl
from sparknlp.base import *
from sparknlp.util import *
from sparknlp.annotator import *
from sparknlp_jsl.base import *
from sparknlp_jsl.annotator import *
from sparknlp.pretrained import ResourceDownloader

import sparkocr
from sparkocr.transformers import *
from sparkocr.utils import *
from sparkocr.enums import *

from pyspark.sql import functions as F
from pyspark.ml import Pipeline, PipelineModel
from sparknlp.training import CoNLL

import matplotlib.pyplot as plt

pd.set_option('max_colwidth', 100)
pd.set_option('display.max_columns', 100)  
pd.set_option('display.expand_frame_repr', False)

spark.sql("set spark.sql.legacy.allowUntypedScalaUDF=true")

print('sparknlp.version : ',sparknlp.version())
print('sparknlp_jsl.version : ',sparknlp_jsl.version())
print('sparkocr : ',sparkocr.version())

spark

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Initial Configurations

# COMMAND ----------

# MAGIC %run ./03-config

# COMMAND ----------

solacc_settings=SolAccUtil('phi_ocr')
solacc_settings.print_paths()

# COMMAND ----------

# DBTITLE 1,download pdf files
remote_url='https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/data/ocr'
for i in range(0,3):
  solacc_settings.load_remote_data(f'{remote_url}/MT_OCR_0{i}.pdf')
dbutils.fs.ls(solacc_settings.data_path)

# COMMAND ----------

pdfs_df = spark.read.format("binaryFile").load(f'{solacc_settings.data_path}/*.pdf').sort('path')
print("Number of files in the folder : ", pdfs_df.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0.1. Write pdf files to delta bronze layer

# COMMAND ----------

pdfs_bronze_df = pdfs_df.selectExpr('sha1(path) as id','*')
display(pdfs_bronze_df)

# COMMAND ----------

pdfs_bronze_df.write.mode('overwrite').save(f'{solacc_settings.delta_path}/bronze/notes_pdfs')

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Parsing the Files through OCR (create bronze layer)

# COMMAND ----------

# MAGIC %md
# MAGIC - The pdf files can have more than one page. We will transform the document in to images per page. Than we can run OCR to get text. 
# MAGIC - We are using `PdfToImage()` to render PDF to images and `ImageToText()` to runs OCR for each images.  

# COMMAND ----------

pdf_df=spark.read.load(f'{solacc_settings.delta_path}/bronze/notes_pdfs')

# COMMAND ----------

# Transform PDF document to images per page
pdf_to_image = PdfToImage()\
      .setInputCol("content")\
      .setOutputCol("image")

# Run OCR
ocr = ImageToText()\
      .setInputCol("image")\
      .setOutputCol("text")\
      .setConfidenceThreshold(65)\
      .setIgnoreResolution(False)

ocr_pipeline = PipelineModel(stages=[
    pdf_to_image,
    ocr
])

# COMMAND ----------

# MAGIC %md
# MAGIC - Now, we can transform the `pdfs` with our pipeline.

# COMMAND ----------

ocr_result_df = ocr_pipeline.transform(pdfs_df)

# COMMAND ----------

# MAGIC %md
# MAGIC - After transforming we get following columns :
# MAGIC 
# MAGIC   - path
# MAGIC   - modificationTime
# MAGIC   - length
# MAGIC   - image
# MAGIC   - total_pages
# MAGIC   - pagenum
# MAGIC   - documentnum
# MAGIC   - confidence
# MAGIC   - exception
# MAGIC   - text
# MAGIC   - positions

# COMMAND ----------

display(
  ocr_result_df.select('modificationTime', 'length', 'total_pages', 'pagenum', 'documentnum', 'confidence', 'exception')
)

# COMMAND ----------

display(ocr_result_df.select('path', 'image', 'text', 'positions'))

# COMMAND ----------

# MAGIC %md
# MAGIC - Now, we have our pdf files in text format and as image. 
# MAGIC 
# MAGIC - Let's see the images and the text.

# COMMAND ----------

import matplotlib.pyplot as plt

img = ocr_result_df.collect()[0].image
img_pil = to_pil_image(img, img.mode)

plt.figure(figsize=(24,16))
plt.imshow(img_pil, cmap='gray')
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC - Let's see extracted text which is stored in `'text'` column as a list. Each line is is an item in this list, so we can join them and see the whole page.

# COMMAND ----------

print("\n".join([row.text for row in ocr_result_df.select("text").collect()[0:1]]))

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1.1. Skew Correction
# MAGIC 
# MAGIC In some images, there may be some skewness and this reduces acuracy of the extracted text. Spark OCR has `ImageSkewCorrector` which detects skew of the image and rotates it. 

# COMMAND ----------

from pyspark.sql.types import *
new_schema = StructType([
                StructField('origin',StringType(),'true'),
                StructField('height',IntegerType(),'false'),
                StructField('width',IntegerType(),'false'),
                StructField('nChannels',IntegerType(),'false'),
                StructField('mode',IntegerType(),'false'),
                StructField('resolution',IntegerType(),'false'),
                StructField('data',BinaryType(),'true')
              ])
new_img_schema = StructType([StructField('image',new_schema,'true')])

# COMMAND ----------

# Image skew corrector 
pdf_to_image = PdfToImage()\
      .setInputCol("content")\
      .setOutputCol("image")

skew_corrector = ImageSkewCorrector()\
      .setInputCol("image")\
      .setOutputCol("corrected_image")\
      .setAutomaticSkewCorrection(True)

ocr = ImageToText()\
      .setInputCol("corrected_image")\
      .setOutputCol("text")\
      .setConfidenceThreshold(65)\
      .setIgnoreResolution(False)

ocr_skew_corrector = PipelineModel(stages=[
    pdf_to_image,
    skew_corrector,
    ocr
])

# COMMAND ----------

ocr_skew_corrected_result_df = ocr_skew_corrector.transform(pdf_df).cache()

# COMMAND ----------

# MAGIC %md
# MAGIC Let's see the results after the skew correction.

# COMMAND ----------

# DBTITLE 1,Original Images
ocr_result_df.select('path', 'confidence').filter("path rlike 'MT_OCR_01.pdf'").limit(1).display()

# COMMAND ----------

# DBTITLE 1,Skew Corrected Images
ocr_skew_corrected_result_df.select('path', 'confidence').filter("path rlike 'MT_OCR_01.pdf'").limit(1).display()

# COMMAND ----------

# MAGIC %md
# MAGIC After skew correction, confidence is increased from %48.3 to % %66.5. Let's display the corrected image and the original image side by side.

# COMMAND ----------

img_orig = ocr_skew_corrected_result_df.select("image").collect()[1].image
img_corrected = ocr_skew_corrected_result_df.select("corrected_image").collect()[1].corrected_image

img_pil_orig = to_pil_image(img_orig, img_orig.mode)
img_pil_corrected = to_pil_image(img_corrected, img_corrected.mode)

plt.figure(figsize=(24,16))
plt.subplot(1, 2, 1)
plt.imshow(img_pil_orig, cmap='gray')
plt.title('Original')
plt.subplot(1, 2, 2)
plt.imshow(img_pil_corrected, cmap='gray')
plt.title("Skew Corrected")
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1.2. Image Processing
# MAGIC 
# MAGIC * After reading pdf files, we can process on images to increase the confidency.
# MAGIC 
# MAGIC * By **`ImageAdaptiveThresholding`**, we can compute a threshold mask image based on local pixel neighborhood and apply it to image. 
# MAGIC 
# MAGIC * Another method which we can add to pipeline is applying morphological operations. We can use **`ImageMorphologyOperation`** which support:
# MAGIC   - Erosion
# MAGIC   - Dilation
# MAGIC   - Opening
# MAGIC   - Closing   
# MAGIC 
# MAGIC * To remove remove background objects **`ImageRemoveObjects`** can be used.
# MAGIC 
# MAGIC * We will add **`ImageLayoutAnalyzer`** to pipeline, to analyze the image and determine the regions of text.

# COMMAND ----------

from sparkocr.enums import *

# Read binary as image
pdf_to_image = PdfToImage()\
  .setInputCol("content")\
  .setOutputCol("image")\
  .setResolution(400)

# Correcting the skewness
skew_corrector = ImageSkewCorrector()\
      .setInputCol("image")\
      .setOutputCol("skew_corrected_image")\
      .setAutomaticSkewCorrection(True)

# Binarize using adaptive tresholding
binarizer = ImageAdaptiveThresholding()\
  .setInputCol("skew_corrected_image")\
  .setOutputCol("binarized_image")\
  .setBlockSize(91)\
  .setOffset(50)

# Apply morphology opening
opening = ImageMorphologyOperation()\
  .setKernelShape(KernelShape.SQUARE)\
  .setOperation(MorphologyOperationType.OPENING)\
  .setKernelSize(3)\
  .setInputCol("binarized_image")\
  .setOutputCol("opening_image")

# Remove small objects
remove_objects = ImageRemoveObjects()\
  .setInputCol("opening_image")\
  .setOutputCol("corrected_image")\
  .setMinSizeObject(130)


ocr_corrected = ImageToText()\
  .setInputCol("corrected_image")\
  .setOutputCol("corrected_text")\
  .setPageIteratorLevel(PageIteratorLevel.SYMBOL) \
  .setPageSegMode(PageSegmentationMode.SPARSE_TEXT) \
  .setConfidenceThreshold(65)

# OCR pipeline
image_pipeline = PipelineModel(stages=[
    pdf_to_image,
    skew_corrector,
    binarizer,
    opening,
    remove_objects,
    ocr_corrected
])

# COMMAND ----------

pdf_processed_df = image_pipeline.transform(pdf_df).cache()

# COMMAND ----------

# MAGIC %md
# MAGIC Let's see the original image and corrected image.

# COMMAND ----------

img_orig = pdf_processed_df.select("image").collect()[1].image
img_corrected = pdf_processed_df.select("corrected_image").collect()[1].corrected_image

img_pil_orig = to_pil_image(img_orig, img_orig.mode)
img_pil_corrected = to_pil_image(img_corrected, img_corrected.mode)

plt.figure(figsize=(24,16))
plt.subplot(1, 2, 1)
plt.imshow(img_pil_orig, cmap='gray')
plt.title('Original')
plt.subplot(1, 2, 2)
plt.imshow(img_pil_corrected, cmap='gray')
plt.title("Skew Corrected")
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC After processing, we have cleaner image. And confidence is increased to %97

# COMMAND ----------

print("Original Images")
display(ocr_result_df.filter("path rlike 'MT_OCR_01.pdf'").select('confidence'))

print("Skew Corrected Images")
display(ocr_skew_corrected_result_df.filter("path rlike 'MT_OCR_01.pdf'").select('confidence'))

print("Corrected Images")
display(pdf_processed_df.filter("path rlike 'MT_OCR_01.pdf'").select('confidence'))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Write to Silver
# MAGIC Now after applying image processing and correction to the notes and extracting corrected text, we write the final result in deltalake's silver layer to 

# COMMAND ----------

pdf_processed_silver_df=pdf_processed_df.select('id','path','length','total_pages','documentnum','pagenum','corrected_image','confidence','corrected_text')
pdf_processed_silver_df.display()

# COMMAND ----------

pdf_processed_silver_df.write.mode('overwrite').save(f'{solacc_settings.delta_path}/silver/processed_pdf')

# COMMAND ----------

# MAGIC %md
# MAGIC In the next notebook, we read extracted text from clinical notes, extract PHI entities and obfuscate those entities.