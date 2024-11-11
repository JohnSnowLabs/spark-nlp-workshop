import argparse

import logging

from FlaskManager import FlaskManager
from SparkNLPManager import SparkNLPManager

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='ZeroShotApp',
        description='A lightweight app to check your prompts with ZeroShot models')

    parser.add_argument('domain', nargs='?')  # positional argument
    args = parser.parse_args()

    domain = args.domain if args.domain is not None else 'finance'

    recognized_domains = ['finance', 'legal', 'medical']
    if domain not in recognized_domains:
        logging.error(f"Unrecognized domain: {domain}. Please use any of these: {str(recognized_domains)}")
    else:
        flask_manager = FlaskManager()
        spark_manager = SparkNLPManager(domain)
        flask_manager.spark_manager = spark_manager
