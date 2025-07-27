import sqlite3
from flask import g
import os
from internal.server.config import CONFIG
from internal.core.logger import logger

DB_NAME = CONFIG.database.db_name

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "db", DB_NAME)
DB_PATH = os.path.abspath(DB_PATH)  # Resolve full path


def get_db():
    """Establish and return a database connection.

    Connects to the SQLite database specified in DB_PATH, storing the connection in Flask’s
    g object to reuse it throughout the request. The row_factory is set to enable dictionary-like
    access to rows.
    """
    if "db" not in g:
        try:
            g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
            g.db.row_factory = sqlite3.Row
            logger.info(f"Database connection established: {DB_PATH}")
        except sqlite3.Error as e:
            logger.critical(f"Failed to connect to database: {e}")
            raise
    return g.db


def close_db(exception=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        try:
            db.close()
            logger.info("Database connection closed successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error closing database connection: {e}")
