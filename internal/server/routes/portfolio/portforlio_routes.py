import os
from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime
from dotenv import load_dotenv

from internal.server.model.sqlite_connection import get_db
from internal.server.utils.utils import apology, login_required
from internal.server.api.API_handlers import lookup
from internal.server.utils.exception import ApiLimitError
from internal.core.logger.logger import logger
from internal.core.bugger.bugger import bugger
import sqlite3

# take environment variables from .env.
load_dotenv()
# Retrieve the API key
API_KEY = os.getenv("API_KEY")

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/", methods=["GET"])
def main():
    """Render the public index page for unauthenticated users."""
    if "user_id" in session:
        return redirect("/home")
    else:
        return render_template("public/index.html")


@portfolio_bp.route("/home", methods=["GET"])
@login_required
def index():
    conn = get_db()
    logger.info(f"Fetching portfolio for user_id={session['user_id']}.")

    # Get list of distinct stocks purchased
    try:
        rows = conn.execute(
            "SELECT DISTINCT stock_symbol FROM user_stocks WHERE user_id = ?",
            (session["user_id"],),
        ).fetchall()
    except sqlite3.Error as e:
        logger.error(f"Database error when fetching distinct stocks: {e}")
        return apology("Could not retrieve portfolio.")

    stocks = []

    for row in rows:
        # Lookup current stock price
        try:
            stock = lookup(row["stock_symbol"], API_KEY)
            print(row["stock_symbol"])
        except ApiLimitError as e:
            logger.warning(f"API limit hit: {e.message}")
            return apology(f"{e.message}")
        except Exception:
            logger.error("unknown error during stock lookup in /home [GET]")
            continue

        # Get total shares for this stock
        try:
            total_shares_row = conn.execute(
                "SELECT shares_amount FROM user_stocks WHERE stock_symbol = ? AND user_id = ?",
                (row["stock_symbol"], session["user_id"]),
            ).fetchone()
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch shares amount: {e}")
            continue

        stock["shares"] = total_shares_row["shares_amount"]
        stock["total"] = stock["price"] * stock["shares"]
        stocks.append(stock)

    # Get cash balance
    try:
        cash_row = conn.execute(
            "SELECT cash FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
        cash_balance = cash_row["cash"]
    except sqlite3.Error as e:
        logger.error(f"Failed to fetch user cash: {e}")
        return apology("Error retrieving account info.")

    # Calculate grand total (cash + total value of stocks)
    grand_total = cash_balance + sum(stock["total"] for stock in stocks)

    return render_template(
        "portfolio/home.html",
        stocks=stocks,
        cash_balance=cash_balance,
        grand_total=grand_total,
    )


@portfolio_bp.route("/buy", methods=["GET", "POST"])
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

        try:
            stock_info = lookup(stock_symbol, API_KEY)
            if not stock_info:
                return apology("Invalid stock symbol")
        except ApiLimitError as e:
            logger.warning(f"API limit hit during buy: {e.message}")
            return apology(f"{e.message}")
        except Exception:
            logger.error("bug during stock lookup in /buy [POST]")
            return apology("Something went wrong.")

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
            user = db.execute(
                "SELECT cash FROM users WHERE id = ?", (session["user_id"],)
            ).fetchone()
            if not user:
                bugger.log("User not found during buy.")
                return apology("User not found")
            remaining_cash = float(user["cash"])
        except Exception as e:
            logger.error(f"Error accessing user cash: {e}")
            return apology("Unexpected error")

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
                (
                    session["user_id"],
                    "buy",
                    stock_info["symbol"],
                    stock_info["price"],
                    buy_amount,
                    datetime.now(),
                ),
            )

            db.execute("COMMIT")
            logger.info(
                f"User {session['user_id']} bought {buy_amount} shares of {stock_info['symbol']}."
            )
        except sqlite3.Error as e:
            db.rollback()
            logger.error(f"Transaction failed during buy: {e}")
            return apology("Transaction failed, /buy")

        # Redirect to main page
        return redirect("/")


