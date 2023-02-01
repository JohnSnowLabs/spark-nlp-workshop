import streamlit as st
import argparse

import logging

import config
from SparkNLPManager import start_spark, load_pipelines, pipelines, spark
from StreamlitManager import StreamlitManager


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ZeroShotApp',
        description='A lightweight app to check your prompts with ZeroShot models')

    parser.add_argument('action', nargs='?')  # positional argument
    parser.add_argument('domain', nargs='?')  # positional argument
    args = parser.parse_args()
    action = args.action

    if action == 'serve':
        domain = args.domain
        recognized_domains = ['finance', 'legal', 'medical']
        if domain not in recognized_domains:
            logging.error(f"Unrecognized domain: {domain}. Please use any of these: {str(recognized_domains)}")
        else:
            start_spark()
            logging.info(f"Spark Session (make sure is the same always): {id(spark)}")

            load_pipelines(domain)
            logging.info(f"Pipelines dict (make sure is the same always): {id(pipelines)}")

            streamlit_manager = StreamlitManager(domain, pipelines)
    else:
        logging.warning(f"Action not recognized: `{args.action}`. Ignoring.")

