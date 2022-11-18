package com.johnsnowlabs;
/*
 * Copyright 2015 The gRPC Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import com.google.common.annotations.VisibleForTesting;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.protobuf.Message;
import com.johnsnowlabs.grpc_async.nlp_input;
import com.johnsnowlabs.grpc_async.nlp_output;
import com.johnsnowlabs.grpc_async.sparknlp_asyncGrpc;
import io.grpc.Channel;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Status;
import io.grpc.StatusRuntimeException;
import io.grpc.stub.StreamObserver;
import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Random;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;
import com.johnsnowlabs.grpc_async.sparknlp_asyncGrpc.*;

public class SparkNLPClient {
    private static final Logger logger = Logger.getLogger(SparkNLPClient.class.getName());

    private final sparknlp_asyncBlockingStub blockingStub;
    private final sparknlp_asyncStub asyncStub;

    /** Construct client for accessing RouteGuide server using the existing channel. */
    public SparkNLPClient(Channel channel) {
        blockingStub = sparknlp_asyncGrpc.newBlockingStub(channel);
        asyncStub = sparknlp_asyncGrpc.newStub(channel);
    }


    public CountDownLatch clf(String Text, int numModels) throws InterruptedException {
        info("-- Models: " + numModels);
        final CountDownLatch finishLatch = new CountDownLatch(1);
        StreamObserver<nlp_output> responseObserver = new StreamObserver<nlp_output>() {
            @Override
            public void onNext(nlp_output summary) {
                info("clf1_m got response {0}", summary.getResult());
            }

            @Override
            public void onError(Throwable t) {
                warning("clf1_m failed: {0}", Status.fromThrowable(t));
                finishLatch.countDown();
            }

            @Override
            public void onCompleted() {
                info("clf1_m finished");
                finishLatch.countDown();
            }
        };
        nlp_input request = nlp_input.newBuilder().setText(Text).build();
        switch(numModels) {
            case 1:
                asyncStub.clf1m(request, responseObserver);
                break;
            case 10:
                asyncStub.clf10m(request, responseObserver);
                break;
            case 100:
                asyncStub.clf100m(request, responseObserver);
                break;
            case 200:
                asyncStub.clf200m(request, responseObserver);
                break;
            case 300:
                asyncStub.clf300m(request, responseObserver);
                break;
        }
        return finishLatch;
    }

    public static void send(String target, boolean initialization) throws InterruptedException {
        long timeout = Utils.INFERENCE_TIMEOUT;
        if (initialization) {
            logger.info("\n--First time initialization. Please, wait...");
            timeout = Utils.INITIALIZATION_TIMEOUT;
        }
        ManagedChannel channel = ManagedChannelBuilder.forTarget(target).usePlaintext().build();
        try {
            SparkNLPClient client = new SparkNLPClient(channel);
            long start = System.currentTimeMillis();
            CountDownLatch finishLatch = client.clf(Utils.newParagraph(), Utils.NUM_MODELS);
            if (!finishLatch.await(timeout, TimeUnit.MINUTES)) {
                client.warning("clm_1m can not finish within 1 minutes");
            }
            long end = System.currentTimeMillis();
            float sec = (end - start) / 1000F;
            channel.shutdownNow().awaitTermination(timeout, TimeUnit.SECONDS);
            if(initialization) {
                client.info(String.format("\n--Initialized! Elapsed time: %s", sec));
            }
        }
        finally {
            channel.shutdownNow().awaitTermination(5, TimeUnit.SECONDS);
        }
    }

    public static void main(String[] args) throws InterruptedException {
        // I do first one call for the initial latency
        String target = String.format("localhost:%s", Utils.RANGE_START);
        send(target, true);

        long start = System.currentTimeMillis();

        int calls = Utils.CALLS / Utils.NUM_WORKERS;

        for (int j = 0; j < calls; j++) {
            for (int i = 0; i < Utils.NUM_WORKERS; i++) {
                send(String.format("localhost:%s", Utils.RANGE_START + i), false);
            }
        }
        long end = System.currentTimeMillis();
        float sec = (end - start) / 1000F;

        logger.info("-- Total of calls: " + Utils.CALLS);
        logger.info("-- Total of calls per worker: " + calls);
        logger.info("-- Total of workers: " + Utils.NUM_WORKERS);
        logger.info("-- Elapsed time: " + sec);
        logger.info("-- Average time per call: " + sec / Utils.CALLS);
    }

    private void info(String msg, Object... params) {
        logger.log(Level.INFO, msg, params);
    }

    private void warning(String msg, Object... params) {
        logger.log(Level.WARNING, msg, params);
    }
}
