import logging
import os
import json
from internal.server.config import CONFIG

# --- TODO: Add unit test if necessary ---

# Set up log directory
LOG_DIR = os.path.join(os.path.dirname(__file__), "../../../logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Only runs once at startup

LOG_FILE = os.path.join(LOG_DIR, CONFIG.core.bugger.filename)

# Create a dedicated logger for bugs
bugger = logging.getLogger("bugger_logger")

if not bugger.hasHandlers():
    bugger.setLevel(logging.ERROR)

    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    bugger.addHandler(handler)


def _log(metadata):
    """
    Logs an error with timestamp and metadata into the bugs.log file.

    Args:
        metadata (dict or str): Info about the error. Dict is preferred.
    """
    if isinstance(metadata, dict):
        message = json.dumps(metadata)
    else:
        message = str(metadata)

    bugger.error(message)


# Attach the function as a method of the logger
bugger.log = _log
