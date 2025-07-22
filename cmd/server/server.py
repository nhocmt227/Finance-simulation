from flask import Flask
from flask_session import Session
from dotenv import load_dotenv
import os
from internal.server.model.sqlite_connection import close_db
from internal.server.routes.auth.auth_routes import auth_bp
from internal.server.routes.portfolio.portforlio_routes import portfolio_bp
from internal.server.utils.utils import usd, time_format

# take environment variables from .env.
load_dotenv()  
# Retrieve the API key
API_KEY = os.getenv("API_KEY")

# Configure application
app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/templates')),
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/static'))
)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Register filters with Jinja
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["time_format"] = time_format

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(portfolio_bp)

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)