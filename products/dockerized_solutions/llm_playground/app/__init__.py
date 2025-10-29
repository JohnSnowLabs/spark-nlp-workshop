from loguru import logger
import os
# Define custom format without file details
_f = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>"

# Remove the default logger
logger.remove()

# Add a new console logger with the custom format
logger.add(lambda msg: print(msg, end=""), format=_f, level=os.environ.get("LOGGING_MODE", "INFO").upper())
try:
    from jsl_i import start as app_start

    app_start()
except ModuleNotFoundError:
    logger.error("*********app is not ready for production use, running in dev mode****")


__all__ = ["logger"]