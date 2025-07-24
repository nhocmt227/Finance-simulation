import sqlite3
import os
from internal.server.config.config import CONFIG

db_folder = os.path.abspath("db")
db_name = CONFIG.database.db_name or "finance.db"
DATABASE = os.path.join(db_folder, db_name)


def create_tables():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hash TEXT NOT NULL,
            cash NUMERIC NOT NULL DEFAULT 10000.00 CHECK (cash >= 0)
        );

        CREATE TABLE IF NOT EXISTS history_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('buy', 'sell')),
            stock_symbol TEXT NOT NULL,
            stock_price NUMERIC NOT NULL,
            shares_amount INTEGER NOT NULL CHECK (shares_amount > 0),
            time DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS user_stocks (
            user_id INTEGER NOT NULL,
            stock_symbol TEXT NOT NULL,
            shares_amount INTEGER NOT NULL CHECK (shares_amount > 0),
            PRIMARY KEY (user_id, stock_symbol),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS stock_status (
            stock_symbol TEXT NOT NULL PRIMARY KEY,
            stock_price NUMERIC NOT NULL,
            time DATETIME NOT NULL 
        );
                      
         
        
                            """
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database initialize successfully")
