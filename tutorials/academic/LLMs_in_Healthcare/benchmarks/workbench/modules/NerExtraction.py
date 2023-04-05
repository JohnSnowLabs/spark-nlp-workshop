# Using short explanation for Test, Procedure, Test Result entity types
import openai
import os
import json

# get creds from config for server connection
from pyaml_env import parse_config
file_name = 'creds.yml'
config_path = os.path.join('..', 'config', file_name )
config = parse_config(config_path)

class ChatGPTNER:

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
        model = "gpt-3.5-turbo" #"gpt-4"#

        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful nlp annotation expert on healthcare domain."},
                {"role": "user", "content": f"{prompt}"}
            ]
        )

        result = response

        return result


