from pyspark.ml import Pipeline
from pyspark.ml import PipelineModel
from pyspark.sql import functions as F
from pyspark.sql import SparkSession

from sparkocr.utils import display_images
from sparkocr.transformers import *
from sparkocr.enums import *
from sparkocr.utils import to_pil_image

from typing import Optional, List, IO
import pandas as pd
import xml.etree.ElementTree as ET
from lxml import etree
import matplotlib.pyplot as plt
from IPython.display import Image 
from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageColor
import re
import os
import random
from collections import OrderedDict

label2color = dict()
colors = ['aqua', 'aquamarine', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'cornflowerblue', 'crimson', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkkhaki', 'darkmagenta',
          'darkolivegreen', 'darkorange', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dodgerblue', 'fuchsia', 'firebrick', 'gold', 'goldenrod', 'green', 'greenyellow', 'hotpink',
          'indianred', 'indigo', 'indianred', 'khaki', 'lightblue', 'lightcoral', 'lightgoldenrodyellow', 'lightgreen', 'lightgray', 'lightgrey', 'lightpink', 'limegreen', 'lightsalmon', 'magenta', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumspringgreen', 'mediumseagreen', 'mediumvioletred',
          'midnightblue', 'navy', 'olive', 'orange', 'orangered', 'peru', 'pink', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'sienna', 'violet', 'tan', 'tomato', 'thistle',
          'yellow', 'yellowgreen'] 

label2rgb = dict()
colors_rgb = [(0, 255, 255), (127, 255, 212), (0, 0, 0), (255, 235, 205), (0, 0, 255), (138, 43, 226), (165, 42, 42), (222, 184, 135), (95, 158, 160), (127, 255, 0), (210, 105, 30), (100, 149, 237), (220, 20, 60), (0, 0, 139), (0, 139, 139), (184, 134, 11), (169, 169, 169), (0, 100, 0), (189, 183, 107), (139, 0, 139) ,
              (85, 107, 47), (255, 140, 0), (139, 0, 0), (233, 150, 122), (143, 188, 143), (72, 61, 139), (47, 79, 79), (0, 206, 209), (148, 0, 211), (255, 20, 147), (0, 191, 255), (105, 105, 105), (30, 144, 255), (255, 0, 255), (178, 34, 34), (255, 215, 0), (218, 165, 32), (0, 128, 0), (173, 255, 47), (255, 105, 180) ,
              (205, 92, 92), (75, 0, 130), (205, 92, 92), (240, 230, 140), (173, 216, 230), (240, 128, 128), (250, 250, 210), (144, 238, 144), (211, 211, 211), (211, 211, 211), (255, 182, 193), (50, 205, 50), (255, 160, 122), (255, 0, 255), (0, 0, 205), (186, 85, 211), (147, 112, 219), (0, 250, 154), (60, 179, 113), (199, 21, 133) ,
              (25, 25, 112), (0, 0, 128), (128, 128, 0), (255, 165, 0), (255, 69, 0), (205, 133, 63), (255, 192, 203), (128, 0, 128), (102, 51, 153), (255, 0, 0), (188, 143, 143), (139, 69, 19), (250, 128, 114), (244, 164, 96), (46, 139, 87), (160, 82, 45), (238, 130, 238), (210, 180, 140), (255, 99, 71), (216, 191, 216) ,
              (255, 255, 0), (154, 205, 50)]

