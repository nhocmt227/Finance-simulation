import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from datetime import datetime

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


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
    """Show portfolio of stocks"""

    # Get list of stocks purchased
    array_of_stocks = db.execute(
        "SELECT DISTINCT stock_symbol FROM status WHERE user_id = ?",
        session["user_id"]
    )
    stocks = []
    for element in array_of_stocks:
        stock = lookup(element["stock_symbol"])
        stock["shares"] = db.execute(
            "SELECT SUM(shares) FROM status WHERE stock_symbol = ?",
            stock["symbol"]
        )[0]["SUM(shares)"]
        stock["total"] = stock["price"] * stock["shares"]
        stocks.append(stock)

    # Get cash balance
    cash_balance = db.execute(
        "SELECT cash from users where id = ?",
        session["user_id"]
    )[0]["cash"]

    # Get grand_total
    grand_total = cash_balance
    for stock in stocks:
        grand_total += stock["total"]
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
        remaining_cash = db.execute(
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
            db.execute("BEGIN TRANSACTION")
            # Subtract cash from user's account
            db.execute("UPDATE users SET cash = ? WHERE id = ?", remaining_cash - amount_bought, session["user_id"])

            # Insert transaction information into database
            db.execute("INSERT INTO history (user_id, type, stock_symbol, stock_price, shares, time) VALUES (?, ?, ?, ?, ?, ?)",
                        session["user_id"],
                        "buy",
                        stock_information["symbol"],
                        stock_information["price"],
                        shares,
                        datetime.now())

            db.execute("INSERT INTO status (user_id, stock_symbol, shares) VALUES (?, ?, ?)",
                        session["user_id"],
                        stock_information["symbol"],
                        shares)
            db.execute("COMMIT")
        except Exception as e:
            db.execute("ROLLBACK")
            return apology(f"Transaction failed: {str(e)}")
        # Redirect to main page
        return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])
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
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

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
        if stock_information == None:
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
        existed_username = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existed_username:
            return apology("Username existed")

        if not password:
            return apology("No password found")
        if not confirmation:
            return apology("Must provide confirmation")
        if password != confirmation:
            return apology("Passwords do not match")

        password_hash = generate_password_hash(password)

        # Insert data into database
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            password_hash
        )
        return redirect("/login")
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    array_of_stocks = db.execute(
        "SELECT DISTINCT stock_symbol FROM status WHERE user_id = ?",
        session["user_id"]
    )

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

        result = db.execute("SELECT SUM(shares) FROM status WHERE user_id = ? AND stock_symbol = ?", session["user_id"], symbol)
        remaining_shares = result[0]["SUM(shares)"]
        if shares <= 0 or shares > remaining_shares:
            return apology("Invalid shares")

        try:
            # Start a transaction
            db.execute("BEGIN TRANSACTION")

            # Update the total cash of user
            remaining_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            amount_sell = stock["price"] * shares
            db.execute("UPDATE users SET cash = ? WHERE id = ?", remaining_cash + amount_sell, session["user_id"])

            # Update transaction history
            db.execute("INSERT INTO status (user_id, stock_symbol, shares) VALUES (?, ?, ?)",
                        session["user_id"],
                        symbol,
                        -shares)
            db.execute("INSERT INTO history (user_id, type, stock_symbol, stock_price, shares, time) VALUES (?, ?, ?, ?, ?, ?)",
                        session["user_id"],
                        "sell",
                        symbol,
                        stock["price"],
                        shares,
                        datetime.now())

            # Commit the transaction
            db.execute("COMMIT")

        except Exception as e:
            db.execute("ROLLBACK")
            return apology(f"Transaction failed: {str(e)}")
        return redirect("/")










