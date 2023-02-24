package com.johnsnowlabs;

import com.johnsnowlabs.grpc_async.nlp_input;
import com.johnsnowlabs.grpc_async.nlp_output;
import com.johnsnowlabs.grpc_async.sparknlp_asyncGrpc;
import com.johnsnowlabs.sparknlp_manager.SparkNLPManager;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;
import java.io.IOException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.StreamObserver;

import java.io.IOException;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

public class SparkNLPServer {
    private static final Logger logger = Logger.getLogger(SparkNLPServer.class.getName());

    private final int port;
    private final Server server;

    public SparkNLPServer(int port) {
        this(ServerBuilder.forPort(port), port);
    }
    /** Create a RouteGuide server using serverBuilder as a base and features as data. */
    public SparkNLPServer(ServerBuilder<?> serverBuilder, int port) {
        this.port = port;
        this.server = serverBuilder.addService(new SparkNLPService())
                .build();
    }


    /** Start serving requests. */
    public void start() throws IOException {
        server.start();
        logger.info("Server started, listening on " + port);
        Runtime.getRuntime().addShutdownHook(new Thread() {
            @Override
            public void run() {
                // Use stderr here since the logger may have been reset by its JVM shutdown hook.
                System.err.println("*** shutting down gRPC server since JVM is shutting down");
                try {
                    SparkNLPServer.this.stop();
                } catch (InterruptedException e) {
                    e.printStackTrace(System.err);
                }
                System.err.println("*** server shut down");
            }
        });
    }

    /** Stop serving requests and shutdown resources. */
    public void stop() throws InterruptedException {
        if (server != null) {
            server.shutdown().awaitTermination(30, TimeUnit.SECONDS);
        }
    }

    /**
     * Await termination on the main thread since the grpc library uses daemon threads.
     */
    private void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }

    /**
     * Main method.  This comment makes the linter happy.
     */
    public static void main(String[] args) throws Exception {
        ArrayList<SparkNLPServer> servers = new ArrayList<>();
        for(int i=0; i<Utils.NUM_WORKERS;i++)
        {
            SparkNLPServer server = new SparkNLPServer(Utils.RANGE_START + i);
            server.start();
            servers.add(server);
            //server.blockUntilShutdown();
        }
        for (SparkNLPServer e: servers) {
            e.blockUntilShutdown();
        }
    }

    private static class SparkNLPService extends sparknlp_asyncGrpc.sparknlp_asyncImplBase {
        SparkNLPManager manager;
        SparkNLPService() {
            this.manager = new SparkNLPManager();
        }

        public void clf1m(nlp_input text, StreamObserver<nlp_output> responseObserver) {
            manager.loadPipelines(1);
            String fs = text.getText();
            String res = this.manager.clf(fs);
            responseObserver.onNext( nlp_output.newBuilder().setResult(res).build());
            responseObserver.onCompleted();
        }
        public void clf10m(nlp_input text, StreamObserver<nlp_output> responseObserver) {
            manager.loadPipelines(10);
            String fs = text.getText();
            String res = this.manager.clf(fs);
            responseObserver.onNext( nlp_output.newBuilder().setResult(res).build());
            responseObserver.onCompleted();
        }
        public void clf100m(nlp_input text, StreamObserver<nlp_output> responseObserver) {
            manager.loadPipelines(100);
            String fs = text.getText();
            String res = this.manager.clf(fs);
            responseObserver.onNext( nlp_output.newBuilder().setResult(res).build());
            responseObserver.onCompleted();
        }

        public void clf200m(nlp_input text, StreamObserver<nlp_output> responseObserver) {
            manager.loadPipelines(200);
            String fs = text.getText();
            String res = this.manager.clf(fs);
            responseObserver.onNext( nlp_output.newBuilder().setResult(res).build());
            responseObserver.onCompleted();
        }

        public void clf300m(nlp_input text, StreamObserver<nlp_output> responseObserver) {
            manager.loadPipelines(300);
            String fs = text.getText();
            String res = this.manager.clf(fs);
            responseObserver.onNext( nlp_output.newBuilder().setResult(res).build());
            responseObserver.onCompleted();
        }
    }
}
