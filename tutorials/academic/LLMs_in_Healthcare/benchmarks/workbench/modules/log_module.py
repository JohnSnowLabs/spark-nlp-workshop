import logging

def setup_logger(logger_name, level=logging.INFO):
    # create logger object
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # create stream handler and set level to INFO
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to handlers
    ch.setFormatter(formatter)

    # add handlers to logger
    logger.addHandler(ch)

    return logger