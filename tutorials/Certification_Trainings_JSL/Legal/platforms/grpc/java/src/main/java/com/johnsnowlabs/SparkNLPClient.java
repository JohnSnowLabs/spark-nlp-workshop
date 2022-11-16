package com.johnsnowlabs;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.util.concurrent.ListenableFuture;
import com.google.protobuf.Message;
import com.johnsnowlabs.grpc.SparkNLPGrpc;
import com.johnsnowlabs.grpc.SparkNLPGrpc.SparkNLPBlockingStub;
import com.johnsnowlabs.grpc.SparkNLPGrpc.SparkNLPStub;
import com.johnsnowlabs.grpc.nlp_input;
import com.johnsnowlabs.grpc.nlp_output;
import io.grpc.Channel;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.Status;
import io.grpc.StatusRuntimeException;
import io.grpc.stub.StreamObserver;
import org.apache.commons.lang.RandomStringUtils;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Sample client code that makes gRPC calls to the server.
 */
public class SparkNLPClient {
    private static final Logger logger = Logger.getLogger(SparkNLPClient.class.getName());

    private final SparkNLPBlockingStub blockingStub;
    private final SparkNLPStub asyncStub;
    private final SparkNLPGrpc.SparkNLPFutureStub futureStub;

    private Random random = new Random();

    /**
     * Construct client for accessing RouteGuide server using the existing channel.
     */
    public SparkNLPClient(Channel channel) {
        blockingStub = SparkNLPGrpc.newBlockingStub(channel);
        futureStub = SparkNLPGrpc.newFutureStub(channel);
        asyncStub = SparkNLPGrpc.newStub(channel);
    }

    /**
     * Blocking unary call example.  Calls getFeature and prints the response.
     */
    public ListenableFuture<nlp_output> clf(String text) {
        info("*** Classify: {0}", text);

        nlp_input request = nlp_input.newBuilder().setText(text).build();

        ListenableFuture<nlp_output> listeneable_response;
        //nlp_output response;
        try {
            listeneable_response = futureStub.clf(request);
        } catch (StatusRuntimeException e) {
            warning("RPC failed: {0}", e.getStatus());
            return null;
        }
        return listeneable_response;
        //info("Response: \"{0}\"", listeneable_response);

    }

    /** Issues several requests and then exits. */
    public static void main(String[] args) throws InterruptedException {
        HashMap<String, ListenableFuture<nlp_output>> results = new HashMap<>();
        HashMap<String, ManagedChannel> channels = new HashMap<>();

        // Adding the futures
        logger.info("Adding the futures...");
        for(int i=0; i<Utils.NUM_WORKERS;i++) {
            String target = String.format("localhost:%s", Utils.RANGE_START + i);
            ManagedChannel channel = ManagedChannelBuilder.forTarget(target).usePlaintext().build();
            SparkNLPClient client = new SparkNLPClient(channel);
            //results.put(target, client.clf(RandomStringUtils.randomAlphanumeric(1000024)));
            results.put(target, client.clf(Utils.DOCUMENT));
            channels.put(target, channel);
        }

        logger.info("Resolving the futures...");
        for(String target: results.keySet()) {
            try {
                ListenableFuture<nlp_output> output = results.get(target);
                long start = System.currentTimeMillis();
                nlp_output o = output.get();
                //logger.info(o.getResult());
                long end = System.currentTimeMillis();
                float sec = (end - start) / 1000F;
                logger.info("\n- Target: " + target + "\n- Result: " + o.getResult() + "\n- Time: " + sec + " seconds");
            } catch (ExecutionException e) {
                throw new RuntimeException(e);
            } finally {
                channels.get(target).shutdownNow().awaitTermination(5, TimeUnit.SECONDS);
            }
        }
    }

    private void info(String msg, Object... params) {
        logger.log(Level.INFO, msg, params);
    }

    private void warning(String msg, Object... params) {
        logger.log(Level.WARNING, msg, params);
    }


}