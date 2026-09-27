"""App configuration. Override any value with an environment variable or a .env file."""
import os

from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

    # SQLite by default. To use MySQL / PostgreSQL / SQL Server just set DATABASE_URL, e.g.
    #   mysql+pymysql://user:pass@localhost/ceylon_micro_credit
    #   mssql+pyodbc://user:pass@SERVER/ceylon_micro_credit?driver=ODBC+Driver+17+for+SQL+Server
    #   postgresql://user:pass@host/dbname   (Render gives this automatically)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "ceylon_micro_credit.db")
    )
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):  # old-style URL some hosts still give
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}   # reconnect if the DB dropped the connection
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Online (HTTPS) only send the login cookie over a secure connection
    SESSION_COOKIE_SECURE = bool(os.environ.get("RENDER"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # max image upload size (5 MB)
    TEMPLATES_AUTO_RELOAD = True          # HTML template edits show without restarting

    # First admin account (created only when no admin exists yet)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe@123")

    PORT = int(os.environ.get("PORT", 5090))
