from flask import Blueprint, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from internal.server.model.sqlite_connection import get_db, close_db
from internal.server.utils.utils import apology, login_required
from internal.core.logger.logger import logger
import sqlite3

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
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
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)

        if not password:
            return apology("must provide password", 403)

        # Query database for username
        try:
            rows = (
                get_db()
                .execute("SELECT * FROM users WHERE username = ?", (username,))
                .fetchall()
            )
        except sqlite3.Error as e:
            logger.error(f"Database error during login for user '{username}': {e}")
            return apology("Unexpected error during login", 500)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        logger.info(f"User logged in: {username} (user_id={rows[0]['id']})")

        # Redirect user to home page
        return redirect("/home")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("auth/register.html")

    elif request.method == "POST":
        db = get_db()
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
        try:
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
        except sqlite3.Error as e:
            logger.error(f"Database error checking user existence: {e}")
            return apology("Unexpected error during registration", 500)

        if user is not None:
            return apology("Username existed")

        password_hash = generate_password_hash(password)

        try:
            # Save user data into database
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (username, password_hash),
            )
            db.commit()
            logger.info(f"User registered successfully: {username}")
            return redirect("/login")
        except sqlite3.IntegrityError as e:
            # This occur because UNIQUE constraint has been violated
            return apology("Username existed")
        except sqlite3.Error as e:
            logger.error(
                {
                    "error": "Registration DB failure",
                    "username": username,
                    "details": str(e),
                }
            )
            return apology("Unexpected error in /register")

    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    """Log user out"""

    user_id = session.get("user_id")
    if user_id:
        logger.info(f"User logged out: user_id={user_id}")

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")
