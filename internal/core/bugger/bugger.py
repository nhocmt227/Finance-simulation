import os
import json
import logging
from internal.server.config import CONFIG


def get_bugger() -> logging.Logger:
    """
    Returns a singleton error-level logger for bug reports.
    Adds a `.log()` method that accepts dict or str.
    """

    print("------------------------ BUGGER INITIALIZE ------------------------")

    logger = logging.getLogger("bugger_logger")

    if logger.hasHandlers():
        return logger

    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs"))
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, CONFIG.core.bugger.filename)
    logger.setLevel(logging.ERROR)

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Attach a custom log method to log structured metadata
    def structured_log(metadata):
        if isinstance(metadata, dict):
            message = json.dumps(metadata)
        else:
            message = str(metadata)
        logger.error(message)

    logger.log = structured_log  # Dynamically attach method

    return logger
