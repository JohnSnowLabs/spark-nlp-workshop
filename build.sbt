import sbt.Keys.unmanagedJars

val scalaLangVersion = "2.11.12"

val sparkVersion = "2.3.0"

unmanagedBase := baseDirectory.value / "lib"
unmanagedJars := (baseDirectory.value ** "*.jar").classpath

scalaSource := baseDirectory.value / "scala"

resolvers += "Maven Central" at "http://central.maven.org/maven2/"


val analyticsDependencies = Seq(
  "org.apache.spark" %% "spark-core" % sparkVersion,
  "org.apache.spark" %% "spark-mllib" % sparkVersion
)

val root = (project in file("."))
  .settings(
    name := "spark-nlp-workshop",
    organization := "com.johnsnowlabs.workshop",
    version := "1.0.0",
    scalaVersion := scalaLangVersion,
    libraryDependencies ++= analyticsDependencies
  )