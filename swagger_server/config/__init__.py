import os
from pytz import utc


class Config(object):
    PORT = os.getenv("FLASK_PORT")
    HOST = os.getenv("FLASK_HOST")
    DEBUG = os.getenv("FLASK_DEBUG")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    JSON_SORT_KEYS = False
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = utc


class Development(Config):
    _db = os.getenv("DB")
    _db_user = os.getenv("DB_USER")
    _db_password = os.getenv("DB_PASSWORD")
    _db_host = os.getenv("DB_HOST")
    _db_schema = os.getenv("DB_SCHEMA")
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}/{}".format(
        _db, _db_user, _db_password, _db_host, _db_schema
    )
    SQLALCHEMY_ECHO = os.getenv("SHOW_SQL_QUERIES") == "True"
    FLASK_ENV = os.getenv("FLASK_ENV")


class Testing(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test.db"
    FLASK_ENV = "development"


class Production(Config):
    PORT = os.getenv("PORT")
    HOST = os.getenv("HOST")
    DEBUG = False
    TESTING = False
    FLASK_DEBUG = False
    FLASK_ENV = "production"

    _db = os.getenv("DB")
    _db_user = os.getenv("DB_USER")
    _db_password = os.getenv("DB_PASSWORD")
    _db_host = os.getenv("DB_HOST")
    _db_schema = os.getenv("DB_SCHEMA")
    SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}/{}".format(
        _db, _db_user, _db_password, _db_host, _db_schema
    )
