#!/usr/bin/env python3

import os

from swagger_server.formatter import render_problem_exception
from connexion import ProblemException
from swagger_server import create_app
from swagger_server import db
from swagger_server import app

flask_app = app.app
db = db

if __name__ == "__main__":
    app = create_app()
    app.add_error_handler(ProblemException, render_problem_exception)
    app.run(os.getenv("FLASK_PORT"), debug=True)
