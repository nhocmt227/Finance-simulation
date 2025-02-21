import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv

from helpers import apology, login_required, usd, time_format
from datetime import datetime
from db import get_db, close_db
from API_handlers import lookup


# take environment variables from .env.
load_dotenv()  
# Retrieve the API key
API_KEY = os.getenv("API_KEY")





# Configure response information
@app.after_request
def after_request(response):
    """Modify response headers to prevent caching.

    This ensures that clients do not cache any responses.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def main():
    """Render the public index page for unauthenticated users."""
    if "user_id" in session:
        return redirect("/home")
    else:
        return render_template("public/index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login.

    GET: Render the login form.
    POST: Validate credentials and log the user in.
    """

    # Forget any user_id
    session.clear()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("auth/login.html")
    
    # User reached route via POST (as by submitting a form via POST)
    else:
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
        return redirect("/home")
    
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("auth/register.html")

    elif request.method == "POST":
        db = get_db()
        # Get data from frontend
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password-confirmation")

        # user data validation
        if not username:
            return apology("No username found")
        if not password:
            return apology("No password found")
        if not password_confirmation:
            return apology("Must provide confirmation")
        if len(username) < 8 or len(username) > 30:
            return apology("Username length must be from 8 to 30 characters")
        if len(password) < 8:
            return apology("Password length must be from 8 to 30 characters")
        if password != password_confirmation:
            return apology("Passwords do not match")
        
        # Check if username exist
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user is not None:
            return apology("Username existed")

        password_hash = generate_password_hash(password)
        
        try:
            # Save user data into database
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (username, password_hash)
            )
            db.commit()
            return redirect("/login")
        except sqlite3.IntegrityError as e:
            # This occur because UNIQUE constraint has been violated
            print(f"Error: {e}")
            return apology("Username existed")
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return apology("Unexpected error in /register")
    
    return render_template("auth/register.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")
    




