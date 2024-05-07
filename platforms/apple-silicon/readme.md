## Installation for Apple Silicon (M1, M2, M3)

Starting from version 4.0.0, Spark NLP has experimental support for apple silicon.

Make sure the following prerequisites are set:

1. Installing SDKMAN, you can follow the official documentation at https://sdkman.io/install
    - `$ curl -s "https://get.sdkman.io" | bash`
    - `source "$HOME/.sdkman/bin/sdkman-init.sh"`
    - `sdk list java`  
    list available java libraries:

2. Installing Java
    - `sdk install java 8.0.402-amzn` 
    - `whereis java`
    - `java -version`

3. Installing MiniConda, you can follow the official documentation at https://docs.anaconda.com/free/miniconda/#quick-command-line-install  
    - `mkdir -p ~/miniconda3`
    - `curl https://repo.anaconda.com/miniconda/Miniconda3-py39_23.11.0-2-MacOSX-arm64.sh -o ~/miniconda3/miniconda.sh` PS: you can change python version to 3.10 or 3.11
    - `bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3`
    - `~/miniconda3/bin/conda init bash`
    - `~/miniconda3/bin/conda init zsh`
    - `source miniconda3/bin/activate`

4. Installing `jupyter environments` or you can install it via `VSCode`

    ```bash
    # base environment
    conda --version
    java -version
    conda activate
    pip install pyspark==3.4.0
    pip install jupyter
    conda env config vars set PYSPARK_PYTHON=python
    conda activate 
    conda env config vars set PYSPARK_DRIVER_PYTHON=jupyter
    conda activate 
    conda env config vars set PYSPARK_DRIVER_python_OPTS=notebook
    conda activate 
    jupyter notebook
    ```

    ```bash
    # new sparknlp environment
    conda --version
    java -version
    conda create -n sparknlp python=3.9 -y
    conda activate sparknlp
    pip install pyspark==3.4.0
    pip install jupyter
    conda env config vars set PYSPARK_PYTHON=python
    conda activate sparknlp
    conda env config vars set PYSPARK_DRIVER_PYTHON=jupyter
    conda activate sparknlp
    conda env config vars set PYSPARK_DRIVER_python_OPTS=notebook
    conda activate sparknlp
    jupyter notebook
    ```

5. Installing Spark NLP Healthcare 

please see the [Spark NLP Healthcare Installation Notebook](https://github.com/JohnSnowLabs/spark-nlp-workshop/blob/master/platforms/apple-silicon/installation.ipynb)


