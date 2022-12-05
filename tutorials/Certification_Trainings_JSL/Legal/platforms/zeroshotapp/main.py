import streamlit as st
import argparse

from SparkNLPManager import SparkNLPManager
import logging

from StreamlitManager import StreamlitManager


@st.experimental_singleton
def start_spark(dom):
    _spark_manager = None
    try:
        _spark_manager = SparkNLPManager(dom)
    except Exception as e:
        st.warning(f"Unable to spin up a spark session. Please click on 'Reboot' button")
        logging.error(f"Unable to spin up a spark session. Reason: {e}")

    return _spark_manager


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
            spark_manager = start_spark(domain)
            if spark_manager is not None:
                StreamlitManager(spark_manager)
            else:
                st.error("Error spinning up Spark. Please, click on the right top corner - 'Clear Cache' and then "
                         "reload the page")
    else:
        logging.warning(f"Action not recognized: `{args.action}`. Ignoring.")

