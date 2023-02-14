import random
from IPython.core.display import display, HTML


def get_color():
    r = lambda: random.randint(100,255)
    return '#%02X%02X%02X' % (r(),r(),r())


def chunk_highlighter (annotated_text, entity_column='ner_chunk'):
  
    from spacy import displacy

    label_list = []
    sent_dict_list = []
    
    for n in annotated_text[entity_column]:

        ent = {'start': n.begin, 'end':n.end+1, 'label':n.metadata['entity'].upper()}
        
        label_list.append(n.metadata['entity'].upper())

        sent_dict_list.append(ent)
   
    document_text = [{'text':annotated_text['document'][0].result, 'ents':sent_dict_list,'title':None}]

    label_list = list(set(label_list))
                
    label_color={}
    
    for l in label_list:
        
        label_color[l]=get_color()
    
    colors = {k:label_color[k] for k in label_list}
        
    
    html_text = displacy.render(document_text, style='ent', jupyter=True, manual=True, options= {"ents": label_list, 'colors': colors})

    return html_text


def token_highlighter (light_data):
    
    html_output=''
    
    label_list = list(set([i.split('-')[1] for i in light_data['ner'] if i!='O']))
        
    label_color={}
    
    for l in label_list:
        
        label_color[l]=get_color()
            
    for index, this_token in enumerate(light_data['token']):

        try:
            ent = light_data['ner'][index].split('-')[1]
        except:
            ent = light_data['ner'][index]
        
       
        if ent in label_list:
            color = label_color[ent]
            html_output+='<SPAN style="background-color: {}">'.format(color) + this_token + " </SPAN>"
        else:
            html_output+=this_token + " "
        

    html_output += '<br>'
    html_output += '<br>Color codes:'
    html_output += '<br>'
        
    for l in label_list:
        
        html_output += '<SPAN style="background-color: {}">{}</SPAN>, '.format(label_color[l],l)
   
    
    return html_output
    