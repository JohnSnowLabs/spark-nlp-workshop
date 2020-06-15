import os

os.system('apt-get install -y openjdk-8-jdk-headless -qq > /dev/null')

os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["PATH"] = os.environ["JAVA_HOME"] + "/bin:" + os.environ["PATH"]

# Install pyspark
os.system("pip install --ignore-installed -q pyspark==2.4.4")
os.system("pip install --ignore-installed -q spark-nlp==2.5.1")