import pandas as pd
import ast
from ast import literal_eval
import os
import warnings
warnings.filterwarnings("ignore")
import logging
from modules.log_module import setup_logger

logger = setup_logger('Evaluation')

class Evaluate:

    def __init__(self, file_path=None, dataframe=None, prediction_source="ChatGPT"):
        self.file_path = file_path
        self.dataframe = dataframe
        self.prediction_source = prediction_source

    def load_data(self):
        # try:
            if self.file_path != None:
                df = pd.read_csv(self.file_path)
                try:
                    df = df[df['prediction_list'].apply(len) != 0]
                except:
                    pass
                # df = pd.read_csv(self.file_path, delimiter="\t")
                # df['ground_truth_list'] = df['ground_truth_list'].apply(lambda x: ast.literal_eval(x.replace("'", "\"")))
                try:
                    df['ground_truth_list'] = df['ground_truth_list'].apply(lambda x: ast.literal_eval(x.replace("'", "\"")))
                    df['prediction_list'] = df['prediction_list'].apply(lambda x: ast.literal_eval(x.replace("'", "\"")))
                except:
                    pass
            else:
                df = self.dataframe.copy()
            return df
        # except Exception as e:
        #     logger.error("An error occurred while loading the data @Evaluate load_data: ", str(e))
        #     return None

    def match_counts(self, predictions, ground_truth, gt_type_dict):
        try:
            full_match = 0
            partial_match = 0
            no_match = 0
            gt = 0
            full_match_chunks = []
            partial_match_chunks = []
            no_match_chunks = []

            def flatten_prediction_list(predictions):
                new_prediction_list = []
                for item in predictions:
                    if len(item['start-end']) > 1:
                        for start_end in item['start-end']:
                            new_item = item.copy()
                            new_item['start-end'] = [start_end]
                            new_item['matched_gt'] = False
                            new_prediction_list.append(new_item)
                    else:
                        new_prediction_list.append(item)
                return new_prediction_list

            if self.prediction_source == "ChatGPT":
                new_prediction_list = flatten_prediction_list(predictions)
            else:
                new_prediction_list = predictions

            for gt in ground_truth:
                found = False
                for i, pred in enumerate(new_prediction_list):
                    if pred != "":
                        if pred.get('matched_gt', False):
                            continue

                        if self.prediction_source == "ChatGPT":
                            full_match_condition = (pred['entity_type'] == gt_type_dict.get(gt['entity_type'])) and \
                                (abs(pred['start-end'][0][0] - gt['start-end'][0]) + abs(pred['start-end'][0][1] - gt['start-end'][1]) <= 3)

                        elif self.prediction_source == "jsl_ner":
                            full_match_condition = (pred['entity_type'] == gt_type_dict.get(gt['entity_type'])) and \
                                ((abs(pred['start-end'][0] - gt['start-end'][0]) + abs(pred['start-end'][1] - gt['start-end'][1])) <= 3)

                        if full_match_condition:
                            # print("full_match_condition:", full_match_condition, pred['chunk'], gt['chunk'])
                            full_match += 1
                            full_match_chunks.append((i, gt))
                            found = True
                            pred['matched_gt'] = True
                            break

                        elif not full_match_condition and (pred['entity_type'] == gt_type_dict.get(gt['entity_type']) and (pred['chunk'] in gt['chunk'] or gt['chunk'] in pred['chunk'])):
                            try:
                                start, end = pred['start-end'][0]
                            except:
                                start, end = pred['start-end']

                            gt_start, gt_end = gt['start-end']
                            if (gt_start >= start and gt_start <= end) or (gt_end >= start and gt_end <= end):
                                partial_match += 1
                                partial_match_chunks.append((i, gt))
                                # print("partial_match:", pred['chunk'], gt['chunk'])
                                found = True
                                pred['matched_gt'] = True
                                break

                if not found:
                    no_match += 1
                    no_match_chunks.append(gt)

            iter=0
            while len(no_match_chunks)>1 and iter<6:
                last_predictions = new_prediction_list
                new_ground_truth = no_match_chunks
                for gt in new_ground_truth:
                    found = False
                    for i, pred in enumerate(last_predictions):
                        if pred['entity_type'] == gt_type_dict.get(gt['entity_type']) and (pred['chunk'] in gt['chunk'] or gt['chunk'] in pred['chunk']):
                            try:
                                start, end = pred['start-end']
                            except:
                                start, end = pred['start-end'][0]

                            gt_start, gt_end = gt['start-end']
                            if (gt_start >= start and gt_start <= end) or (gt_end >= start and gt_end <= end):
                                partial_match += 1
                                partial_match_chunks.append((i, gt))
                                try:
                                    no_match_chunks.remove(gt)
                                except:
                                    pass
                                found = True
                                pred['matched_gt'] = True
                                break
                iter+=1

            return {
                "full_match_count": full_match,
                "partial_match_count": partial_match,
                "no_match_count": len(no_match_chunks),
                "full_match_chunks": full_match_chunks,
                "partial_match_chunks": partial_match_chunks,
                "no_match_chunks":no_match_chunks,
                "gt_count": len(ground_truth),
                "fp_count": max(len(predictions) - (full_match + partial_match), 0),
                "pred_count": len(new_prediction_list)
            }
        except Exception as e:
            logger.error("An error occurred while calculating the match counts: ", str(e))
            return None


    def get_match_counts(self, selected_entity_prediction, selected_entity_gt, eval_name, gt_type_dict):
        try:
            full_match = 0
            partial_match = 0
            no_match = 0
            gt_count=0
            pred_count=0
            fp_count = 0
            df = self.load_data()
            if df is None:
                return None
            df.loc[:, 'result_summary'] = [[] for _ in range(len(df))]
            for i, row in df.iterrows():
                if not isinstance(df.loc[i, 'prediction_list'], float) and not isinstance(df.loc[i, 'prediction_list'], str):
                    predictions_filtered = [x for x in df.loc[i, 'prediction_list'] if x['entity_type'] in selected_entity_prediction]
                    ground_truth_filtered = [x for x in df.loc[i, "ground_truth_list"] if x["entity_type"] in  selected_entity_gt]
                res = self.match_counts(predictions_filtered, ground_truth_filtered, gt_type_dict)
                if res is None:
                    return None

                df.at[i, "result_summary"] = res

                full_match += res['full_match_count']
                partial_match += res['partial_match_count']
                no_match += res['no_match_count']
                gt_count += res['gt_count']
                pred_count += res['pred_count']
                fp_count += res['fp_count']

            self.result_df = df.copy()
            dir = "./eval_results/"
            if not os.path.exists(dir):
                os.makedirs(dir)
            self.result_df.to_excel(f"{dir}{eval_name}.xlsx")
            print(f"Evaluation results saved as {dir}{eval_name}.xlsx")

            return {
                "version": (eval_name),
                "selected_entity_prediction":selected_entity_prediction,
                "selected_entity_gt":selected_entity_gt,
                "full_match": full_match,
                "accuracy_full_match": round(full_match/gt_count, 2),
                "partial_match": partial_match,
                "accuracy_partial_match": round((full_match+partial_match)/gt_count, 2),
                "no_match": no_match,
                "gt_count": gt_count,
                "fp_count": fp_count,
                # "pred_count":pred_count
            }

        except Exception as e:
            logger.info("An error occurred while getting the match counts: ", str(e))
            return None




