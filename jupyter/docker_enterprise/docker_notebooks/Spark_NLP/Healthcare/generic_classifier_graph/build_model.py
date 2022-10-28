# -*- coding: utf-8 -*-

from generic_classifier_model import GenericClassifierModel
from settings import Settings

build_params = {
    "hidden_layers": [400, 200, 100, 50],
    "hidden_act": "relu",
    "input_dim": 20,
    "output_dim": 10,
}

model = GenericClassifierModel()

model.build(build_params)

model.export_graph(
    model_dir=Settings.MODELS_DIR,
    log_dir=Settings.LOGS_DIR)
