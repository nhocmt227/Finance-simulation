import sqlite3
from flask import g
from dotenv import load_dotenv
import os

# take environment variables from .env.
load_dotenv()  
DATABASE = os.getenv("DATABASE")

def get_db():
    """Establish and return a database connection.

    Connects to the SQLite database specified in DATABASE, storing the connection in Flask’s
    g object to reuse it throughout the request. The row_factory is set to enable dictionary-like
    access to rows.
    """
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row  # Enables dictionary-like row access
    return g.db

def close_db(exception=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
