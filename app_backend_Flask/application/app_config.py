import os
from datetime import timedelta
base_dir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevConfig(Config):
    DEBUG = False
    SQLITE_DB_DIR = os.path.join(base_dir, "../database")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "HMS_DB.sqlite3")
    JWT_SECRET_KEY = "8#FgtG^78#ytf2K49045jK5" 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["headers", "json", "cookies"]
    JWT_HEADER_TYPE = "Bearer"
    PROPAGATE_EXCEPTIONS = True