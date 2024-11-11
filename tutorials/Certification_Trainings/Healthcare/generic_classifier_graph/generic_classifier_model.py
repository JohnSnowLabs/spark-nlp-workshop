# -*- coding: utf-8 -*-

import tensorflow.compat.v1 as tf
import keras
import numpy as np

from basetfmodel import BaseTFModel
from settings import Settings, RUN_TYPES, MODEL_TENSORS


class GenericClassifierModel(BaseTFModel):


    def build(self, params):

        self.__inputDim =  params["input_dim"]
        self.__outputDim =  params["output_dim"]

        if "hidden_act" not in params:
            params["hidden_act"] = "sigmoid"
        else:
            if params["hidden_act"] not in ["sigmoid", "tanh", "relu", "linear"]:
                error = "activation function '{}' is not supported".format(params["hidden_act"])
                raise Exception(error)

        if "hidden_act_l2" not in params:
            params["hidden_act_l2"] = 0

        if "hidden_weights_l2" not in params:
            params["hidden_weights_l2"] = 0

        tf.reset_default_graph()

        with tf.Session() as session:
            #Input
            inputs = tf.placeholder(
                tf.float32,
                shape=[None, params["input_dim"]],
                name='inputs')

            #Targets
            targets = tf.placeholder(
                tf.float32,
                shape=[None, params["output_dim"]], name='targets')

            #Learning rate
            learning_rate = tf.placeholder_with_default(
                tf.constant(0.001, dtype=tf.float32),
                shape=[], name='learning_rate')

            #Class weight
            class_weights = tf.placeholder_with_default(
                tf.ones(shape=params["output_dim"]),
                shape=[params["output_dim"]],
                name='class_weights')

            #Class weight
            dropout = tf.placeholder_with_default(
                tf.constant(0.0, dtype=tf.float32),
                shape=[],
                name='dropout')

            last_input = inputs
            i = 0
            for hidden_layer in params["hidden_layers"]:
                hidden = keras.layers.Dense(
                    units=hidden_layer,
                    activation=params["hidden_act"],
                    activity_regularizer=keras.regularizers.l2(params["hidden_act_l2"]),
                    kernel_regularizer=keras.regularizers.l2(params["hidden_weights_l2"]),
                    name="hidden{}".format(i))(last_input)
                last_input = hidden
                i += 1



            dropout_layer = tf.nn.dropout(
                last_input * 1.,
                rate=tf.minimum(1.0, tf.minimum(1.0, dropout)),
                name="dropout")


            output_layer = keras.layers.Dense(units=params["output_dim"])(dropout_layer)

            if "batch_norm" in params:
                normalization_layer = keras.layers.normalization.BatchNormalization()(output_layer)
            else:
                normalization_layer = output_layer

            outputs = tf.math.softmax(
                output_layer,
                name="outputs")

            #loss weights
            weights = tf.gather(class_weights,  tf.argmax(targets, 1))

            #Loss function
            loss = tf.reduce_mean(
                tf.losses.softmax_cross_entropy(
                    onehot_labels=targets,
                    logits=output_layer,
                    weights=weights
                ),
                name='loss')

            #Optimizer
            optimizer = tf.train.AdamOptimizer(
                learning_rate=learning_rate,
                name='optimizer').minimize(loss)

            #Accuracy per trial
            correct_prediction = tf.equal(
                tf.argmax(output_layer, 1),
                tf.argmax(targets, 1),
                name='correct_prediction')

            #Overall accuracy/by batch
            accuracy = tf.reduce_mean(
                tf.cast(correct_prediction, tf.float32),
                name='accuracy')

            #Model predictions
            cls_prediction = tf.argmax(
                output_layer,
                axis=1,
                name='predictions')

            #TF variables initialization
            init = tf.global_variables_initializer()

            self.__saver = tf.train.Saver()

            self._set_graph(session.graph)

    def _get_feed(self, run_type):
        if run_type == RUN_TYPES.TRAIN:
            return {}
        else:
            return {}
        
    def _process_data(self, filename):
        data = []
        labels = []
        input_shape = self._get_tensor(MODEL_TENSORS.INPUTS).shape[1]
        output_shape = self._get_tensor(MODEL_TENSORS.TARGETS).shape[1]

        with open(filename, "r") as F:
            for line in F.readlines()[1:]:
                line = line.strip().split(",")
                inputs = np.zeros(shape=input_shape)
                data_row = np.array(list(map(float, line[0].split("\t"))))
                inputs[:len(data_row)] = data_row
                data.append(inputs)
                output = np.zeros(output_shape)
                output[int(line[1])] = 1
                labels.append(output)
        data = np.array(data)
        labels = np.array(labels)
           
        return data, labels
    
    def _train_test(self, verbose):

        self.load_graph(Settings.MODELS_DIR)

        train_set = self._process_data(Settings.DATASETS_DIR + "news_category_train.csv")
        test_set = self._process_data(Settings.DATASETS_DIR + "news_category_test.csv")
    
    
        
    
        self.fit_dataset(
            training_set=train_set, 
            validation_set=test_set, 
            training_batch_size=200,
            validation_batch_size=None,
            epochs_n=10,
            learning_rate=0.0001,
            verbose=verbose)
        
    def run_tests(self, verbose=True):
        self._train_test(verbose)

    def export_graph(self, model_dir, log_dir):

        if self.__inputDim and self.__outputDim:
            suffix = ".in{}D.out{}".format(self.__inputDim, self.__outputDim)
        else:
            suffix = ""

        super(GenericClassifierModel, self).export_graph(model_dir, log_dir, suffix)

    def __init__(self, name = None):
        if name is None:
            name = "genericclassifier"
        super(GenericClassifierModel, self).__init__(name)
        self._learning_rate = 0.1
        self.__inputDim = None
        self.__outputDim = None