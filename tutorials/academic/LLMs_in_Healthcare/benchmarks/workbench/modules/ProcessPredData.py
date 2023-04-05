## Version 2
import re
import json
from json import JSONDecoder

import logging
from modules.log_module import setup_logger
logger = setup_logger('ProcessPredData', level=logging.DEBUG)

def generate_start_end_index(text, word):
    try:
        word = re.escape(word)
        matches = re.finditer(r"\b" + word + r"\b", text)
        indexes = []
        for match in matches:
            try:
                start_index = match.start()
                end_index = match.end()
                indexes.append([start_index, end_index])
            except:
                indexes.append([])
        return indexes
    except Exception as e:
        logger.error(f"generate_start_end_index function error {e}")
        return []


def corrected_json(query_result):
    try:
        # text = query_result['choices'][0]['text']
        text = query_result["choices"][0]['message']['content']
        # Remove leading and trailing whitespaces
        text = text.strip()
        text = text.replace('{{', '{').replace('}}', '}')
        # Extract the JSON string from the text
        start_index = text.find('{')
        text = text.replace("'", '"')
        text = text[start_index:]
        # Load the JSON string as a dictionary
        json_result = json.loads(text)
    except Exception as e:
        logger.error(f"corrected_json function error :malformed or empty prediction from gpt api... skipping this sentence")
        json_result = {}
    return json_result


def get_list_of_entities(json_result, sentence):
    try:
        temp_list_of_entities = []
        text = sentence

        for item in json_result['list_of_entities']:
            try:
                temp_dict = dict()
                temp_dict['entity_type'] = item['entity_type']
                word = temp_dict['chunk'] = item['chunk']
                index_list_of_same_chunks = [x['start-end'] for x in temp_list_of_entities if x['entity_type'] == item['entity_type'] and word == x['chunk']]
                if len(index_list_of_same_chunks) > 0:
                    last_index = max(index_list_of_same_chunks, key=lambda x: x[1])
                    if last_index is not None and word in text[last_index[1]:]:
                        start_index = last_index[1] + text[last_index[1]:].index(word)
                    else:
                        start_index = text.find(word)
                    end_index = start_index + len(word)
                    temp_dict['start-end'] = [start_index, end_index]
                else:
                    temp_dict['start-end'] = generate_start_end_index(text, word)
                if temp_dict['start-end'] != []:
                    temp_list_of_entities.append(temp_dict)
            except:
                pass
        return temp_list_of_entities
    except Exception as e:
        #logger.error(f"get_list_of_entities function error :malformed or empty prediction from gpt api.. skipping this sentence")
        return []