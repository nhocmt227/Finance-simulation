import os
from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime
from dotenv import load_dotenv

from internal.server.model.sqlite_connection import get_db
from internal.server.utils.utils import apology, login_required
from internal.server.api.API_handlers import lookup
from internal.server.utils.exception import ApiLimitError
from internal.core.logger import logger
from internal.core.bugger.bugger import bugger
import sqlite3

# ----------------------
# Logging Message Constants
# ----------------------

LOG_CTX = "/portfolio"

LOG_HOME_GET = f"{LOG_CTX}/home [GET]: Rendering portfolio"
LOG_HOME_DB_ERROR = (
    f"{LOG_CTX}/home: DB error while fetching stocks for user {{}}: {{}}"
)
LOG_HOME_API_LIMIT = f"{LOG_CTX}/home: API limit reached - {{}}"
LOG_HOME_LOOKUP_ERROR = (
    f"{LOG_CTX}/home: Unexpected error during lookup for symbol '{{}}': {{}}"
)
LOG_HOME_CASH_ERROR = f"{LOG_CTX}/home: Error fetching cash for user {{}}: {{}}"
LOG_HOME_RENDERED = f"{LOG_CTX}/home: Rendered for user_id={{}}"

LOG_INDEX_GET_AUTH = f"{LOG_CTX}/ [GET]: Redirecting authenticated user to /home"
LOG_INDEX_GET_PUBLIC = f"{LOG_CTX}/ [GET]: Rendering public index page"

LOG_BUY_GET = f"{LOG_CTX}/buy [GET]: Rendering buy form for user_id={{}}"
LOG_BUY_POST = f"{LOG_CTX}/buy [POST]: User {{}} buying stock '{{}}' amount {{}}"
LOG_BUY_LOOKUP_FAIL = f"{LOG_CTX}/buy: Lookup error for symbol '{{}}': {{}}"
LOG_BUY_TRANSACTION_FAIL = f"{LOG_CTX}/buy: Transaction failed for user {{}}: {{}}"
LOG_BUY_SUCCESS = f"{LOG_CTX}/buy [POST]: User {{}} bought {{}} shares of {{}}"
LOG_BUY_UNKNOWN_METHOD = "Unsupported method used on /buy: '{}'"

LOG_SELL_GET = f"{LOG_CTX}/sell [GET]: Rendering sell page for user_id={{}}"
LOG_SELL_LOOKUP_FAIL = f"{LOG_CTX}/sell: Lookup error for '{{}}': {{}}"
LOG_SELL_TRANSACTION_FAIL = f"{LOG_CTX}/sell: Transaction failed for user {{}}: {{}}"
LOG_SELL_SUCCESS = f"{LOG_CTX}/sell [POST]: User {{}} sold {{}} shares of {{}}"
LOG_SELL_UNKNOWN_METHOD = "Unsupported method used on /sell: '{}'"

LOG_HISTORY_GET = (
    f"{LOG_CTX}/history [GET]: Retrieving transaction history for user {{}}"
)
LOG_HISTORY_FAIL = f"{LOG_CTX}/history: Failed to retrieve history for user {{}}: {{}}"

LOG_QUOTE_GET = f"{LOG_CTX}/quote [GET]: Rendering quote form"
LOG_QUOTE_LOOKUP_FAIL = f"{LOG_CTX}/quote: Lookup error for '{{}}': {{}}"
LOG_QUOTE_API_LIMIT = f"{LOG_CTX}/quote: API limit reached for '{{}}' - {{}}"
LOG_QUOTE_SUCCESS = f"{LOG_CTX}/quote [POST]: Successfully looked up symbol '{{}}'"
LOG_QUOTE_UNKNOWN_METHOD = "Unsupported method used on /quote: '{}'"

LOG_CONTRIBUTE_GET = f"{LOG_CTX}/contribute [GET]: Rendering contribute page"
LOG_APOLOGIZE_GET = f"{LOG_CTX}/apologize [GET]: Rendering apology message"

# ----------------------
# Environment
# ----------------------

load_dotenv()
API_KEY = os.getenv("API_KEY")
portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/", methods=["GET"])
def main():
    """Render the public index page for unauthenticated users."""
    if "user_id" in session:
        logger.debug(LOG_INDEX_GET_AUTH)
        return redirect("/home")

    logger.debug(LOG_INDEX_GET_PUBLIC)
    return render_template("public/index.html")


