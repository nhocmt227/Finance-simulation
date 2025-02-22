from flask import Blueprint, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from db.connection import get_db, close_db
from helpers.utils import apology, login_required
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
    
    
@auth_bp.route("/register", methods=["GET", "POST"])
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
    

@auth_bp.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/home")
    

