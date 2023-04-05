import pandas as pd
import ast
from collections import Counter
import re
from ast import literal_eval
import warnings
warnings.filterwarnings("ignore")

import logging
from modules.log_module import setup_logger

logger = setup_logger('ProcessRawData')

class ProcessData:
    def __init__(self, label_list, entity_count_filter, main_data_path, prediction_source) -> None:
        self.label_list = label_list
        self.entity_count_filter = entity_count_filter
        self.main_data_path  = main_data_path
        self.prediction_source = prediction_source
        self.main_df = self.process_main_df()


    def process_main_df(self):
        print("Processing main csv...")
        if self.main_data_path.split(".")[-1] == "csv":
            self.main_df = pd.read_csv(self.main_data_path)
        if self.main_data_path.split(".")[-1] == "xlsx":
            self.main_df = pd.read_excel(self.main_data_path)
        if self.main_data_path.split(".")[-1] == "pkl":
            self.main_df = pd.read_pickle(self.main_data_path)

        if self.prediction_source == "jsl_ner":
           self.main_df['prediction_list'] =  self.main_df['jsl_prediction']

        if "ground_truth_list" not in self.main_df.columns:
            try:
                self.main_df['ner_label'] = self.main_df['ner_label'].apply(lambda x: ast.literal_eval(x))
            except:
                pass
            try:
                self.main_df['label_count'] = self.main_df['ner_label'].apply(lambda x: dict(Counter(x)))
            except:
                pass
            logger.info(f"main df shape: {self.main_df.shape}")
            return self.main_df

    def get_counts(self, row_values_as_dict):
        res = 0
        for z in self.label_list:
            res += row_values_as_dict.get(z, 0)
        return res

    def get_interim_df(self):
        self.main_df['entity_counts'] = self.main_df.label_count.apply(lambda x: self.get_counts(x))
        filtered_interim_df = self.main_df[self.main_df.entity_counts > self.entity_count_filter ]
        logger.info(f"filtered df shape: {filtered_interim_df.shape}")
        return filtered_interim_df

    def gt_generate_start_end_indexes(self, text, word):
        try:
            word = re.escape(word)
            matches = re.finditer(r"\b" + word + r"\b", text)
            indexes = []
            for match in matches:
                try:
                    start_index = match.start()
                    end_index = match.end()
                    indexes.append({'start': start_index, 'end': end_index})
                except:
                    indexes.append({})
            return indexes[0]['start'], indexes[0]['end'] if indexes else None, None
        except:
            return None, None, None


    def gt_get_list_of_entities(self, text, chunks, labels):
        temp_list_of_entities = []
        for i, chunk in enumerate(chunks):
            temp_dict = {}
            temp_dict['chunk'] = chunk
            temp_dict['entity_type'] = labels[i]

            index_list_of_same_chunks = [x['start-end'] for x in temp_list_of_entities if x['chunk'] == chunk and x['entity_type'] == labels[i]]

            if len(index_list_of_same_chunks) > 0:
                last_index = max(index_list_of_same_chunks, key=lambda x: x[1])
                if last_index is not None and chunk in text[last_index[1]:]:
                    start_index = last_index[1] + text[last_index[1]:].index(chunk)
                else:
                    start_index = text.find(chunk)
                end_index = start_index + len(chunk)
                temp_dict['start-end'] = [start_index, end_index]
            else:
                start, end, _ = self.gt_generate_start_end_indexes(text, chunk)
                if start is not None:
                    temp_dict['start-end'] = [start, end]

            if 'start-end' in temp_dict:
                temp_list_of_entities.append(temp_dict)

        return temp_list_of_entities


    def get_final_df(self):
        df_with_gt_list = self.get_interim_df()
        try:
            df_with_gt_list.loc[:, 'chunk'] = df_with_gt_list['chunk'].apply(lambda x: literal_eval(x))
        except:
            pass
        try:
            df_with_gt_list.loc[:, 'ner_label'] = df_with_gt_list['ner_label'].apply(lambda x: literal_eval(x))
        except:
            pass
        df_with_gt_list.loc[:, 'ground_truth_list'] = [[] for _ in range(len(df_with_gt_list))]
        try:
            df_with_gt_list.loc[:, 'prediction_list'] = [[] for _ in range(len(df_with_gt_list))]
        except:
            pass
        for idx, row in df_with_gt_list.iterrows():
            df_with_gt_list.at[idx, "ground_truth_list"] =  self.gt_get_list_of_entities(row['text'], row['chunk'], row['ner_label'])
        logger.info(f"final df shape: {df_with_gt_list.shape}" )
        return df_with_gt_list