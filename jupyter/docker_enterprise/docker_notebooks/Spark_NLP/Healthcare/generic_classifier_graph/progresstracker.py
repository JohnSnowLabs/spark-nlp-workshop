# -*- coding: utf-8 -*-
import sys

class ProgressTracker:
    def on_training_start(self, model, epochs_n):
        print("Training {}, {} epochs\n".format(model, epochs_n))

    def on_training_end(self):
        print("\nTraining completed.")

    def on_batch(self, loss, accuracy, is_validation = False):
        if not is_validation:
            self._loss_accum += loss
            self._acc_accum += accuracy
            self._batch_i += 1
            self.print_progress()
        else:
            self._val_loss_accum += loss
            self._val_acc_accum += accuracy
            self._val_batch_i += 1

    def on_epoch(self):
        self._epoch_i += 1
        self.print_progress(True)

        self._loss_accum = 0
        self._acc_accum = 0

        self._batch_i = 0

    def get_report_interval(self):
        return self._report_interval

    def print_progress(self, end_of_epoch=False):

        if (self._batches_n):
            epoch_progress = "{}%".format(
                int(100 * (self._batch_i) / float(self._batches_n)))
        else:
            epoch_progress = self._batch_i

        print("\r{:>20}   Loss:{:.3f}   ACC:{:.3f}" \
            .format(
            "\rEpoch #{:<5}{:>6}".format(
                self._epoch_i if end_of_epoch else self._epoch_i + 1,
                epoch_progress),
            self._loss_accum / float(self._batch_i),
            self._acc_accum / float(self._batch_i)),
            end="")
        sys.stdout.flush()

        if end_of_epoch:
            if self._val_loss_accum > 0:
                print("   Val Loss:{:.3f}   Val ACC:{:.3f}" \
                    .format(
                    self._val_loss_accum / float(self._val_batch_i),
                    self._val_acc_accum / float(self._val_batch_i)),
                    end="\n")
                sys.stdout.flush()

    def __init__(self, batches_n = None):
        self._batch_i = 0
        self._val_batch_i = 0
        self._epoch_i = 0
        self._loss_accum = 0
        self._acc_accum = 0
        self._val_loss_accum = 0
        self._val_acc_accum = 0
        self._batches_n = batches_n