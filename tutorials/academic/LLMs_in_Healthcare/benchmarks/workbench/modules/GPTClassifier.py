# Using short explanation for Test, Procedure, Test Result entity types
import openai
import os
import json
from collections import defaultdict
from typing import Tuple, Dict


# get creds from config for server connection
# get creds from config for server connection
from pyaml_env import parse_config
file_name = 'creds.yml'
config_path = os.path.join('..', 'config', file_name )
config = parse_config(config_path)

class Classifier:

    def __init__(self, prompt_path):
        self.openai_api_key = config.get("openai_key")
        self.prompt_path = prompt_path
        self.get_annotation_guidelines()

    def get_annotation_guidelines(self):
        with open(self.prompt_path,"r") as f:
            self.annotation_guidelines = f.read()

    def do_query(self, sentence):

        prompt = f"""
                    {self.annotation_guidelines}
                    {sentence}
                """

        openai.api_key = self.openai_api_key
        model = "gpt-3.5-turbo"

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful nlp annotation expert on healthcare domain."},
                {"role": "user", "content": f"{prompt}"}
            ]
        )
        result = response
        return result


    def gender_metrics(self, data: Tuple[str, str], file_name: str) -> Dict[str, float]:
        counts = defaultdict(int)
        correct = defaultdict(int)
        not_found = defaultdict(int)
        false_positives = defaultdict(int)

        for gt, pred in data:
            counts[gt] += 1
            if gt == pred:
                correct[gt] += 1
            elif pred == "Not Found":
                not_found[gt] += 1
            else:
                false_positives[gt] += 1

        accuracy = {gt: correct[gt] / counts[gt] for gt in counts}

        metrics = {
            "Version": file_name,
            "Male Accuracy": accuracy["Male"],
            "Male Not Found": not_found["Male"],
            "Male False Positive": false_positives["Male"],
            "Female Accuracy": accuracy["Female"],
            "Female Not Found": not_found["Female"],
            "Female False Positive": false_positives["Female"],
            "Data Distribution": f"{counts['Female']}F-{counts['Male']}M"
        }

        return metrics

    def gender_fix_output_typo(self, row):
        gender_labels = ["Male", "Female", "Not Found"]
        for label in gender_labels:
            if label in row:
                return label


    def ade_metrics(self, data: Tuple[str, str], file_name:str) -> Dict[str, float]:
        counts = defaultdict(int)
        correct = defaultdict(int)
        false_positives = defaultdict(int)
        not_found = defaultdict(int)

        for gt, pred in data:
            counts[gt] += 1
            if gt == pred:
                correct[gt] += 1
            elif pred == "Not Found":
                not_found[gt] += 1
            else:
                false_positives[gt] += 1

        accuracy = {gt: correct[gt] / counts[gt] for gt in counts}

        results = {
            "Version": file_name,
            "Positive Accuracy": accuracy["POSITIVE"],
            "Negative Accuracy": accuracy["NEGATIVE"],
            "Positive Not Found": not_found["POSITIVE"],
            "Negative Not Found": not_found["NEGATIVE"],
            "Positive False Positives": false_positives["POSITIVE"],
            "Negative False Positives": false_positives["NEGATIVE"],
        }

        return results

    def ade_fix_output_typo(self, row):
        labels = ["POSITIVE", "NEGATIVE", "Not SURE"]
        for label in labels:
            if label in row:
                return label








