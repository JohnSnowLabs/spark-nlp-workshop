import pandas as pd
import xml.etree.ElementTree as ET
from lxml import etree
import matplotlib.pyplot as plt
from IPython.display import Image 
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import re

def hocr_to_dataframe(hocr):
    with open ("demo_hocr_content.xml",'w',encoding='utf-8') as f:
        f.write(str(hocr))
    doc = etree.parse("demo_hocr_content.xml")
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
    for i,ent in enumerate(ent_dict_list):
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
    coord_df_pipe = pd.DataFrame(ent_dict_list)
    return coord_df_pipe


label2color = {'problem':'blue', 'test':'green', 'treatment':'orange', 'street':'red', 
               'phone':'purple', 'fax':'pink', 'city':'magenta', 'date':'cyan', 
               'zip':'coral', 'doctor': 'greenyellow', 'other':'yellow'}

def iob_to_label(label):
    if label not in label2color.keys():
        return 'other'
    else:
        return label

def draw_outline(img_pil_deid, coord_df):
    draw = ImageDraw.Draw(img_pil_deid)


    for i,row in coord_df.iterrows():
        point = row['coord']
        pred_label = iob_to_label(row['ner_label'].lower())
        draw.rectangle((row['coord'][:2], row['coord'][2:]), outline=label2color[pred_label], width=5)
    # image_list.append(img_pil_deid) 
    display(img_pil_deid)

TINT_COLOR = (255, 255, 0)  # yellow
TRANSPARENCY = .25  # Degree of transparency, 0-100%
OPACITY = int(255 * TRANSPARENCY)

def highlight(img_pil_deid, coord_df):
    # draw = ImageDraw.Draw(img_pil_deid)

    # Make a blank image the same size as the image for the rectangle, initialized
    # to a fully transparent (0% opaque) version of the tint color, then draw a
    # semi-transparent version of the square on it.
    overlay = Image.new('RGBA', img_pil_deid.size, TINT_COLOR+(0,))
    draw = ImageDraw.Draw(overlay)  # Create a context for drawing things on it.
    for i,row in coord_df.iterrows():
        point = row['coord']
        pred_label = iob_to_label(row['ner_label'].lower())
        draw.rectangle((row['coord'][:2], row['coord'][2:]), fill=TINT_COLOR+(OPACITY,), outline=TINT_COLOR+(OPACITY,), width=5)

    # Alpha composite these two images together to obtain the desired result.
    img = Image.alpha_composite(img_pil_deid, overlay)
    img = img.convert("RGBA") # Remove alpha for saving in jpg format.
    # highlighted_image_list.append(img) 
    display(img)