@app.route("/home")
@login_required
def index():
    conn = get_db()

    # Get list of distinct stocks purchased
    rows = conn.execute(
        "SELECT DISTINCT stock_symbol FROM user_stocks WHERE user_id = ?",
        (session["user_id"],)
    ).fetchall()

    stocks = []

    for row in rows:
        # Lookup current stock price
        stock = lookup(row["stock_symbol"], API_KEY)
        if stock is None:
            continue  # or handle error
        
        # Get total shares for this stock
        total_shares_row = conn.execute(
            "SELECT shares_amount FROM user_stocks WHERE stock_symbol = ? AND user_id = ?",
            (stock["symbol"], session["user_id"])
        ).fetchone()
        stock["shares"] = total_shares_row["shares_amount"]
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
    
    return render_template("portfolio/home.html", stocks=stocks, cash_balance=cash_balance, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    db = get_db()

    if request.method == "GET":
        return render_template("portfolio/buy.html")
    
    else:
        # Get stock info from form
        stock_symbol = request.form.get("symbol")
        if not stock_symbol:
            return apology("No stock found")
        stock_info = lookup(stock_symbol, API_KEY)
        if not stock_info:
            return apology("Invalid stock symbol")

        # Get number of shares
        buy_amount = request.form.get("shares")
        if not buy_amount:
            return apology("Must provide shares")
        try:
            buy_amount = int(buy_amount)
            if buy_amount <= 0:
                return apology("Shares amount must be positive")
        except ValueError:
            return apology("Invalid shares amount")

        # Check for remaining cash in the account
        try:
            user = db.execute("SELECT cash FROM users WHERE id = ?", (session["user_id"],)).fetchone()
            if not user:
                return apology("User not found")
            remaining_cash = float(user["cash"])  
        except ValueError:
            return apology("Unexpected error when access database")

        # Calculate total cost of purchase
        amount_bought = float(stock_info["price"]) * buy_amount
        if remaining_cash < amount_bought:
            return apology("Insufficient cash in your account")
        try:
            db.execute("BEGIN TRANSACTION")

            # Deduct cash from user's account
            db.execute(
                "UPDATE users SET cash = ? WHERE id = ?",
                (remaining_cash - amount_bought, session["user_id"]),
            )

            # Insert stock status into portfolio (if exists, update instead)
            existing_stock = db.execute(
                "SELECT shares_amount FROM user_stocks WHERE user_id = ? AND stock_symbol = ?",
                (session["user_id"], stock_info["symbol"]),
            ).fetchone()

            if existing_stock:
                new_shares_amount = existing_stock["shares_amount"] + buy_amount
                db.execute(
                    "UPDATE user_stocks SET shares_amount = ? WHERE user_id = ? AND stock_symbol = ?",
                    (new_shares_amount, session["user_id"], stock_info["symbol"]),
                )
            else:
                db.execute(
                    "INSERT INTO user_stocks (user_id, stock_symbol, shares_amount) VALUES (?, ?, ?)",
                    (session["user_id"], stock_info["symbol"], buy_amount),
                )

            # Insert transaction into history table
            db.execute(
                "INSERT INTO history_logs (user_id, type, stock_symbol, stock_price, shares_amount, time) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (session["user_id"], "buy", stock_info["symbol"], stock_info["price"], buy_amount, datetime.now()),
            )

            db.execute("COMMIT")
        except sqlite3.IntegrityError as e: 
            db.rollback()
            print(f"Error: {e}")
            return apology(f"Transaction failed, /buy")
        
        except sqlite3.Error as e:
            db.rollback()
            print(f"Error: {e}")
            return apology(f"Transaction failed, /buy")
        
        # Redirect to main page
        return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history_logs = get_db().execute(
        "SELECT * FROM history_logs WHERE user_id = ? ORDER BY time DESC", (session["user_id"],)
    ).fetchall()
    return render_template("portfolio/history.html", history=history_logs)


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("portfolio/quote.html")
    else:
        # Get symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("No symbol found")

        # get stock information
        stock_information = lookup(symbol, API_KEY)
        print(stock_information)
        if stock_information is None:
            return apology("Invalid stock symbol")


        return render_template("portfolio/quoted.html", information=stock_information)




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    db = get_db()

    if request.method == "GET":
        # Fetch user's stocks
        array_of_stocks = db.execute("SELECT DISTINCT stock_symbol FROM user_stocks WHERE user_id = ?", (session["user_id"],)).fetchall()
        return render_template("portfolio/sell.html", stocks=array_of_stocks)
    else:
        # Validate stock symbol from frontend
        stock_symbol = request.form.get("symbol")
        if not stock_symbol:
            return apology("Require symbol")
        stock_info = lookup(stock_symbol, API_KEY)
        if not stock_info:
            return apology("Stock not found")

        # Validate sell amount from frontend
        sell_amount = request.form.get("shares")
        if not sell_amount:
            return apology("Require shares")
        try:
            sell_amount = int(sell_amount)
            if sell_amount < 0:
                return apology("Invalid number of shares")
        except ValueError:
            return apology("Invalid shares")

        # Get the user's available shares for this stock
        result = db.execute(
            "SELECT shares_amount FROM user_stocks WHERE user_id = ? AND stock_symbol = ?", 
            (session["user_id"], stock_symbol)
        ).fetchone()

        if result is None:
            return apology("Not enough shares to sell")
        remaining_shares = result["shares_amount"]

        if sell_amount > remaining_shares:
            return apology("Not enough shares to sell")

        try:
            # Start a transaction
            db.execute("BEGIN TRANSACTION")
            
            if sell_amount == remaining_shares:
                db.execute(
                    "DELETE FROM user_stocks WHERE user_id = ? AND stock_symbol = ?", 
                    (session["user_id"], stock_symbol)
                )
            else:
                new_shares = remaining_shares - sell_amount
                # Update stock holdings (subtract shares)
                db.execute(
                    "UPDATE user_stocks SET shares_amount = ? WHERE user_id = ? AND stock_symbol = ?",
                    (new_shares, session["user_id"], stock_symbol),
                )
            # Get user's current cash balance
            user_cash = db.execute(
                "SELECT cash FROM users WHERE id = ?", 
                (session["user_id"],)
            ).fetchone()

            if not user_cash:
                db.rollback()
                return apology("User not found")

            current_cash = float(user_cash["cash"])
            amount_sell = stock_info["price"] * sell_amount
            updated_cash = current_cash + amount_sell
                
            # Update user's cash
            db.execute(
                "UPDATE users SET cash = ? WHERE id = ?", 
                (updated_cash, session["user_id"])
            )

            # Update transaction history
            db.execute(
                "INSERT INTO history_logs (user_id, type, stock_symbol, stock_price, shares_amount, time) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (session["user_id"], "sell", stock_symbol, stock_info["price"], sell_amount, datetime.now()),
            )

            # Commit the transaction
            db.execute("COMMIT")

        except sqlite3.Error as e:
            db.rollback()
            print(f"Error: {e}")
            return apology(f"Transaction failed: /sell")
        
        except sqlite3.IntegrityError as e:
            db.rollback()
            print(f"Error: {e}")
            return apology(f"Transaction failed: /sell")
        
        return redirect("/home")

@app.route("/apologize", methods=["GET"])
def apologize():
    return apology("This feature is being implemented!")


@app.teardown_appcontext
def teardown_db(exception):
    """Close the database connection at the end of the request"""
    close_db(exception)



if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)