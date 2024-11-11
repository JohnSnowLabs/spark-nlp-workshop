import json
import logging
import threading

from flask import Flask, render_template, request
from johnsnowlabs import viz

import config
import uuid
import re
from flask_bootstrap import Bootstrap

from chatGPTManager import ChatGPTManager


class FlaskManager:
    def __init__(self):
        self.app = Flask(__name__)
        Bootstrap(self.app)
        self.spark_manager = None
        self.texts = {}
        self.ner_tags = {}
        self.ner_confidences = {}
        self.tokens = {}

        @self.app.route('/')
        def render_main_page():
            if self.spark_manager is None:
                return render_template('loading.html')
            new_user_id = uuid.uuid4().hex
            return render_template('index.html',
                                   ner_tags=self.get_ner_tags_by_user_id(new_user_id),
                                   ner_tags_str=json.dumps(self.get_ner_tags_by_user_id(new_user_id), indent=4),
                                   text=self.get_text_by_user_id(new_user_id),
                                   user_id=new_user_id, confidence=self.get_confidence_by_user_id(new_user_id),
                                   token=self.get_token_by_user_id(new_user_id))

        def change_tag_number():
            if self.spark_manager is None:
                return render_template('loading.html')

            user_id = request.form['user_id']

            v = int(request.form['n_tags'])
            new_ner_tags = {}
            for i, elem in enumerate(self.get_ner_tags_by_user_id(user_id)):
                if i < v:
                    new_ner_tags[elem] = self.get_ner_tags_by_user_id(user_id)[elem]
            for i in range(len(new_ner_tags), v):
                new_ner_tags[f'TAG {i}'] = ['']
            self.set_ner_tags_by_user_id(new_ner_tags, user_id)

            new_confidences = self.get_confidence_by_user_id(user_id)
            for k in self.get_ner_tags_by_user_id(user_id):
                if k not in self.get_confidence_by_user_id(user_id):
                    new_confidences[k] = 0.5

            self.set_confidence_by_user_id(new_confidences, user_id)

        def configure_tag():
            if self.spark_manager is None:
                return render_template('loading.html')

            user_id = request.form['user_id']

            for k in request.form.keys():
                new_tags = self.get_ner_tags_by_user_id(user_id).copy()
                new_confidences = self.get_confidence_by_user_id(user_id).copy()
                to_add = []
                to_delete = []
                if k.startswith('confidence_') or k.startswith('tagname_') or k.startswith('nquestions_'):
                    k_splits = k.split('_')
                    elem_id = int(k_splits[1])
                    if len(new_tags) < elem_id:
                        continue
                    elem = list(new_tags.keys())[elem_id - 1]
                    if k.startswith('tagname_'):
                        v = request.form[k]
                        for i, tk in enumerate(new_tags.keys()):
                            # Change name
                            if i == elem_id-1:
                                if v != tk:
                                    to_add.append({v: new_tags[tk]})
                                    to_delete.append(tk)
                    elif k.startswith('confidence_'):
                        v = float(request.form[k])
                        new_confidences[elem] = v
                    elif k.startswith('nquestions_'):
                        # Number of questions
                        v = int(request.form[k])
                        # For each present question
                        questions = []
                        for i, q in enumerate(new_tags[elem]):
                            if i < v:
                                if q not in questions:
                                    questions.append(q)
                        for i in range(len(new_tags[elem]), v):
                            questions.append(f'')
                        new_tags[elem] = questions
                for td in to_delete:
                    del new_tags[td]
                for ta in to_add:
                    for k, v in ta.items():
                        new_tags[k] = v
                self.set_ner_tags_by_user_id(new_tags, user_id)
                self.set_confidence_by_user_id(new_confidences, user_id)

        def set_questions():
            if self.spark_manager is None:
                return render_template('loading.html')

            user_id = request.form['user_id']

            for k in request.form.keys():
                v = request.form[k]
                if k.startswith('tagquestion_'):
                    k_splits = k.split('_')
                    elem_id = int(k_splits[1])
                    if len(self.get_ner_tags_by_user_id(user_id)) < elem_id:
                        continue
                    elem = list(self.get_ner_tags_by_user_id(user_id).keys())[elem_id - 1]
                    j = int(k_splits[3])
                    if len(self.get_ner_tags_by_user_id(user_id)[elem]) <= j:
                        continue
                    self.get_ner_tags_by_user_id(user_id)[elem][j] = v

        def infer():
            if self.spark_manager is None:
                return render_template('loading.html')

            user_id = request.form['user_id']
            v = self.get_text_by_user_id(user_id)
            annotations = self.spark_manager.infer('ner', v)
            annotation = annotations[0]

            annotation['ner_chunk'] = list(filter(lambda x: float(x.metadata['confidence']) >=
                                             self.get_confidence_by_user_id(user_id)[x.metadata['entity']],
                                             annotation['ner_chunk']))

            ner_viz = viz.NerVisualizer()
            html_widget = ner_viz.display(result=annotation, label_col='ner_chunk',
                                          document_col='document', raw_text=v, return_html=True)
            html_widget = html_widget.replace("background-color: white","")
            return html_widget

        def set_prompts():
            user_id = request.form['user_id']
            self.spark_manager.set_prompts('ner', self.get_ner_tags_by_user_id(user_id))

        def set_token():
            user_id = request.form['user_id']
            token = request.form['token']
            self.set_token_by_user_id(token, user_id)

        def set_text():
            user_id = request.form['user_id']
            text = request.form['text']
            self.set_text_by_user_id(text, user_id)

        @self.app.route('/save_prompts', methods=['POST'])
        def save_prompts():
            if self.spark_manager is None:
                return render_template('loading.html')

            user_id = request.form['user_id']

            v = request.form['filename']
            msg = "Only characters and numbers are valid"
            if re.match(r'[a-zA-Z0-9]', v):
                n = f"{v}_domain_ner.json"
                with open(f'./prompts/{n}', 'w') as f:
                    json.dump(self.get_ner_tags_by_user_id(user_id), f)
                msg = f"Saved as {n}"

            return render_template('index.html',
                                   ner_tags=self.get_ner_tags_by_user_id(user_id),
                                   ner_tags_str=json.dumps(self.get_ner_tags_by_user_id(user_id), indent=4),
                                   text=self.get_text_by_user_id(user_id),
                                   user_id=user_id, msg=msg,
                                   confidence=self.get_confidence_by_user_id(user_id),
                                   token=self.get_token_by_user_id(user_id))

        @self.app.route('/submit', methods=['POST'])
        def submit():
            if self.spark_manager is None:
                return render_template('loading.html')

            user_id = request.form['user_id']

            set_token()
            change_tag_number()
            configure_tag()
            set_questions()
            set_prompts()
            set_text()
            if 'ask_gpt' in request.form:
                html_widget = ChatGPTManager.ask(request.form['text'], request.form['token'])
                html_widget = html_widget.replace("\n", "<br/>")
            else:
                html_widget = infer()

            return render_template('index.html',
                                   ner_tags=self.get_ner_tags_by_user_id(user_id),
                                   ner_tags_str=json.dumps(self.get_ner_tags_by_user_id(user_id), indent=4),
                                   text=self.get_text_by_user_id(user_id), user_id=user_id,
                                   confidence=self.get_confidence_by_user_id(user_id),
                                   html_widget=html_widget,
                                   token=self.get_token_by_user_id(user_id))

        @self.app.route('/healthcheck')
        def check_jvm_spark():
            if self.spark_manager is None:
                return json.dumps({'success': False}), 503, {'ContentType': 'application/json'}
            try:
                self.spark_manager.spark.createDataFrame([[""]])
                return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
            except Exception as e:
                logging.error(f"[Healthcheck] Spark NLP or java are not running. Cause: {e}")
                return json.dumps({'success': False}), 503, {'ContentType': 'application/json'}

        # self.app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=True, use_reloader=True)
        threading.Thread(target=lambda: self.app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=True,
                                                     use_reloader=False)).start()

    def get_ner_tags_by_user_id(self, user_id):
        if user_id not in self.ner_tags:
            self.ner_tags[user_id] = {'TAG 0': ['']}

        return self.ner_tags[user_id]

    def set_ner_tags_by_user_id(self, tags, user_id):
        self.ner_tags[user_id] = tags

    def get_text_by_user_id(self, user_id):
        if user_id not in self.texts:
            self.texts[user_id] = ""
        return self.texts[user_id]

    def set_text_by_user_id(self, text, user_id):
        self.texts[user_id] = text

    def get_confidence_by_user_id(self, user_id):
        if user_id not in self.ner_confidences:
            self.ner_confidences[user_id] = {'TAG 0': 0.5}
        return self.ner_confidences[user_id]

    def set_confidence_by_user_id(self, confidence, user_id):
        self.ner_confidences[user_id] = confidence

    def get_token_by_user_id(self, user_id):
        if user_id not in self.tokens:
            self.tokens[user_id] = ""
        return self.tokens[user_id]

    def set_token_by_user_id(self, token, user_id):
        self.tokens[user_id] = token
