import os
from datetime import timedelta
base_dir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = None
    CELERY_RESULT_BACKEND = None

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
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 600
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 3
    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = "noreply@pentaflow.com"