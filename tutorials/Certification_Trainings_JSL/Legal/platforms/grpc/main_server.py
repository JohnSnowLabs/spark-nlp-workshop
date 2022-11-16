import contextlib
import multiprocessing
import sys
import time
from concurrent import futures
import socket

import grpc

import config
from config import RANGE_START
from definition.definition_pb2_grpc import add_SparkNLPServicer_to_server, SparkNLPServicer
import logging

from sparknlp_manager.sparknlp_manager import SparkNLPManager


def _run_server(bind_address):
    """Start a server in a subprocess."""
    logging.info('Starting new server.')
    options = (('grpc.so_reuseaddress', 1),)

    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=10,),
                         options=options)
    add_SparkNLPServicer_to_server(
        SparkNLPServicer(), server)
    server.add_insecure_port(bind_address)
    server.start()
    #_wait_forever(server)
    server.wait_for_termination()


@contextlib.contextmanager
def _reserve_port(port):
    """Find and reserve a port for all subprocesses to use."""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) == 0:
    #    raise RuntimeError("Failed to set SO_REUSEPORT.")
    #sock.bind(('', 0))
    sock.bind(('localhost', port))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()


def main():
    workers = []
    for i in range(0, config.NUM_WORKERS):
        with _reserve_port(i+RANGE_START) as port:
            bind_address = 'localhost:{}'.format(port)
            print(f"Worker {i} bound to {bind_address}")
            sys.stdout.flush()
            # NOTE: It is imperative that the worker subprocesses be forked before
            # any gRPC servers start up. See
            # https://github.com/grpc/grpc/issues/16001 for more details.
            worker = multiprocessing.Process(target=_run_server,
                                             args=(bind_address,))

            worker.start()
            workers.append(worker)
    for worker in workers:
        time.sleep(5)
        worker.join()


if __name__ == '__main__':
    main()
