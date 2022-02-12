import connexion
import os
import requests
from flask import Flask
from swagger_ui_bundle import swagger_ui_3_path
from os.path import join, dirname
from swagger_server.database import db as db_session
from dotenv import load_dotenv
from swagger_server import encoder
from logging.config import dictConfig
from swagger_server.extensions import Logger, scheduler
import alembic.config
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = db_session

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
dictConfig(Logger.configure_logger())

test_flag = os.getenv("TEST", "False").lower() in ("true", "1", "t")
if test_flag:
    from swagger_server.database.models import *

app = connexion.App(__name__, specification_dir="./swagger/")


def create_app():
    _app = app
    _app.app.json_encoder = encoder.JSONEncoder
    _app.add_api(
        "swagger.yaml",
        arguments={"title": "CMS NFT Minting"},
        options={"swagger_path": swagger_ui_3_path},
    )
    configure_app(_app.app)
    init_app(_app.app)
    return _app


def configure_app(flask_app):
    flask_app.config.from_object(
        f"swagger_server.config.{os.getenv('APPLICATION_ENV', 'Development')}"
    )

    @flask_app.before_first_request
    def create_database():
        test_flag = os.getenv("TEST", "False").lower() in ("true", "1", "t")
        if not test_flag:
            alembic.config.main(argv=["--raiseerr", "upgrade", "head"])

    @flask_app.before_first_request
    def create_scheduler():
        if os.getenv("SCHEDULER") == "True":
            flask_app.config["SCHEDULER_JOBSTORES"] = {
                "default": SQLAlchemyJobStore(engine=db.engine)
            }
            scheduler.init_app(flask_app)
            scheduler.start()
        else:
            scheduler_host = os.getenv("SCHEDULER_HOST")
            requests.Session().get(f"{scheduler_host}/scheduler/jobs")


def init_app(flask_app: Flask):
    db.init_app(flask_app)
