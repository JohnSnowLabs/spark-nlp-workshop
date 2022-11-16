import logging
import multiprocessing

import grpc

import config
from config import RANGE_START
from definition.definition_pb2 import nlp_input, nlp_output
from definition.definition_pb2_grpc import SparkNLPStub
import time


def _spin_worker(bind_address, text):
    with grpc.insecure_channel(bind_address) as channel:
        stub = SparkNLPStub(channel)
        print(f"Worker at {bind_address} starts processing...")
        start_time = time.time()
        print(stub.clf.future(nlp_input(text=text)).result())
        end_time = time.time()
        print(f"Worker at {bind_address} finishes processing...")
        print(f"Worker at {bind_address} took {end_time - start_time} seconds...")
        print(f"Worker at {bind_address} sleeps 10 seconds...")
        time.sleep(10)
        #print("-------------- NER Pipeline --------------")
        #do_ner(stub)
        #print("-------------- RE Pipeline --------------")
        #do_re(stub)


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    workers = []
    for i in range(0, config.NUM_WORKERS):
        bind_address = f"localhost: {i + RANGE_START}"
        print(f"Sending worker {i} to {bind_address}")
        worker = multiprocessing.Process(target=_spin_worker,
                                         args=(bind_address, config.DOCUMENT))
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()


if __name__ == '__main__':
    logging.basicConfig()
    run()