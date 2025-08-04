import os
from flask import Flask
from flask_session import Session
from dotenv import load_dotenv

from internal.server.model.sqlite_connection import close_db
from internal.server.routes.auth.auth_routes import auth_bp
from internal.server.routes.portfolio.portforlio_routes import portfolio_bp
from internal.server.utils.utils import usd, time_format
from internal.core.logger import logger


def create_app() -> Flask:
    """
    Create and configure the Flask app.
    """
    logger.info("---------- Flask app initialized begin ----------")

    load_env_variables()

    app = Flask(
        __name__,
        template_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../frontend/templates")
        ),
        static_folder=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../frontend/static")
        ),
    )

    configure_app(app)
    configure_session(app)
    register_filters(app)
    register_blueprints(app)
    register_teardown(app)

    logger.info("---------- Flask app initialized complete ----------")

    return app


def load_env_variables():
    """
    Load environment variables from .env file.
    """
    load_dotenv()


def configure_app(app: Flask):
    """
    Set app config values.
    """
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["API_KEY_ALPHA_VANTAGE"] = os.getenv("API_KEY_ALPHA_VANTAGE")
    app.config["API_KEY_FINNHUB"] = os.getenv("API_KEY_FINNHUB")
    app.config["API_KEY_TWELVE_DATA"] = os.getenv("API_KEY_TWELVE_DATA")


def configure_session(app: Flask):
    """
    Initialize Flask session.
    """
    Session(app)


def register_filters(app: Flask):
    """
    Register custom Jinja filters.
    """
    app.jinja_env.filters["usd"] = usd
    app.jinja_env.filters["time_format"] = time_format


def register_blueprints(app: Flask):
    """
    Register Flask blueprints.
    """
    app.register_blueprint(auth_bp)
    app.register_blueprint(portfolio_bp)


def register_teardown(app: Flask):
    """
    Register teardown function to close DB connection.
    """

    @app.teardown_appcontext
    def teardown_db(exception):
        close_db(exception)


# Entry point: create app instance
app = create_app()