@portfolio_bp.route("/history")
@login_required
def history():
    """Show history of transactions"""
    try:
        history_logs = (
            get_db()
            .execute(
                "SELECT * FROM history_logs WHERE user_id = ? ORDER BY time DESC",
                (session["user_id"],),
            )
            .fetchall()
        )
        logger.info(f"Transaction history retrieved for user_id={session['user_id']}.")
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve transaction history: {e}")
        return apology("Could not load history.")
    return render_template("portfolio/history.html", history=history_logs)


@portfolio_bp.route("/quote", methods=["GET", "POST"])
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

        try:
            # get stock information
            stock_information = lookup(symbol, API_KEY)
            if stock_information is None:
                return apology("Invalid stock symbol")
        except ApiLimitError as e:
            logger.warning(f"API limit during quote: {e.message}")
            return apology(f"{e.message}")
        except Exception as e:
            logger.error(f"Quote lookup error: {e}")
            return apology("Something went wrong")

        return render_template("portfolio/quoted.html", information=stock_information)


@portfolio_bp.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    db = get_db()

    if request.method == "GET":
        try:
            array_of_stocks = db.execute(
                "SELECT DISTINCT stock_symbol FROM user_stocks WHERE user_id = ?",
                (session["user_id"],),
            ).fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching stocks for sell page: {e}")
            return apology("Could not load sell page.")
        return render_template("portfolio/sell.html", stocks=array_of_stocks)
    else:
        # Validate stock symbol from frontend
        stock_symbol = request.form.get("symbol")
        if not stock_symbol:
            return apology("Require symbol")

        try:
            stock_info = lookup(stock_symbol, API_KEY)
            if not stock_info:
                return apology("Stock not found")
        except ApiLimitError as e:
            return apology(f"{e.message}")
        except Exception as e:
            logger.error(f"Sell lookup failed: {e}")
            return apology("Something went wrong")

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
            (session["user_id"], stock_symbol),
        ).fetchone()

        if result is None or sell_amount > result["shares_amount"]:
            return apology("Not enough shares to sell")

        try:
            with db:  # This automatically starts and commits a transaction
                if sell_amount == result["shares_amount"]:
                    db.execute(
                        "DELETE FROM user_stocks WHERE user_id = ? AND stock_symbol = ?",
                        (session["user_id"], stock_symbol),
                    )
                else:
                    new_shares = result["shares_amount"] - sell_amount
                    # Update stock holdings (subtract shares)
                    db.execute(
                        "UPDATE user_stocks SET shares_amount = ? WHERE user_id = ? AND stock_symbol = ?",
                        (new_shares, session["user_id"], stock_symbol),
                    )
                # Get user's current cash balance
                user_cash = db.execute(
                    "SELECT cash FROM users WHERE id = ?", (session["user_id"],)
                ).fetchone()

                updated_cash = (
                    float(user_cash["cash"]) + stock_info["price"] * sell_amount
                )

                # Update user's cash
                db.execute(
                    "UPDATE users SET cash = ? WHERE id = ?",
                    (updated_cash, session["user_id"]),
                )

                # Update transaction history
                db.execute(
                    "INSERT INTO history_logs (user_id, type, stock_symbol, stock_price, shares_amount, time) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        session["user_id"],
                        "sell",
                        stock_symbol,
                        stock_info["price"],
                        sell_amount,
                        datetime.now(),
                    ),
                )
                logger.info(
                    f"User {session['user_id']} sold {sell_amount} shares of {stock_symbol}."
                )

        except sqlite3.Error as e:
            logger.error(f"Sell transaction failed: {e}")
            return apology("Transaction failed: /sell")

        return redirect("/home")


@portfolio_bp.route("/contribute", methods=["GET"])
@login_required
def contribute():
    return render_template("portfolio/contribute.html")


@portfolio_bp.route("/apologize", methods=["GET"])
def apologize():
    return apology("This feature is being implemented!")