def OCR_pipeline(spark, pdf_path, ner_pipeline, chunk_col="ner_chunk") :
    
    # Read Pdf as image
    pdf_to_image = PdfToImage()\
        .setInputCol("content")\
        .setOutputCol("image_raw")\
        .setResolution(400)

    # Extract text from image
    ocr = ImageToText() \
        .setInputCol("image_raw") \
        .setOutputCol("text") \
        .setIgnoreResolution(False) \
        .setPageIteratorLevel(PageIteratorLevel.SYMBOL) \
        .setPageSegMode(PageSegmentationMode.SPARSE_TEXT) \
        .setWithSpaces(True) \
        .setConfidenceThreshold(70)

    hocr = ImageToHocr() \
        .setInputCol("image_raw") \
        .setOutputCol("hocr") \
        .setIgnoreResolution(False) \
        .setOcrParams(["preserve_interword_spaces=0"])\
        .setPageIteratorLevel(PageIteratorLevel.SYMBOL)\
        .setPageSegMode(PageSegmentationMode.SPARSE_TEXT) 

    
    pipeline_stages = [pdf_to_image, ocr, hocr] + ner_pipeline.stages 
    ocr_pipeline = PipelineModel(stages = pipeline_stages)

    print("OCR pipeline is running...")
 
    pdfs = spark.read.format("binaryFile").load(pdf_path)
    result = ocr_pipeline.transform(pdfs).cache()

    return result


def hocr_to_dataframe(hocr):
    with open ("hocr_content.xml",'w',encoding='utf-8') as f:
        f.write(str(hocr))
    doc = etree.parse("hocr_content.xml")
    words    = []
    wordConf = []
    fonts    = []
    sizes    = []
    font     = -1
    size     = -1
    for path in doc.xpath('//*'):
        
        try:
            if 'ocr_line' in path.values():
                a = float(path.values()[2].split(';')[3].split()[1])
                b = float(path.values()[2].split(';')[4].split()[1])
                font  = round((a+b)/2, 2)
                size = float(path.values()[2].split(';')[2].split()[1])

            if 'ocrx_word' in path.values():
                conf = [x for x in path.values() if 'x_wconf' in x][0]
                wordConf.append((conf.split('bbox ')[1].split(";")[0].split()))
                words.append(path.text)
                fonts.append(font)
                sizes.append(int(size))
        except:
            pass
    dfReturn = pd.DataFrame({'word' : words,
                             'bbox' : wordConf,
                             'borders':fonts,
                             'size':sizes})
    try:
        dfReturn = dfReturn[dfReturn['word'].str.strip()!=''].reset_index(drop=True)
    except:
        pass
    os.remove("hocr_content.xml")
    return(dfReturn)


def get_token_df(text):
    try:
        tokens, borders = zip(*[(m.group(0), (m.start(), m.end()-1)) for m in re.finditer(r'\S+', text)])
        tuples = [(x, y[0], y[1]) for x,y in zip(tokens, borders)]
    except:
        tuples = [('-',0,0)]
    df = pd.DataFrame(tuples, columns=['token','start','end'])
    return df


def get_mapping(text, hocr=None):
    hdf = hocr_to_dataframe(hocr)
    token_df = get_token_df(text)
    token_df['start'] = token_df['start'].astype(int)
    token_df['end'] = token_df['end'].astype(int)
    token_df = pd.concat([hdf, token_df], axis=1)[['token','start','end','bbox','borders','size']]
    token_df['h'] = token_df.bbox.apply(lambda x: int(x[3])-int(x[1]) if type(x) is not float else 0)
    return token_df

