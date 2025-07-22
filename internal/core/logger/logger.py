# internal/server/logger.py
import logging

logger = logging.getLogger("server_logger")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs/server.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
