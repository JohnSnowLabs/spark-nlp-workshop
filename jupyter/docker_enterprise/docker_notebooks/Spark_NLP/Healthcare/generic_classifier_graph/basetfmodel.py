# -*- coding: utf-8 -*-
import tensorflow.compat.v1 as tf

import numpy as np

from progresstracker import ProgressTracker
from settings import Settings, MODEL_OPS, MODEL_TENSORS, RUN_TYPES

class BaseTFModel:
    _model_id = None
    _graph = None

    def __str__(self):
        return str(self._model_id)

    def __get_node_name(self, node):
        if node in Settings.DEFAULT_MODEL_NODE_NAMES:
            return "{}".format(Settings.DEFAULT_MODEL_NODE_NAMES[node])
        else:
            return "{}".format(node)

    def _get_op(self, op):
        return self._graph.get_operation_by_name(
            self.__get_node_name(op))

    def _get_tensor(self, tensor):
        return self._graph.get_tensor_by_name(
            self.__get_node_name(tensor))

    def _get_init_op(self):
        return self._get_op(MODEL_OPS.INIT)

    def _get_optimizer_op(self):
        return self._get_op(MODEL_OPS.TRAIN)

    def _get_inputs_tensor(self):
        return self._get_tensor(MODEL_TENSORS.INPUTS)

    def _get_outputs_tensor(self):
        return self._get_tensor(MODEL_TENSORS.OUTPUTS)

    def _get_targets_tensor(self):
        return self._get_tensor(MODEL_TENSORS.TARGETS)

    def _get_loss_tensor(self):
        return self._get_tensor(MODEL_TENSORS.LOSS)

    def _get_accuracy_tensor(self):
        return self._get_tensor(MODEL_TENSORS.ACC)

    def _get_learning_rate_tensor(self):
        return self._get_tensor(MODEL_TENSORS.LEARNING_RATE)

    def _get_feed(self, run_type):
        return {}

    def get_graph(self):
        if self._graph is None:
            raise Exception('the model is not built')
        return self._graph

    def _set_graph(self, graph):
        self._graph = graph

    def is_built(self):
        return self._graph

    def export_graph(self, model_dir, log_dir, suffix=""):
        #Save TF graph

        tf.io.write_graph(
            self._graph,
            "{}/{}".format(log_dir, self._model_id),
            "{}/{}{}.pb".format(model_dir, self._model_id, suffix),
            False)

        print("Graph exported to {}".format("{}/{}{}.pb".format(model_dir, self._model_id, suffix)))

    def generate_batch(self, inputs, outputs, batch_size):

        #generate randomization
        permutation = np.random.permutation(inputs.shape[0])

        #randomize sets
        inputs = inputs[permutation, :]
        outputs = outputs[permutation, :]

        for offset in range(0, inputs.shape[0] // batch_size):
            yield (
                inputs[offset:offset + batch_size, :],
                outputs[offset:offset + batch_size, :]
            )

    def __get_batch_feed(self, batch, run_type, learning_rate = None):
        feed = self._get_feed(run_type)
        feed[self._get_inputs_tensor()] = batch[0]
        feed[self._get_targets_tensor()] = batch[1]
        if learning_rate:
            feed[self._get_learning_rate_tensor()] = learning_rate

        return feed

    def fit_dataset(
            self,
            training_set,
            validation_set = None,
            training_batch_size = None,
            validation_batch_size = None,
            epochs_n = 1,
            learning_rate = None,
            verbose = True,
            progresstracker = None
    ):

        assert(self.is_built())

        if training_batch_size is None:
            training_batch_size = training_set[0].shape[0]

        if validation_set and (validation_batch_size is None):
            validation_batch_size = validation_set[0].shape[0]


        if verbose and progresstracker is None:
            batches_n = training_set[0].shape[0] // training_batch_size
            progresstracker = ProgressTracker(batches_n)

        with tf.Session() as session:

            session.run(self._get_init_op())

            if progresstracker:
                progresstracker.on_training_start(self,  epochs_n)

            for e in range(1, epochs_n + 1):

                training_bacthes = self.generate_batch(
                    training_set[0],
                    training_set[1],
                    training_batch_size)

                for batch in training_bacthes:
                    #do training

                    session.run(
                        self._get_optimizer_op(),
                        feed_dict=self.__get_batch_feed(
                            batch,
                            RUN_TYPES.TRAIN,
                            learning_rate))

                    loss, acc = session.run(
                        [
                            self._get_loss_tensor(),
                            self._get_accuracy_tensor()
                        ],
                        feed_dict=self.__get_batch_feed(
                            batch,
                            RUN_TYPES.EVALUATE))

                    if progresstracker:
                        progresstracker.on_batch(loss, acc)

                if validation_set:
                    validation_bacthes = self.generate_batch(
                        validation_set[0],
                        validation_set[1],
                        validation_batch_size)

                    for batch in validation_bacthes:
                        val_loss, val_acc = session.run(
                            [
                                self._get_loss_tensor(),
                                self._get_accuracy_tensor()
                            ],
                            feed_dict=self.__get_batch_feed(
                                batch,
                                RUN_TYPES.EVALUATE))

                        if progresstracker:
                            progresstracker.on_batch(val_loss, val_acc, True)

                if progresstracker:
                    progresstracker.on_epoch()

            if progresstracker:
                progresstracker.on_training_end()

    def load_graph(self, models_dir):
        model_path = "{}/{}.pb".format(models_dir, self._model_id)

        tf.reset_default_graph()

        with tf.Session() as session:


            with tf.gfile.GFile(model_path,'rb') as F:
                graph_def = tf.GraphDef()

            graph_def.ParseFromString(F.read())

            session.graph.as_default()

            tf.import_graph_def(graph_def, name="")

            self._set_graph(session.graph)


    def build(self, params):
        raise("Built method not implemented for bas class!")

    def run_tests(self, verbose=True):
        raise("Tests not implemented for base class!")

    def __init__(self, model_id):
        self._model_id = model_id