def get_coordinates_frame(ent_dict_list, text, hocr):
    token_df = get_mapping(text, hocr)
    new_ent_dict_list = []

    for entity in ent_dict_list:
        if "\n" in entity["chunk"]:
            part_0_chunk = entity["chunk"].split("\n")[0]
            part_1_chunk = entity["chunk"].split("\n")[1]
            part_0_begin = entity["begin"]
            part_0_end = part_0_begin + entity["chunk"].find("\n")-1
            part_1_begin = part_0_begin + entity["chunk"].find("\n")+1
            part_1_end = entity["end"]          
            new_ent_dict_list.append({ 'begin': part_0_begin,
                                       'end': part_0_end,
                                       'chunk': part_0_chunk,
                                       'ner_label': entity["ner_label"],
                                       'sentence_id': entity["sentence_id"]})        
            new_ent_dict_list.append({ 'begin': part_1_begin,
                                       'end': part_1_end,
                                       'chunk': part_1_chunk,
                                       'ner_label': entity["ner_label"],
                                       'sentence_id': entity["sentence_id"]})
            
        else:
            new_ent_dict_list.append({ 'begin': entity["begin"],
                                       'end': entity["end"],
                                       'chunk': entity["chunk"],
                                       'ner_label': entity["ner_label"],
                                       'sentence_id': entity["sentence_id"]})

    for i,ent in enumerate(new_ent_dict_list):
        ix = list(set(token_df[(token_df.start>=ent['begin'])|(token_df.end>=ent['begin'])].index).intersection(set(token_df[(token_df.start<=ent['end']+1)|(token_df.end<=ent['end']+1)].index)))
        coords = token_df.loc[ix,'bbox'].values
        if len(coords)>0:
            xo_list = [] 
            x1_list = []
            yo_list = []
            y1_list = []
            for box in coords:
                try:
                    xo_list.append(int(box[0]))
                    yo_list.append(int(box[1]))
                    x1_list.append(int(box[2]))
                    y1_list.append(int(box[3]))
                except:
                    xo_list.append(0)
                    yo_list.append(0)
                    x1_list.append(0)
                    y1_list.append(0)
            ent['coord'] = (min(xo_list), min(yo_list), max(x1_list), max(y1_list))
        else:
            ent['coord'] = []
    coord_df_pipe = pd.DataFrame(new_ent_dict_list)
    return coord_df_pipe