@portfolio_bp.route("/home", methods=["GET"])
@login_required
def index():
    conn = get_db()
    user_id = session["user_id"]
    logger.debug(LOG_HOME_GET)

    # Get list of distinct stocks purchased
    try:
        rows = conn.execute(
            "SELECT DISTINCT stock_symbol FROM user_stocks WHERE user_id = ?",
            (user_id,),
        ).fetchall()
    except sqlite3.Error as e:
        logger.error(LOG_HOME_DB_ERROR, user_id, e)
        return apology("Could not retrieve portfolio.")

    stocks = []

    for row in rows:
        # Lookup current stock price
        symbol = row["stock_symbol"]
        try:
            stock = lookup(symbol, API_KEY)
        except ApiLimitError as e:
            logger.warning(LOG_HOME_API_LIMIT, e.message)
            return apology(e.message)
        except Exception as e:
            logger.error(LOG_HOME_LOOKUP_ERROR, symbol, e)
            continue

        # Get total shares for this stock
        try:
            total_shares_row = conn.execute(
                "SELECT shares_amount FROM user_stocks WHERE stock_symbol = ? AND user_id = ?",
                (row["stock_symbol"], session["user_id"]),
            ).fetchone()
        except sqlite3.Error as e:
            logger.error(LOG_HOME_DB_ERROR, user_id, e)
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
        logger.error(LOG_HOME_CASH_ERROR, user_id, e)
        return apology("Error retrieving account info.")

    # Calculate grand total (cash + total value of stocks)
    grand_total = cash_balance + sum(stock["total"] for stock in stocks)
    logger.debug(LOG_HOME_RENDERED.format(user_id))

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
    user_id = session["user_id"]

    if request.method == "GET":
        logger.debug(LOG_BUY_GET, user_id)
        return render_template("portfolio/buy.html")

    elif request.method == "POST":
        # Get stock info from form
        stock_symbol = request.form.get("symbol")
        if not stock_symbol:
            return apology("No stock found")

        try:
            stock_info = lookup(stock_symbol, API_KEY)
            if not stock_info:
                return apology("Invalid stock symbol")
        except ApiLimitError as e:
            logger.warning(LOG_HOME_API_LIMIT, e.message)
            return apology(e.message)
        except Exception as e:
            logger.error(LOG_BUY_LOOKUP_FAIL, stock_symbol, e)
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
                "SELECT cash FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if not user:
                bugger.log({"event": "buy_user_not_found", "user_id": user_id})
                return apology("User not found")
            remaining_cash = float(user["cash"])
        except Exception as e:
            logger.error(LOG_HOME_CASH_ERROR, user_id, e)
            return apology("Unexpected error")

        # Calculate total cost of purchase
        total_cost = float(stock_info["price"]) * buy_amount
        if remaining_cash < total_cost:
            return apology("Insufficient cash in your account")
        try:
            db.execute("BEGIN TRANSACTION")

            # Deduct cash from user's account
            db.execute(
                "UPDATE users SET cash = ? WHERE id = ?",
                (remaining_cash - total_cost, user_id),
            )

            # Insert stock status into portfolio (if exists, update instead)
            existing_stock = db.execute(
                "SELECT shares_amount FROM user_stocks WHERE user_id = ? AND stock_symbol = ?",
                (user_id, stock_info["symbol"]),
            ).fetchone()

            if existing_stock:
                new_shares_amount = existing_stock["shares_amount"] + buy_amount
                db.execute(
                    "UPDATE user_stocks SET shares_amount = ? WHERE user_id = ? AND stock_symbol = ?",
                    (new_shares_amount, user_id, stock_info["symbol"]),
                )
            else:
                db.execute(
                    "INSERT INTO user_stocks (user_id, stock_symbol, shares_amount) VALUES (?, ?, ?)",
                    (user_id, stock_info["symbol"], buy_amount),
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
            logger.info(LOG_BUY_SUCCESS, user_id, buy_amount, stock_info["symbol"])
        except sqlite3.Error as e:
            db.rollback()
            logger.error(LOG_BUY_TRANSACTION_FAIL, user_id, e)
            return apology("Transaction failed, /buy")

        # Redirect to main page
        return redirect("/")

    else:
        logger.warning(LOG_BUY_UNKNOWN_METHOD, request.method)
        return apology("Method not allowed", 405)


@portfolio_bp.route("/history")
@login_required
def history():
    user_id = session["user_id"]
    logger.debug(LOG_HISTORY_GET, user_id)
    try:
        history_logs = (
            get_db()
            .execute(
                "SELECT * FROM history_logs WHERE user_id = ? ORDER BY time DESC",
                (user_id,),
            )
            .fetchall()
        )
    except sqlite3.Error as e:
        logger.error(LOG_HISTORY_FAIL, user_id, e)
        return apology("Could not load history.")
    return render_template("portfolio/history.html", history=history_logs)


@portfolio_bp.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        logger.debug(LOG_QUOTE_GET)
        return render_template("portfolio/quote.html")

    elif request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("No symbol found")

        try:
            stock_info = lookup(symbol, API_KEY)
            if stock_info is None:
                return apology("Invalid stock symbol")
            logger.info(LOG_QUOTE_SUCCESS, symbol)
        except ApiLimitError as e:
            logger.warning(LOG_QUOTE_API_LIMIT, symbol, e.message)
            return apology(e.message)
        except Exception as e:
            logger.error(LOG_QUOTE_LOOKUP_FAIL, symbol, e)
            return apology("Something went wrong")

        return render_template("portfolio/quoted.html", information=stock_info)

    else:
        logger.warning(LOG_QUOTE_UNKNOWN_METHOD, request.method)
        return apology("Method not allowed", 405)


@portfolio_bp.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    db = get_db()
    user_id = session["user_id"]

    if request.method == "GET":
        logger.debug(LOG_SELL_GET, user_id)
        try:
            stocks = db.execute(
                "SELECT DISTINCT stock_symbol FROM user_stocks WHERE user_id = ?",
                (user_id,),
            ).fetchall()
        except sqlite3.Error as e:
            logger.error(LOG_SELL_LOOKUP_FAIL, "list", e)
            return apology("Could not load sell page.")
        return render_template("portfolio/sell.html", stocks=stocks)

    elif request.method == "POST":
        stock_symbol = request.form.get("symbol")
        sell_amount = request.form.get("shares")

        if not stock_symbol or not sell_amount:
            return apology("Require symbol and shares")

        try:
            stock_info = lookup(stock_symbol, API_KEY)
            if not stock_info:
                return apology("Stock not found")
        except ApiLimitError as e:
            return apology(e.message)
        except Exception as e:
            logger.error(LOG_SELL_LOOKUP_FAIL, stock_symbol, e)
            return apology("Something went wrong")

        try:
            sell_amount = int(sell_amount)
            if sell_amount <= 0:
                return apology("Invalid number of shares")
        except ValueError:
            return apology("Invalid shares")

        result = db.execute(
            "SELECT shares_amount FROM user_stocks WHERE user_id = ? AND stock_symbol = ?",
            (user_id, stock_symbol),
        ).fetchone()

        if result is None or sell_amount > result["shares_amount"]:
            return apology("Not enough shares to sell")

        try:
            with db:
                if sell_amount == result["shares_amount"]:
                    db.execute(
                        "DELETE FROM user_stocks WHERE user_id = ? AND stock_symbol = ?",
                        (user_id, stock_symbol),
                    )
                else:
                    new_shares = result["shares_amount"] - sell_amount
                    db.execute(
                        "UPDATE user_stocks SET shares_amount = ? WHERE user_id = ? AND stock_symbol = ?",
                        (new_shares, user_id, stock_symbol),
                    )

                user_cash = db.execute(
                    "SELECT cash FROM users WHERE id = ?", (user_id,)
                ).fetchone()
                updated_cash = (
                    float(user_cash["cash"]) + stock_info["price"] * sell_amount
                )

                db.execute(
                    "UPDATE users SET cash = ? WHERE id = ?", (updated_cash, user_id)
                )

                db.execute(
                    "INSERT INTO history_logs (user_id, type, stock_symbol, stock_price, shares_amount, time) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        user_id,
                        "sell",
                        stock_symbol,
                        stock_info["price"],
                        sell_amount,
                        datetime.now(),
                    ),
                )

                logger.info(LOG_SELL_SUCCESS, user_id, sell_amount, stock_symbol)
        except sqlite3.Error as e:
            logger.error(LOG_SELL_TRANSACTION_FAIL, user_id, e)
            return apology("Transaction failed")

        return redirect("/home")

    else:
        logger.warning(LOG_SELL_UNKNOWN_METHOD, request.method)
        return apology("Method not allowed", 405)


@portfolio_bp.route("/contribute", methods=["GET"])
@login_required
def contribute():
    logger.debug(LOG_CONTRIBUTE_GET)
    return render_template("portfolio/contribute.html")


@portfolio_bp.route("/apologize", methods=["GET"])
def apologize():
    logger.debug(LOG_APOLOGIZE_GET)
    return apology("This feature is being implemented!")
