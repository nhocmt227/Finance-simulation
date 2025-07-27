import os
import logging
from internal.server.config import CONFIG


def get_logger() -> logging.Logger:
    """
    Creates and returns a singleton logger instance based on config settings.
    Prevents reinitialization if already created.
    """

    print("------------------------ LOGGER INITIALIZE ------------------------")

    logger = logging.getLogger("app_logger")

    if logger.hasHandlers():
        return logger  # Return existing instance

    # Setup log directory
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs"))
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, CONFIG.core.logger.filename)
    log_level = getattr(logging, CONFIG.core.logger.level.upper(), logging.INFO)

    logger.setLevel(log_level)

    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