def save_color_chart(style, color_chart_path = 'color_chart.png'):
    global label2color,label2rgb
    if style == "colored":
        label2color_sorted = OrderedDict(sorted(label2color.items()))
    
    #highlight
    else:                                             
        label2color_sorted = OrderedDict(sorted(label2rgb.items()))

    n = len(label2color_sorted)
    cols        = 4
    rows        = ((n-1) // cols) +1
    cellHeight  = 30
    cellWidth   = 250
    imgHeight   = cellHeight * rows
    imgWidth    = cellWidth * cols
    i = Image.new( "RGB", (imgWidth,imgHeight), (0,0,0) )
    a = ImageDraw.Draw( i )

    for idx, name in enumerate(label2color_sorted):
        y0 = cellHeight * (idx // cols)
        y1 = y0 + cellHeight
        x0 = cellWidth * (idx % cols)
        x1 = x0 + (cellWidth / 4)
        a.rectangle( [ x0, y0, x1, y1 ], fill=label2color_sorted[name], outline= "black")
        a.text( ( x1+1, y0+10 ), name, fill='white' )
        
    i.save(color_chart_path)
    print(f"Color chart of the entity labels is saved to {color_chart_path}.")

def conv_rgba_to_rgb(_rgba):
    _rgb = Image.new('RGB', _rgba.size, (255, 255, 255))
    _rgb.paste(_rgba, mask=_rgba.split()[3])
    return _rgb

def save_file(image_list, file_name, style, save_dir):
    print("Saving started...")
    images = [conv_rgba_to_rgb(_f) for _f in image_list]
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    images[0].save(f"{save_dir}/{file_name}_{style}.pdf", "PDF", resolution=72.0, save_all=True, append_images=images[1:])
    print(f"File saved to {save_dir}/{file_name}_{style} successfully.")


def draw_black_box(img_pil_deid, coord_df, label, label_color): 

    overlay = Image.new('RGBA', img_pil_deid.size, (0,0,0,0)) # black
    draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
    for i,row in coord_df.iterrows():
        point = row['coord']
        pred_label = row['ner_label'].lower()
        draw.rectangle((row['coord'][:2], row['coord'][2:]), fill=(0,0,0,255), outline=(0,0,0,255), width=5)

        if label == True:
            label_position = tuple([row['coord'][0], row['coord'][1]-10])
            draw.text(label_position, text = row['ner_label'], fill= label_color)
        else: pass

    # Alpha composite these two images together to obtain the desired result.
    img = Image.alpha_composite(img_pil_deid, overlay)
    img = img.convert("RGBA") # Remove alpha for saving in jpg format.
   
    return img

def black_box(result, file_name, style, chunk_col, save_dir = "Black_Box", label = False, label_color = "black", display_result=False):
    print("Drawing black box...")
    image_list = []  # append highlighted images
    res_pd = result.selectExpr("pagenum", f"{chunk_col}.begin", f"{chunk_col}.end", f"{chunk_col}.result", f"{chunk_col}.metadata").toPandas()
    res_pd = res_pd.explode(["begin", "end", "result", "metadata"])
    res_pd = res_pd.rename(columns = {"result":"chunk"})
    res_pd["ner_label"] = res_pd.metadata.apply(lambda x: x["entity"])
    res_pd["sentence_id"] = res_pd.metadata.apply(lambda x: x["sentence"])
    res_pd.drop("metadata", axis=1, inplace=True)
    file_length = result.count()
    text_list = result.select('text').collect()
    hocr_list = result.select('hocr').collect()

    for row in range(0,file_length):
        text = text_list[row][0]
        hocr =  hocr_list[row][0]     
        ent_dict_list = [{'begin':x.begin, 'end':x.end, 'chunk':x.chunk, 'ner_label':x.ner_label, 'sentence_id':x.sentence_id} for y,x in res_pd[res_pd.pagenum==row].iterrows()]        
        coord_df = get_coordinates_frame(ent_dict_list, text, hocr)
        img_deid = result.select('image_raw').collect()[row][0]
        img_pil_deid = to_pil_image(img_deid, img_deid.mode)
        img_pil_deid = img_pil_deid.convert("RGBA")
        image_list.append(draw_black_box(img_pil_deid, coord_df, label, label_color))

    save_file(image_list, file_name, style, save_dir)

    if display_result==True:
        for i in image_list:
            display(i)
    else: pass


def highlight(img_pil_deid, coord_df, label, label_color, black_list):
    # Make a blank image the same size as the image for the rectangle, initialized
    # to a fully transparent (0% opaque) version of the tint color, then draw a
    # semi-transparent version of the square on it.

    global label2rgb, colors
    TRANSPARENCY = .25  # Degree of transparency, 0-100%
    OPACITY = int(255 * TRANSPARENCY)
    overlay = Image.new('RGBA', img_pil_deid.size, (255,255,0,0)) # yellow
    draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
    for i,row in coord_df.iterrows():
        point = row['coord']

        try: 
            row['ner_label'].lower() in label2rgb.keys()
            pred_label = row['ner_label'].lower()

        except: 
            raise Exception(row['ner_label'].lower(), 'label is not in the classes of ner model.')

        try:
            if pred_label in black_list:
                draw.rectangle((row['coord'][:2], row['coord'][2:]), fill=label2rgb[pred_label]+(255,), outline=label2rgb[pred_label]+(255,), width=5)   
            else:
                draw.rectangle((row['coord'][:2], row['coord'][2:]), fill=label2rgb[pred_label]+(OPACITY,), outline=label2rgb[pred_label]+(OPACITY,), width=5)

        except:
            print("Error in this row:", row)
            continue
    
        if label == True:
            label_position = tuple([row['coord'][0], row['coord'][1]-10])
            draw.text(label_position, text = row['ner_label'], fill= label_color)
        else: pass

    # Alpha composite these two images together to obtain the desired result.
    img = Image.alpha_composite(img_pil_deid, overlay)
    img = img.convert("RGBA") # Remove alpha for saving in jpg format.
   
    return img

def highlighted_box(result, file_name, style, chunk_col, black_list, save_dir = "Highlighted_Box", label = False, label_color = "red", color_chart_path = "color_chart.png", display_result=False):
    global label2rgb, colors_rgb
    print("Highlighting...")
    image_list = []  # append highlighted images
    black_list = list(set([i.lower() for i in black_list])) # lowercase black_list
    res_pd = result.selectExpr("pagenum", f"{chunk_col}.begin", f"{chunk_col}.end", f"{chunk_col}.result", f"{chunk_col}.metadata").toPandas()
    res_pd = res_pd.explode(["begin", "end", "result", "metadata"])
    res_pd = res_pd.rename(columns = {"result":"chunk"})
    res_pd["ner_label"] = res_pd.metadata.apply(lambda x: x["entity"])
    res_pd["sentence_id"] = res_pd.metadata.apply(lambda x: x["sentence"])
    res_pd.drop("metadata", axis=1, inplace=True)
    random.shuffle(colors_rgb) 
    classes = res_pd.ner_label.str.lower().unique()
    label2rgb = dict(zip(classes, colors_rgb))
    file_length = result.count()
    text_list = result.select('text').collect()
    hocr_list = result.select('hocr').collect()

    for row in range(0,file_length):
        text = text_list[row][0]
        hocr =  hocr_list[row][0]     
        ent_dict_list = [{'begin':x.begin, 'end':x.end, 'chunk':x.chunk, 'ner_label':x.ner_label, 'sentence_id':x.sentence_id} for y,x in res_pd[res_pd.pagenum==row].iterrows()]        
        coord_df = get_coordinates_frame(ent_dict_list, text, hocr)
        img_deid = result.select('image_raw').collect()[row][0]
        img_pil_deid = to_pil_image(img_deid, img_deid.mode)
        img_pil_deid = img_pil_deid.convert("RGBA")
        image_list.append(highlight(img_pil_deid, coord_df, label, label_color, black_list))

    save_file(image_list, file_name, style, save_dir)
    save_color_chart("highlight", color_chart_path)

    if display_result==True:
        for i in image_list:
            display(i)
    else: pass

def draw_outline(img_pil_deid, coord_df, label, label_color, black_list):
    global label2color, colors
    draw = ImageDraw.Draw(img_pil_deid)

    for i,row in coord_df.iterrows():
        point = row['coord']

        try: 
            row['ner_label'].lower() in label2color.keys()
            pred_label = row['ner_label'].lower()

        except: 
            raise Exception(row['ner_label'].lower(), 'label is not in the classes of the ner model.')

        try:
            if pred_label in black_list:
                draw.rectangle((row['coord'][:2], row['coord'][2:]), outline=label2color[pred_label], width=5, fill=label2color[pred_label]) 

            else:  
                draw.rectangle((row['coord'][:2], row['coord'][2:]), outline=label2color[pred_label], width=5)
        except:
            print("Error in this row:", row)
            continue

        if label == True:
            label_position = tuple([row['coord'][0], row['coord'][1]-10])
            draw.text(label_position, text = row['ner_label'], fill= label_color)
        else: pass

    return img_pil_deid  

def colored_box(result, file_name, style, chunk_col, black_list, save_dir = "Colored_Box", label = False, label_color = "red", color_chart_path = "color_chart.png", display_result=False) :
    
    global label2color, colors
    print("Drawing colored box...")
    image_list = []  # append images
    black_list = list(set([i.lower() for i in black_list])) # lowercase black_list
    res_pd = result.selectExpr("pagenum", f"{chunk_col}.begin", f"{chunk_col}.end", f"{chunk_col}.result", f"{chunk_col}.metadata").toPandas()
    res_pd = res_pd.explode(["begin", "end", "result", "metadata"])
    res_pd = res_pd.rename(columns = {"result":"chunk"})
    res_pd["ner_label"] = res_pd.metadata.apply(lambda x: x["entity"])
    res_pd["sentence_id"] = res_pd.metadata.apply(lambda x: x["sentence"])
    res_pd.drop("metadata", axis=1, inplace=True)
    random.shuffle(colors) 
    classes = res_pd.ner_label.str.lower().unique()
    label2color = dict(zip(classes, colors))
    file_length = result.count()
    text_list = result.select('text').collect()
    hocr_list = result.select('hocr').collect()

    for row in range(0,file_length):
        text = text_list[row][0]
        hocr =  hocr_list[row][0]
        ent_dict_list = [{'begin':x.begin, 'end':x.end, 'chunk':x.chunk, 'ner_label':x.ner_label, 'sentence_id':x.sentence_id} for y,x in res_pd[res_pd.pagenum==row].iterrows()]
        coord_df = get_coordinates_frame(ent_dict_list, text, hocr)
        img_deid = result.select('image_raw').collect()[row][0]
        img_pil_deid = to_pil_image(img_deid, img_deid.mode)
        img_pil_deid = img_pil_deid.convert("RGBA")
        image_list.append(draw_outline(img_pil_deid, coord_df, label, label_color, black_list))

    save_file(image_list, file_name, style, save_dir)
    save_color_chart("colored", color_chart_path)
    
    if display_result==True:
        for i in image_list:
            display(i)
    else: pass


def ocr_entity_processor(spark:SparkSession, file_path:str, ner_pipeline:PipelineModel, chunk_col:str = "ner_chunk", black_list : Optional[List[str]] = [], 
                         style:str = "bounding_box", save_dir:str = "save_folder", label:bool= False, label_color:str = "red", 
                         color_chart_path:str = "color_chart.png", display_result:bool=False)-> IO:

    """Generates an annotated PDF file using input PDF files 
        :param spark: Spark session with spark-nlp-jsl and spark-ocr jar
        :type spark: SparkSession

        :param file_path: Path to PDF files
        :type file_path: str

        :param ner_pipeline: Fitted NER pipeline
        :type ner_pipeline: PipelineModel

        :param chunk_col: OutputCol name of the chunk in ner pipeline that will be annotated, default 'ner_chunk'
        :type chunk_col: str

        :param black_list: List of NER labels that will be painted over in 'highlight' and 'bounding_box' styles
        :type black_list: list

        :param style:  PDF file proccess style that has 3 options; 
          'black_band': Black bands over the chunks detected by NER pipeline.
          'bounding_box': Colorful bounding boxes around the chunks detected by NER pipeline. Each color represents a different NER label.
          'highlight': Colorful highlights over the chunks detected by NER pipeline. Each color represents a different NER label.
        :type style: str

        :param save_dir: Path for saving folder of proccessed PDF files, defaults to 'save_folder'
        :type save_dir: str

        :param label: Set to True to write NER labels over the chunks, defaults to False
        :type label: bool

        :param label_color: Color of NER labels if 'label=True' , defaults to "red"
        :type label_color: str

        :param color_chart_path: File name of color chart in PNG format that shows the colors of NER labels in the processed file, defaults to "color_chart.png"
        :type color_chart_path: str

        :param display_result: Set to True to see the output of processed file, defaults to False
        :type display_result: bool

        :return: PDF file
        :rtype: IO
    """

    global colors

    results = OCR_pipeline(spark, pdf_path = file_path, ner_pipeline = ner_pipeline, chunk_col = chunk_col)

    for i in results.select('path').distinct().collect():
        result = results[results.path == i.path]
        file_name = i.path.split("/")[-1].split(".")[0]

        if style == "bounding_box":
            if (label == True) and (label_color not in colors):
                raise Exception(f"{label_color} is not a valid color. Please pick one:{colors}")
            else:
                colored_box(result,file_name, style, chunk_col, black_list, save_dir, label, label_color, color_chart_path, display_result)    

        elif style == "highlight":
            if (label == True) and (label_color not in colors):
                raise Exception(f"{label_color} is not a valid color. Please pick one:{colors}")
            else:
                highlighted_box(result, file_name, style, chunk_col, black_list, save_dir, label, label_color, color_chart_path, display_result)

        elif style == "black_band" :
            if (label == True) and (label_color not in colors):
                raise Exception(f"{label_color} is not a valid color. Please pick one:{colors}")
            else: 
                black_box(result, file_name, style, chunk_col, save_dir, label, label_color, display_result)

        else:
            raise Exception(style, "is not a valid option. Please try one: ['bounding_box', 'highlight', 'black_band']")
