#!/bin/bash

install_flag=false
run_flag=false
env_pth=./sparknlp_env
jupyter_port=8805
pyspark_version=3.0.2
hc_json_path=false
ocr_json_path=false
comb_json_path=false

license_path=JohnSnowLabs/licenses
notebooks_path=JohnSnowLabs/example_notebooks

while getopts hirv:l:o:a:s:p: flag; do
    case "${flag}" in
        h)
            echo "Script for creating a virtual environment for running Spark NLP."
            echo "Options:"
            echo "        -h    show brief help"
            echo "        -i    install mode: create a virtual environment and install the library"
            echo "        -r    run mode: run a jupyter notebook"
            echo "        -v    path of virtual environment (default: $env_pth)"
            echo "        -j    path of license json for Spark NLP for Healthcare"
            echo "        -o    path of license json for Spark OCR"
            echo "        -a    path of a single license json for both Spark OCR and Spark NLP"
            echo "        -s    specify pyspark version"
            echo "        -p    specify port of jupyter notebook"
            echo "Instructions on running the script:"
            echo "    - For a fresh install, use the -i flag for installing the libraries in a new virtual environment. You can provide desired path for virtual env using -v flag, otherwise a default location of $env_pth will be selected. You also need to provide license json file paths for spark nlp for healthcare (and/or) spark ocr using -j, -o, -a flags."
            echo "    - Once your virtual env is configured, use the -r flag to run a jupyter notebook while specifying virtual env and license json paths."
            echo "    - You need to provide license json paths using -j (for Spark NLP for Healthcare), OR/AND -o (for Spark OCR), OR/AND -a (a single json for both Spark NLP for Healthcare & Spark OCR)."
            exit
            ;;
        i)  install_flag=true;;
        r)  run_flag=true;;
        v)  env_pth=$OPTARG;;
        j)  hc_json_path=$OPTARG;;
        o)  ocr_json_path=$OPTARG;;
        a)  comb_json_path=$OPTARG;;
        s)  pyspark_version=$OPTARG;;
        p)  jupyter_port=$OPTARG;;
    esac
done

if [ $OPTIND -eq 1 ]; 
then 
    echo "Please use -h flag to check for available options.";
fi

if [ "$install_flag" == false ] && [ "$run_flag" == false ]
then
    echo "Please specify the mode by selecting either -i (for fresh installation) or -r (run from existing environment)."
    exit
fi

if [ "$hc_json_path" == false ] && [ "$ocr_json_path" == false ]  && [ "$comb_json_path" == false ]
then
    echo "Please use -l , -o , and -a flags to provide json paths."
    echo "Please use -h flag to check for available options."
    exit
fi

