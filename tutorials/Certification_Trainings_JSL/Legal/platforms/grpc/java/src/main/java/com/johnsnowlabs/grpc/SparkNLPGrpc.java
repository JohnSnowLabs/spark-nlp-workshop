package com.johnsnowlabs.grpc;

import static io.grpc.MethodDescriptor.generateFullMethodName;

/**
 * <pre>
 * Interface exported by the server.
 * </pre>
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.50.2)",
    comments = "Source: definition.proto")
@io.grpc.stub.annotations.GrpcGenerated
public final class SparkNLPGrpc {

  private SparkNLPGrpc() {}

  public static final String SERVICE_NAME = "routeguide.SparkNLP";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<nlp_input,
      nlp_output> getClfMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "clf",
      requestType = nlp_input.class,
      responseType = nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<nlp_input,
      nlp_output> getClfMethod() {
    io.grpc.MethodDescriptor<nlp_input, nlp_output> getClfMethod;
    if ((getClfMethod = SparkNLPGrpc.getClfMethod) == null) {
      synchronized (SparkNLPGrpc.class) {
        if ((getClfMethod = SparkNLPGrpc.getClfMethod) == null) {
          SparkNLPGrpc.getClfMethod = getClfMethod =
              io.grpc.MethodDescriptor.<nlp_input, nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "clf"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new SparkNLPMethodDescriptorSupplier("clf"))
              .build();
        }
      }
    }
    return getClfMethod;
  }

  private static volatile io.grpc.MethodDescriptor<nlp_input,
      nlp_output> getNerMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "ner",
      requestType = nlp_input.class,
      responseType = nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<nlp_input,
      nlp_output> getNerMethod() {
    io.grpc.MethodDescriptor<nlp_input, nlp_output> getNerMethod;
    if ((getNerMethod = SparkNLPGrpc.getNerMethod) == null) {
      synchronized (SparkNLPGrpc.class) {
        if ((getNerMethod = SparkNLPGrpc.getNerMethod) == null) {
          SparkNLPGrpc.getNerMethod = getNerMethod =
              io.grpc.MethodDescriptor.<nlp_input, nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "ner"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new SparkNLPMethodDescriptorSupplier("ner"))
              .build();
        }
      }
    }
    return getNerMethod;
  }

  private static volatile io.grpc.MethodDescriptor<nlp_input,
      nlp_output> getReMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "re",
      requestType = nlp_input.class,
      responseType = nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<nlp_input,
      nlp_output> getReMethod() {
    io.grpc.MethodDescriptor<nlp_input, nlp_output> getReMethod;
    if ((getReMethod = SparkNLPGrpc.getReMethod) == null) {
      synchronized (SparkNLPGrpc.class) {
        if ((getReMethod = SparkNLPGrpc.getReMethod) == null) {
          SparkNLPGrpc.getReMethod = getReMethod =
              io.grpc.MethodDescriptor.<nlp_input, nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "re"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new SparkNLPMethodDescriptorSupplier("re"))
              .build();
        }
      }
    }
    return getReMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static SparkNLPStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<SparkNLPStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<SparkNLPStub>() {
        @java.lang.Override
        public SparkNLPStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new SparkNLPStub(channel, callOptions);
        }
      };
    return SparkNLPStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static SparkNLPBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<SparkNLPBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<SparkNLPBlockingStub>() {
        @java.lang.Override
        public SparkNLPBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new SparkNLPBlockingStub(channel, callOptions);
        }
      };
    return SparkNLPBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static SparkNLPFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<SparkNLPFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<SparkNLPFutureStub>() {
        @java.lang.Override
        public SparkNLPFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new SparkNLPFutureStub(channel, callOptions);
        }
      };
    return SparkNLPFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * Interface exported by the server.
   * </pre>
   */
  public static abstract class SparkNLPImplBase implements io.grpc.BindableService {

    /**
     * <pre>
     *A simple RPC where the client sends a request to the server using the stub and waits for a response to come back,
     *just like a normal function call.
     * </pre>
     */
    public void clf(nlp_input request,
        io.grpc.stub.StreamObserver<nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getClfMethod(), responseObserver);
    }

    /**
     */
    public void ner(nlp_input request,
        io.grpc.stub.StreamObserver<nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getNerMethod(), responseObserver);
    }

    /**
     */
    public void re(nlp_input request,
        io.grpc.stub.StreamObserver<nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getReMethod(), responseObserver);
    }

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getClfMethod(),
            io.grpc.stub.ServerCalls.asyncUnaryCall(
              new MethodHandlers<
                nlp_input,
                nlp_output>(
                  this, METHODID_CLF)))
          .addMethod(
            getNerMethod(),
            io.grpc.stub.ServerCalls.asyncUnaryCall(
              new MethodHandlers<
                nlp_input,
                nlp_output>(
                  this, METHODID_NER)))
          .addMethod(
            getReMethod(),
            io.grpc.stub.ServerCalls.asyncUnaryCall(
              new MethodHandlers<
                nlp_input,
                nlp_output>(
                  this, METHODID_RE)))
          .build();
    }
  }

  /**
   * <pre>
   * Interface exported by the server.
   * </pre>
   */
  public static final class SparkNLPStub extends io.grpc.stub.AbstractAsyncStub<SparkNLPStub> {
    private SparkNLPStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected SparkNLPStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new SparkNLPStub(channel, callOptions);
    }

    /**
     * <pre>
     *A simple RPC where the client sends a request to the server using the stub and waits for a response to come back,
     *just like a normal function call.
     * </pre>
     */
    public void clf(nlp_input request,
        io.grpc.stub.StreamObserver<nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getClfMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void ner(nlp_input request,
        io.grpc.stub.StreamObserver<nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getNerMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void re(nlp_input request,
        io.grpc.stub.StreamObserver<nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncUnaryCall(
          getChannel().newCall(getReMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * <pre>
   * Interface exported by the server.
   * </pre>
   */
  public static final class SparkNLPBlockingStub extends io.grpc.stub.AbstractBlockingStub<SparkNLPBlockingStub> {
    private SparkNLPBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected SparkNLPBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new SparkNLPBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     *A simple RPC where the client sends a request to the server using the stub and waits for a response to come back,
     *just like a normal function call.
     * </pre>
     */
    public nlp_output clf(nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getClfMethod(), getCallOptions(), request);
    }

    /**
     */
    public nlp_output ner(nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getNerMethod(), getCallOptions(), request);
    }

    /**
     */
    public nlp_output re(nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingUnaryCall(
          getChannel(), getReMethod(), getCallOptions(), request);
    }
  }

  /**
   * <pre>
   * Interface exported by the server.
   * </pre>
   */
  public static final class SparkNLPFutureStub extends io.grpc.stub.AbstractFutureStub<SparkNLPFutureStub> {
    private SparkNLPFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected SparkNLPFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new SparkNLPFutureStub(channel, callOptions);
    }

    /**
     * <pre>
     *A simple RPC where the client sends a request to the server using the stub and waits for a response to come back,
     *just like a normal function call.
     * </pre>
     */
    public com.google.common.util.concurrent.ListenableFuture<nlp_output> clf(
        nlp_input request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getClfMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<nlp_output> ner(
        nlp_input request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getNerMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<nlp_output> re(
        nlp_input request) {
      return io.grpc.stub.ClientCalls.futureUnaryCall(
          getChannel().newCall(getReMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_CLF = 0;
  private static final int METHODID_NER = 1;
  private static final int METHODID_RE = 2;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final SparkNLPImplBase serviceImpl;
    private final int methodId;

    MethodHandlers(SparkNLPImplBase serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_CLF:
          serviceImpl.clf((nlp_input) request,
              (io.grpc.stub.StreamObserver<nlp_output>) responseObserver);
          break;
        case METHODID_NER:
          serviceImpl.ner((nlp_input) request,
              (io.grpc.stub.StreamObserver<nlp_output>) responseObserver);
          break;
        case METHODID_RE:
          serviceImpl.re((nlp_input) request,
              (io.grpc.stub.StreamObserver<nlp_output>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        default:
          throw new AssertionError();
      }
    }
  }

  private static abstract class SparkNLPBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    SparkNLPBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return RouteGuideProto.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("SparkNLP");
    }
  }

  private static final class SparkNLPFileDescriptorSupplier
      extends SparkNLPBaseDescriptorSupplier {
    SparkNLPFileDescriptorSupplier() {}
  }

  private static final class SparkNLPMethodDescriptorSupplier
      extends SparkNLPBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    SparkNLPMethodDescriptorSupplier(String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (SparkNLPGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new SparkNLPFileDescriptorSupplier())
              .addMethod(getClfMethod())
              .addMethod(getNerMethod())
              .addMethod(getReMethod())
              .build();
        }
      }
    }
    return result;
  }
}
