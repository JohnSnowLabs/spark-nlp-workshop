#!/bin/bash

export_json () {
    for s in $(echo $values | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' $1 ); do
        export $s
    done
}

export_json "/content/sparknlp_keys.json"

pip install --upgrade spark-nlp-jsl==$JSL_VERSION --user --extra-index-url https://pypi.johnsnowlabs.com/$SECRET

if [ $? != 0 ];
then
    exit 1
fi

pip install --upgrade spark-nlp-display

streamlit run /content/sparknlp_ner_playground.py --server.port=8501