import os
import logging
from internal.server.config import CONFIG

# --- TODO: Add unit test if necessary ---
# --- TODO: Split logging logic based on the log level: DEBUG, INFO, WARNING, ERROR, CRITICAL ---


# Set up log directory and file
LOG_DIR = os.path.join(os.path.dirname(__file__), "../../../logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Only runs once at startup

LOG_FILE = os.path.join(LOG_DIR, CONFIG.core.logger.filename)

# --- Configure logging ---
logger = logging.getLogger("app_logger")

if not logger.hasHandlers():  # Prevent duplicate handlers if re-imported
    level = getattr(logging, CONFIG.core.logger.level.upper(), logging.INFO)
    logger.setLevel(level)

    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
