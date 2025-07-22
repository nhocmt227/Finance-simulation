import os
import logging
from internal.server.config.config import CONFIG

# Set up log directory and file
log_dir = os.path.join(os.path.dirname(__file__), '../../../logs')
os.makedirs(log_dir, exist_ok=True)  # Only runs once at startup

log_file = os.path.join(log_dir, CONFIG.core.logger.filename)

# --- Configure logging ---
logger = logging.getLogger("app_logger")

if not logger.hasHandlers():  # Prevent duplicate handlers if re-imported
    level = getattr(logging, CONFIG.core.logger.level.upper(), logging.INFO)
    logger.setLevel(level)

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)