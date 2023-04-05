import pandas as pd
import os

class ProcessBatch:
    def __init__(
        self,
        dataframe,
        ner_extraction,
        corrected_json,
        get_list_of_entities,
        file_name
    ):
        self.dataframe = dataframe
        print(f"Given dataframe shape {dataframe.shape}")
        self.ner_extraction = ner_extraction
        self.corrected_json = corrected_json
        self.get_list_of_entities = get_list_of_entities
        self.file_name = file_name

    def generate_json_result(self, sentence):
        result = self.ner_extraction.do_query(sentence)
        json_result = self.corrected_json(result)
        temp_list_of_entities  = self.get_list_of_entities(json_result, sentence)
        return temp_list_of_entities

    def do_processing(self):
        print("Getting predictions from API started...")
        df = self.dataframe.copy()
        i = 1
        for index, row in df.iterrows():
            try:
                sentence = row['text']
                df.at[index, 'prediction_list'] = self.generate_json_result(sentence)
                if df.at[index, 'prediction_list'] != []:
                    print(f"Query: {i} | index: {index} | status: SUCCESS")
            except Exception as e:
                print(i, index, "FAILED", f"ERROR: {e}")
                df.at[index, 'prediction_list'] = []
            i += 1

        df_filtered = df[df['prediction_list'].apply(lambda x: len(x) != 0)]
        df_filtered = df_filtered[df_filtered['ground_truth_list'].apply(lambda x: len(x) != 0)]
        try:
            df_filtered.to_csv(f"{self.file_name}.csv")
            df_filtered.to_excel(f"{self.file_name}.xlsx")
        except Exception as e:
            print(f"Error: {e}")

        print("Getting predictions from API finished.")
        print(f"final df shape: {df_filtered.shape}")
        print(f"file saved as {self.file_name}.csv ")
        return df