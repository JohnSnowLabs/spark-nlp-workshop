# -*- coding: utf-8 -*-
import os
from enum import Enum

class MODEL_OPS(Enum):
    INIT = 10
    TRAIN = 11

class MODEL_TENSORS(Enum):
    LOSS = 100
    ACC = 101
    INPUTS = 102
    TARGETS = 103
    OUTPUTS = 104
    LEARNING_RATE = 105
    
class RUN_TYPES(Enum):
    TRAIN = 0
    EVALUATE = 0
    PREDICT = 0
    
class Settings:
    DATASETS_DIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../test_jsl/resources/")
    MODELS_DIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + "/../../../src/main/resources/genericclassifier/")
    LOGS_DIR = "/tmp/genericclassifier"

    
    DEFAULT_MODEL_NODE_NAMES = {
            MODEL_OPS.INIT: "init",
            MODEL_OPS.TRAIN: "optimizer",
            MODEL_TENSORS.LOSS: "loss:0",
            MODEL_TENSORS.ACC: "accuracy:0",
            MODEL_TENSORS.INPUTS: "inputs:0",
            MODEL_TENSORS.OUTPUTS: "outputs:0",
            MODEL_TENSORS.TARGETS: "targets:0",
            MODEL_TENSORS.LEARNING_RATE: "learning_rate:0",
        }    
    