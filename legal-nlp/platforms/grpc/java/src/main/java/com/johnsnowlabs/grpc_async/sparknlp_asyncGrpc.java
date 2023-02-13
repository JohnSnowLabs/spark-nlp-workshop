package com.johnsnowlabs.grpc_async;

import io.grpc.stub.ServerCalls;

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
public final class sparknlp_asyncGrpc {

  private sparknlp_asyncGrpc() {}

  public static final String SERVICE_NAME = "grpc_async.sparknlp_async";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf1mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "clf_1m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf1mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getClf1mMethod;
    if ((getClf1mMethod = sparknlp_asyncGrpc.getClf1mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getClf1mMethod = sparknlp_asyncGrpc.getClf1mMethod) == null) {
          sparknlp_asyncGrpc.getClf1mMethod = getClf1mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "clf_1m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("clf_1m"))
              .build();
        }
      }
    }
    return getClf1mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf10mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "clf_10m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf10mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getClf10mMethod;
    if ((getClf10mMethod = sparknlp_asyncGrpc.getClf10mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getClf10mMethod = sparknlp_asyncGrpc.getClf10mMethod) == null) {
          sparknlp_asyncGrpc.getClf10mMethod = getClf10mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "clf_10m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("clf_10m"))
              .build();
        }
      }
    }
    return getClf10mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf100mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "clf_100m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf100mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getClf100mMethod;
    if ((getClf100mMethod = sparknlp_asyncGrpc.getClf100mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getClf100mMethod = sparknlp_asyncGrpc.getClf100mMethod) == null) {
          sparknlp_asyncGrpc.getClf100mMethod = getClf100mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "clf_100m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("clf_100m"))
              .build();
        }
      }
    }
    return getClf100mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf200mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "clf_200m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf200mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getClf200mMethod;
    if ((getClf200mMethod = sparknlp_asyncGrpc.getClf200mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getClf200mMethod = sparknlp_asyncGrpc.getClf200mMethod) == null) {
          sparknlp_asyncGrpc.getClf200mMethod = getClf200mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "clf_200m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("clf_200m"))
              .build();
        }
      }
    }
    return getClf200mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf300mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "clf_300m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClf300mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getClf300mMethod;
    if ((getClf300mMethod = sparknlp_asyncGrpc.getClf300mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getClf300mMethod = sparknlp_asyncGrpc.getClf300mMethod) == null) {
          sparknlp_asyncGrpc.getClf300mMethod = getClf300mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "clf_300m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("clf_300m"))
              .build();
        }
      }
    }
    return getClf300mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClfner1mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "clfner_1m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getClfner1mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getClfner1mMethod;
    if ((getClfner1mMethod = sparknlp_asyncGrpc.getClfner1mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getClfner1mMethod = sparknlp_asyncGrpc.getClfner1mMethod) == null) {
          sparknlp_asyncGrpc.getClfner1mMethod = getClfner1mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "clfner_1m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("clfner_1m"))
              .build();
        }
      }
    }
    return getClfner1mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf1mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "docclf_1m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf1mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getDocclf1mMethod;
    if ((getDocclf1mMethod = sparknlp_asyncGrpc.getDocclf1mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getDocclf1mMethod = sparknlp_asyncGrpc.getDocclf1mMethod) == null) {
          sparknlp_asyncGrpc.getDocclf1mMethod = getDocclf1mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "docclf_1m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("docclf_1m"))
              .build();
        }
      }
    }
    return getDocclf1mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf10mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "docclf_10m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf10mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getDocclf10mMethod;
    if ((getDocclf10mMethod = sparknlp_asyncGrpc.getDocclf10mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getDocclf10mMethod = sparknlp_asyncGrpc.getDocclf10mMethod) == null) {
          sparknlp_asyncGrpc.getDocclf10mMethod = getDocclf10mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "docclf_10m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("docclf_10m"))
              .build();
        }
      }
    }
    return getDocclf10mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf100mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "docclf_100m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf100mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getDocclf100mMethod;
    if ((getDocclf100mMethod = sparknlp_asyncGrpc.getDocclf100mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getDocclf100mMethod = sparknlp_asyncGrpc.getDocclf100mMethod) == null) {
          sparknlp_asyncGrpc.getDocclf100mMethod = getDocclf100mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "docclf_100m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("docclf_100m"))
              .build();
        }
      }
    }
    return getDocclf100mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf200mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "docclf_200m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf200mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getDocclf200mMethod;
    if ((getDocclf200mMethod = sparknlp_asyncGrpc.getDocclf200mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getDocclf200mMethod = sparknlp_asyncGrpc.getDocclf200mMethod) == null) {
          sparknlp_asyncGrpc.getDocclf200mMethod = getDocclf200mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "docclf_200m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("docclf_200m"))
              .build();
        }
      }
    }
    return getDocclf200mMethod;
  }

  private static volatile io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf300mMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "docclf_300m",
      requestType = com.johnsnowlabs.grpc_async.nlp_input.class,
      responseType = com.johnsnowlabs.grpc_async.nlp_output.class,
      methodType = io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
  public static io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input,
      com.johnsnowlabs.grpc_async.nlp_output> getDocclf300mMethod() {
    io.grpc.MethodDescriptor<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output> getDocclf300mMethod;
    if ((getDocclf300mMethod = sparknlp_asyncGrpc.getDocclf300mMethod) == null) {
      synchronized (sparknlp_asyncGrpc.class) {
        if ((getDocclf300mMethod = sparknlp_asyncGrpc.getDocclf300mMethod) == null) {
          sparknlp_asyncGrpc.getDocclf300mMethod = getDocclf300mMethod =
              io.grpc.MethodDescriptor.<com.johnsnowlabs.grpc_async.nlp_input, com.johnsnowlabs.grpc_async.nlp_output>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.SERVER_STREAMING)
              .setFullMethodName(generateFullMethodName(SERVICE_NAME, "docclf_300m"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_input.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  com.johnsnowlabs.grpc_async.nlp_output.getDefaultInstance()))
              .setSchemaDescriptor(new sparknlp_asyncMethodDescriptorSupplier("docclf_300m"))
              .build();
        }
      }
    }
    return getDocclf300mMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static sparknlp_asyncStub newStub(io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<sparknlp_asyncStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<sparknlp_asyncStub>() {
        @java.lang.Override
        public sparknlp_asyncStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new sparknlp_asyncStub(channel, callOptions);
        }
      };
    return sparknlp_asyncStub.newStub(factory, channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static sparknlp_asyncBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<sparknlp_asyncBlockingStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<sparknlp_asyncBlockingStub>() {
        @java.lang.Override
        public sparknlp_asyncBlockingStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new sparknlp_asyncBlockingStub(channel, callOptions);
        }
      };
    return sparknlp_asyncBlockingStub.newStub(factory, channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static sparknlp_asyncFutureStub newFutureStub(
      io.grpc.Channel channel) {
    io.grpc.stub.AbstractStub.StubFactory<sparknlp_asyncFutureStub> factory =
      new io.grpc.stub.AbstractStub.StubFactory<sparknlp_asyncFutureStub>() {
        @java.lang.Override
        public sparknlp_asyncFutureStub newStub(io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
          return new sparknlp_asyncFutureStub(channel, callOptions);
        }
      };
    return sparknlp_asyncFutureStub.newStub(factory, channel);
  }

  /**
   * <pre>
   * Interface exported by the server.
   * </pre>
   */
  public static abstract class sparknlp_asyncImplBase implements io.grpc.BindableService {

    /**
     * <pre>
     * A response-streaming RPC where the client sends a request to the server and gets a stream to read a sequence of
     * messages back.The client reads from the returned stream until there are no more messages.As you can see in the
     * example, you specify a response-streaming method by placing the stream keyword before the response type.
     * </pre>
     */
    public void clf1m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getClf1mMethod(), responseObserver);
    }

    /**
     */
    public void clf10m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getClf10mMethod(), responseObserver);
    }

    /**
     */
    public void clf100m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getClf100mMethod(), responseObserver);
    }

    /**
     */
    public void clf200m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getClf200mMethod(), responseObserver);
    }

    /**
     */
    public void clf300m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getClf300mMethod(), responseObserver);
    }

    /**
     */
    public void clfner1m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getClfner1mMethod(), responseObserver);
    }

    /**
     */
    public void docclf1m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDocclf1mMethod(), responseObserver);
    }

    /**
     */
    public void docclf10m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDocclf10mMethod(), responseObserver);
    }

    /**
     */
    public void docclf100m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDocclf100mMethod(), responseObserver);
    }

    /**
     */
    public void docclf200m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDocclf200mMethod(), responseObserver);
    }

    /**
     */
    public void docclf300m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall(getDocclf300mMethod(), responseObserver);
    }

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getClf1mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_CLF_1M)))
          .addMethod(
            getClf10mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_CLF_10M)))
          .addMethod(
            getClf100mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_CLF_100M)))
          .addMethod(
            getClf200mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_CLF_200M)))
          .addMethod(
            getClf300mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_CLF_300M)))
          .addMethod(
            getClfner1mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_CLFNER_1M)))
          .addMethod(
            getDocclf1mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_DOCCLF_1M)))
          .addMethod(
            getDocclf10mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_DOCCLF_10M)))
          .addMethod(
            getDocclf100mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_DOCCLF_100M)))
          .addMethod(
            getDocclf200mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_DOCCLF_200M)))
          .addMethod(
            getDocclf300mMethod(),
            io.grpc.stub.ServerCalls.asyncServerStreamingCall(
              new MethodHandlers<
                com.johnsnowlabs.grpc_async.nlp_input,
                com.johnsnowlabs.grpc_async.nlp_output>(
                  this, METHODID_DOCCLF_300M)))
          .build();
    }
  }

  /**
   * <pre>
   * Interface exported by the server.
   * </pre>
   */
  public static final class sparknlp_asyncStub extends io.grpc.stub.AbstractAsyncStub<sparknlp_asyncStub> {
    private sparknlp_asyncStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected sparknlp_asyncStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new sparknlp_asyncStub(channel, callOptions);
    }

    /**
     * <pre>
     * A response-streaming RPC where the client sends a request to the server and gets a stream to read a sequence of
     * messages back.The client reads from the returned stream until there are no more messages.As you can see in the
     * example, you specify a response-streaming method by placing the stream keyword before the response type.
     * </pre>
     */
    public void clf1m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getClf1mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void clf10m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getClf10mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void clf100m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getClf100mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void clf200m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getClf200mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void clf300m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getClf300mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void clfner1m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getClfner1mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void docclf1m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getDocclf1mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void docclf10m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getDocclf10mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void docclf100m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getDocclf100mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void docclf200m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getDocclf200mMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void docclf300m(com.johnsnowlabs.grpc_async.nlp_input request,
        io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output> responseObserver) {
      io.grpc.stub.ClientCalls.asyncServerStreamingCall(
          getChannel().newCall(getDocclf300mMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   * <pre>
   * Interface exported by the server.
   * </pre>
   */
  public static final class sparknlp_asyncBlockingStub extends io.grpc.stub.AbstractBlockingStub<sparknlp_asyncBlockingStub> {
    private sparknlp_asyncBlockingStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected sparknlp_asyncBlockingStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new sparknlp_asyncBlockingStub(channel, callOptions);
    }

    /**
     * <pre>
     * A response-streaming RPC where the client sends a request to the server and gets a stream to read a sequence of
     * messages back.The client reads from the returned stream until there are no more messages.As you can see in the
     * example, you specify a response-streaming method by placing the stream keyword before the response type.
     * </pre>
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> clf1m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getClf1mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> clf10m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getClf10mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> clf100m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getClf100mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> clf200m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getClf200mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> clf300m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getClf300mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> clfner1m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getClfner1mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> docclf1m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getDocclf1mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> docclf10m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getDocclf10mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> docclf100m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getDocclf100mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> docclf200m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getDocclf200mMethod(), getCallOptions(), request);
    }

    /**
     */
    public java.util.Iterator<com.johnsnowlabs.grpc_async.nlp_output> docclf300m(
        com.johnsnowlabs.grpc_async.nlp_input request) {
      return io.grpc.stub.ClientCalls.blockingServerStreamingCall(
          getChannel(), getDocclf300mMethod(), getCallOptions(), request);
    }
  }

  /**
   * <pre>
   * Interface exported by the server.
   * </pre>
   */
  public static final class sparknlp_asyncFutureStub extends io.grpc.stub.AbstractFutureStub<sparknlp_asyncFutureStub> {
    private sparknlp_asyncFutureStub(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected sparknlp_asyncFutureStub build(
        io.grpc.Channel channel, io.grpc.CallOptions callOptions) {
      return new sparknlp_asyncFutureStub(channel, callOptions);
    }
  }

  private static final int METHODID_CLF_1M = 0;
  private static final int METHODID_CLF_10M = 1;
  private static final int METHODID_CLF_100M = 2;
  private static final int METHODID_CLF_200M = 3;
  private static final int METHODID_CLF_300M = 4;
  private static final int METHODID_CLFNER_1M = 5;
  private static final int METHODID_DOCCLF_1M = 6;
  private static final int METHODID_DOCCLF_10M = 7;
  private static final int METHODID_DOCCLF_100M = 8;
  private static final int METHODID_DOCCLF_200M = 9;
  private static final int METHODID_DOCCLF_300M = 10;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final sparknlp_asyncImplBase serviceImpl;
    private final int methodId;

    MethodHandlers(sparknlp_asyncImplBase serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_CLF_1M:
          serviceImpl.clf1m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_CLF_10M:
          serviceImpl.clf10m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_CLF_100M:
          serviceImpl.clf100m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_CLF_200M:
          serviceImpl.clf200m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_CLF_300M:
          serviceImpl.clf300m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_CLFNER_1M:
          serviceImpl.clfner1m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_DOCCLF_1M:
          serviceImpl.docclf1m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_DOCCLF_10M:
          serviceImpl.docclf10m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_DOCCLF_100M:
          serviceImpl.docclf100m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_DOCCLF_200M:
          serviceImpl.docclf200m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
          break;
        case METHODID_DOCCLF_300M:
          serviceImpl.docclf300m((com.johnsnowlabs.grpc_async.nlp_input) request,
              (io.grpc.stub.StreamObserver<com.johnsnowlabs.grpc_async.nlp_output>) responseObserver);
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

  private static abstract class sparknlp_asyncBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    sparknlp_asyncBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return com.johnsnowlabs.grpc_async.SparkNLP.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("sparknlp_async");
    }
  }

  private static final class sparknlp_asyncFileDescriptorSupplier
      extends sparknlp_asyncBaseDescriptorSupplier {
    sparknlp_asyncFileDescriptorSupplier() {}
  }

  private static final class sparknlp_asyncMethodDescriptorSupplier
      extends sparknlp_asyncBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    sparknlp_asyncMethodDescriptorSupplier(String methodName) {
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
      synchronized (sparknlp_asyncGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new sparknlp_asyncFileDescriptorSupplier())
              .addMethod(getClf1mMethod())
              .addMethod(getClf10mMethod())
              .addMethod(getClf100mMethod())
              .addMethod(getClf200mMethod())
              .addMethod(getClf300mMethod())
              .addMethod(getClfner1mMethod())
              .addMethod(getDocclf1mMethod())
              .addMethod(getDocclf10mMethod())
              .addMethod(getDocclf100mMethod())
              .addMethod(getDocclf200mMethod())
              .addMethod(getDocclf300mMethod())
              .build();
        }
      }
    }
    return result;
  }
}
