import os

import sqlite3
from flask import g
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from datetime import datetime


DATABASE = "finance.db"

def get_db():
    """Get a database connection"""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row  # Enables dictionary-like row access
    return g.db


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    conn = get_db()

    # Get list of distinct stocks purchased
    rows = conn.execute(
        "SELECT DISTINCT stock_symbol FROM status WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    stocks = []

    for row in rows:
        # Lookup current stock price
        stock = lookup(row["stock_symbol"])
        if stock is None:
            continue  # or handle error
        
        # Get total shares for this stock
        total_shares_row = conn.execute(
            "SELECT SUM(shares) as total_shares FROM status WHERE stock_symbol = ? AND user_id = ?",
            (stock["symbol"], session["user_id"])
        ).fetchone()
        stock["shares"] = total_shares_row["total_shares"]
        stock["total"] = stock["price"] * stock["shares"]
        stocks.append(stock)

    # Get cash balance
    # Get cash balance
    cash_row = conn.execute(
        "SELECT cash FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    cash_balance = cash_row["cash"]

    # Calculate grand total (cash + total value of stocks)
    grand_total = cash_balance + sum(stock["total"] for stock in stocks)
    
    return render_template("index.html", stocks=stocks, cash_balance=cash_balance, grand_total=grand_total)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        # Get stock price
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("No stock found")
        stock_information = lookup(symbol)
        if stock_information == None:
            return apology("Invalid stock symbol")

        # Get number of shares
        shares = request.form.get("shares")
        if not shares:
            return apology("Must provide shares")
        try:
            shares = int(shares)
            if shares <= 0:
                return apology("Shares must be positive")
        except ValueError:
            return apology("Invalid shares")

        # Check for remaining cash in the account
        remaining_cash = get_db().execute(
            "SELECT cash FROM users WHERE id = ?",
            session["user_id"]
        )
        if not remaining_cash:
            return apology("Error retrieving remaining cash.")
        try:
            remaining_cash = remaining_cash[0]["cash"]
            remaining_cash = float(remaining_cash)
        except ValueError:
            return apology("Unexpected error when access database")

        amount_bought = float(stock_information["price"]) * shares
        if remaining_cash < amount_bought:
            return apology("Insufficient cash in your account")

        try:
            get_db().execute("BEGIN TRANSACTION")
            # Subtract cash from user's account
            get_db().execute("UPDATE users SET cash = ? WHERE id = ?", remaining_cash - amount_bought, session["user_id"])

            # Insert transaction information into database
            get_db().execute("INSERT INTO history (user_id, type, stock_symbol, stock_price, shares, time) VALUES (?, ?, ?, ?, ?, ?)",
                        session["user_id"],
                        "buy",
                        stock_information["symbol"],
                        stock_information["price"],
                        shares,
                        datetime.now())

            get_db().execute("INSERT INTO status (user_id, stock_symbol, shares) VALUES (?, ?, ?)",
                        session["user_id"],
                        stock_information["symbol"],
                        shares)
            get_db().execute("COMMIT")
        except Exception as e:
            get_db().execute("ROLLBACK")
            return apology(f"Transaction failed: {str(e)}")
        # Redirect to main page
        return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = get_db().execute(
        "SELECT * FROM history WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    return render_template("history.html", history=history)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        # Get symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("No symbol found")

        # get stock information
        stock_information = lookup(symbol)
        if stock_information is None:
            return apology("Invalid stock symbol")


        return render_template("quoted.html", information=stock_information)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        # Get data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Data validation
        if not username:
            return apology("No username found")
        
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user is not None:
            return apology("Username existed")
        
        if not password:
            return apology("No password found")
        if not confirmation:
            return apology("Must provide confirmation")
        if password != confirmation:
            return apology("Passwords do not match")

        password_hash = generate_password_hash(password)
        
        # Insert data into database
        db = get_db()
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            (username, password_hash)
        )
        db.commit()  # Commit the changes
        
        return redirect("/login")
    
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    array_of_stocks = get_db().execute("SELECT DISTINCT stock_symbol FROM status WHERE user_id = ?", (session["user_id"],)).fetchall()

    if request.method == "GET":
        return render_template("sell.html", stocks=array_of_stocks)
    else:
        # Stock validation
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Require symbol")
        stock = lookup(symbol)
        if stock == None:
            return apology("Stock not found")

        # Shares validation
        shares = request.form.get("shares")
        if not shares:
            return apology("Require shares")
        try:
            shares = int(shares)
        except ValueError:
            return apology("Invalid shares")

        result = get_db().execute("SELECT SUM(shares) FROM status WHERE user_id = ? AND stock_symbol = ?", session["user_id"], symbol)
        remaining_shares = result[0]["SUM(shares)"]
        if shares <= 0 or shares > remaining_shares:
            return apology("Invalid shares")

        try:
            # Start a transaction
            get_db().execute("BEGIN TRANSACTION")

            # Update the total cash of user
            remaining_cash = get_db().execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            amount_sell = stock["price"] * shares
            get_db().execute("UPDATE users SET cash = ? WHERE id = ?", remaining_cash + amount_sell, session["user_id"])

            # Update transaction history
            get_db().execute("INSERT INTO status (user_id, stock_symbol, shares) VALUES (?, ?, ?)",
                        session["user_id"],
                        symbol,
                        -shares)
            get_db().execute("INSERT INTO history (user_id, type, stock_symbol, stock_price, shares, time) VALUES (?, ?, ?, ?, ?, ?)",
                        session["user_id"],
                        "sell",
                        symbol,
                        stock["price"],
                        shares,
                        datetime.now())

            # Commit the transaction
            get_db().execute("COMMIT")

        except Exception as e:
            get_db().rollback()
            return apology(f"Transaction failed: {str(e)}")
        return redirect("/")



@app.teardown_appcontext
def close_db(exception):
    """Close the database connection at the end of the request"""
    db = g.pop("db", None)
    if db is not None:
        db.close()