export_json () {
    cp $1 $license_path
    for s in $(echo $values | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' $1 ); do
        export $s
    done
}

install_jsl(){
    
    echo "Installing Spark NLP for Healthcare (version: $JSL_VERSION) ..."

    pip install --upgrade -q spark-nlp==$PUBLIC_VERSION
    pip install --upgrade -q spark-nlp-display
    pip install --upgrade -q spark-nlp-jsl==$JSL_VERSION  --extra-index-url https://pypi.johnsnowlabs.com/$SECRET
    pip install --upgrade -q --no-dependencies nlu
}

install_ocr(){

    echo "Installing Spark OCR (version: $OCR_VERSION) ..."

    pip install --upgrade -q spark-nlp==$PUBLIC_VERSION
    pip install --upgrade -q spark-nlp-display
    pip install --upgrade --no-dependencies -q spark-ocr==$OCR_VERSION+spark30 --extra-index-url=https://pypi.johnsnowlabs.com/$SPARK_OCR_SECRET

}

download_notebooks(){

    mkdir -p $notebooks_path

    wget -q -P $notebooks_path https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/jupyter/docker_notebooks/Spark_NLP/Healthcare/1.Clinical_Named_Entity_Recognition_Model.ipynb
    wget -q -P $notebooks_path https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/jupyter/docker_notebooks/Spark_NLP/Healthcare/2.Clinical_Assertion_Model.ipynb
    wget -q -P $notebooks_path https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/jupyter/docker_notebooks/Spark_NLP/Healthcare/3.Clinical_Entity_Resolvers.ipynb
    wget -q -P $notebooks_path https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/jupyter/docker_notebooks/Spark_NLP/Healthcare/4.Clinical_DeIdentification.ipynb
    wget -q -P $notebooks_path https://raw.githubusercontent.com/JohnSnowLabs/spark-nlp-workshop/master/jupyter/docker_notebooks/Spark_OCR/5.Spark_OCR.ipynb
}

export PYSPARK_DRIVER_PYTHON=python3
export PYSPARK_PYTHON=python3
export DEBIAN_FRONTEND=noninteractive

mkdir -p JohnSnowLabs
mkdir -p $license_path

if [ "$install_flag" == true ]
then
    echo "Creating a virtual environment at $env_pth ..."
    python3 -m venv $env_pth --without-pip
    source $env_pth/bin/activate
    
    echo "Virtual environment created at $env_pth ..."
    echo "Installing libraries ..."
    
    sudo apt-get update -qq > /dev/null || apt-get update -qq > /dev/null
    sudo apt-get -y upgrade -qq > /dev/null || apt-get upgrade -qq > /dev/null
    sudo apt-get install -y jq -qq > /dev/null || apt-get install jq -qq > /dev/null
    sudo apt-get purge -y openjdk-11* -qq > /dev/null || apt-get purge -y openjdk-11* -qq > /dev/null
    sudo apt-get install -y openjdk-8-jdk-headless -qq > /dev/null || apt-get install -y openjdk-8-jdk-headless -qq > /dev/null
    sudo apt-get install -y build-essential python3-pip -qq > /dev/null || apt-get install -y build-essential python3-pip -qq > /dev/null
    
    pip3 install -q --upgrade pip
    pip install -q --upgrade environment_kernels
    pip install -q jupyter
    pip install -q pandas
    pip install -q --upgrade pyspark==$pyspark_version
    pip install -q --upgrade tensorflow
    pip install -q --upgrade scikit-image
    
    if ! [ "$hc_json_path" == false ]
    then
        echo "Reading HC License json from $hc_json_path ..."
        export_json "$hc_json_path"
        install_jsl
    fi
    
    if ! [ "$ocr_json_path" == false ]
    then
        echo "Reading OCR License json from $ocr_json_path ..."
        export_json "$ocr_json_path"
        install_ocr
    fi
    
    if ! [ "$comb_json_path" == false ]
    then
        echo "Reading Combined License json from $comb_json_path ..."
        export_json "$comb_json_path"
        install_jsl
        install_ocr
    fi
    
    echo "Libraries Installed ..."
    
    download_notebooks
    
    echo "Sample Notebooks Downloaded ..."
    echo ""
    echo "JSL libraries are installed in virtual env $env_pth. 
    What next?
    1. On your terminal run 'source ./$env_pth/bin/activate' to activate the virtual env. 
    2. Run 'jupyter notebook' to test the predefined notebooks available on ./JohnSnowLabs/example_notebooks folder."
    echo ""
    
fi

if [ "$run_flag" == true ]
then
    echo "Activating environment at $env_pth ..."
    source $env_pth/bin/activate
    
    if ! [ "$hc_json_path" == false ]
    then
        echo "Reading HC License json from $hc_json_path ..."
        export_json "$hc_json_path"
    fi
    
    if ! [ "$ocr_json_path" == false ]
    then
        echo "Reading OCR License json from $ocr_json_path ..."
        export_json "$ocr_json_path"
    fi
    
    if ! [ "$comb_json_path" == false ]
    then
        echo "Reading Combined License json from $comb_json_path ..."
        export_json "$comb_json_path"
    fi
    
    cd JohnSnowLabs
    echo "Running Jupyter Notebook at Port $jupyter_port ..."
    jupyter notebook --port=$jupyter_port --ip=0.0.0.0 --NotebookApp.token='' --NotebookApp.password='' --allow-root
fi
