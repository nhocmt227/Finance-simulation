CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    cash NUMERIC NOT NULL DEFAULT 10000.00 CHECK (cash >= 0)
);

CREATE TABLE IF NOT EXISTS sqlite_sequence(name,seq);

CREATE TABLE IF NOT EXISTS history_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('buy', 'sell')),
    stock_symbol TEXT NOT NULL,
    stock_price NUMERIC NOT NULL CHECK (stock_price > 0),
    shares_amount INTEGER NOT NULL CHECK (shares_amount > 0),
    platform_fee NUMERIC NOT NULL CHECK (platform_fee >= 0),
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

CREATE TABLE IF NOT EXISTS revenue (
    total_revenue NUMERIC NOT NULL DEFAULT 0
);