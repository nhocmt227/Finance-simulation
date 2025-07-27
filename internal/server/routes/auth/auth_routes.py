from flask import Blueprint, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from internal.server.model.sqlite_connection import get_db
from internal.server.utils.utils import apology
from internal.core.logger import logger
import sqlite3

# ----------------------
# Logging Message Constants
# ----------------------

LOG_LOGIN_GET = "/login [GET]: Rendering login page"
LOG_LOGIN_POST_START = "/login [POST]: Attempting login for user '%s'"
LOG_LOGIN_DB_ERROR = "/login [POST]: Database error during login for user '%s': %s"
LOG_LOGIN_INVALID = "/login [POST]: Invalid username and/or password for user '%s'"
LOG_LOGIN_SUCCESS = "/login [POST]: Login successful for user '%s' (user_id=%s)"
LOG_LOGIN_UNKNOWN_METHOD = "Unsupported method used on /login: '%s'"

LOG_REGISTER_GET = "/register [GET]: Rendering registration page"
LOG_REGISTER_POST_START = "/register [POST]: Attempting registration for user '%s'"
LOG_REGISTER_DB_CONN_ERROR = "/register [POST]: Database connection error"
LOG_REGISTER_VALIDATION_FAILED = "/register [POST]: Validation failed: %s"
LOG_REGISTER_USER_EXISTS = "/register [POST]: Username already exists: '%s'"
LOG_REGISTER_DB_QUERY_ERROR = (
    "/register [POST]: DB error checking user existence for '%s': %s"
)
LOG_REGISTER_SUCCESS = "/register [POST]: Registration successful for user '%s'"
LOG_REGISTER_DB_INSERT_ERROR = "/register [POST]: DB insertion failed for '%s': %s"
LOG_REGISTER_UNKNOWN_METHOD = "Unsupported method used on /register: '%s'"

LOG_LOGOUT = "/logout: User logged out (user_id=%s)"

LOG_UNKNOWN_ROUTE = "Unknown route accessed: %s"

# ----------------------
# Environment
# ----------------------

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    session.clear()

    if request.method == "GET":
        logger.debug(LOG_LOGIN_GET)
        return render_template("auth/login.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        logger.debug(LOG_LOGIN_POST_START, username)

        if not username:
            return apology("must provide username", 403)
        if not password:
            return apology("must provide password", 403)

        try:
            user_rows = (
                get_db()
                .execute("SELECT * FROM users WHERE username = ?", (username,))
                .fetchall()
            )
        except sqlite3.Error as e:
            logger.error(LOG_LOGIN_DB_ERROR, username, e)
            return apology("Unexpected error during login", 500)

        if len(user_rows) != 1 or not check_password_hash(
            user_rows[0]["hash"], password
        ):
            logger.warning(LOG_LOGIN_INVALID, username)
            return apology("invalid username and/or password", 403)

        user_record = user_rows[0]
        session["user_id"] = user_record["id"]

        logger.info(LOG_LOGIN_SUCCESS, username, user_record["id"])
        return redirect("/home")
    else:
        logger.warning(LOG_LOGIN_UNKNOWN_METHOD, request.method)
        return apology("Method not allowed", 405)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        logger.debug(LOG_REGISTER_GET)
        return render_template("auth/register.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password-confirmation")

        logger.debug(LOG_REGISTER_POST_START, username)

        try:
            db = get_db()
        except sqlite3.Error:
            logger.error(LOG_REGISTER_DB_CONN_ERROR)
            return apology("Database connection error", 500)

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

        try:
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
        except sqlite3.Error as e:
            logger.error(LOG_REGISTER_DB_QUERY_ERROR, username, e)
            return apology("Unexpected error during registration", 500)

        if user is not None:
            logger.debug(LOG_REGISTER_USER_EXISTS, username)
            return apology("Username existed")

        password_hash = generate_password_hash(password)

        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (username, password_hash),
            )
            db.commit()
            logger.info(LOG_REGISTER_SUCCESS, username)
            return redirect("/login")
        except sqlite3.IntegrityError:
            logger.debug(LOG_REGISTER_USER_EXISTS, username)
            return apology("Username existed")
        except sqlite3.Error as e:
            logger.error(LOG_REGISTER_DB_INSERT_ERROR, username, e)
            return apology("Unexpected error in /register")

    else:
        logger.warning(LOG_REGISTER_UNKNOWN_METHOD.format(request.method))
        return apology("Method not allowed", 405)


@auth_bp.route("/logout")
def logout():
    """Log user out"""
    user_id = session.get("user_id")
    if user_id:
        logger.info(LOG_LOGOUT, user_id)
    session.clear()
    return redirect("/home")
