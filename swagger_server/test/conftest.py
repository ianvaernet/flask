import pytest
import os
import requests

from swagger_server.__main__ import create_app

os.environ["TEST"] = "True"
os.environ["JWT_SECRET"] = "4ksh5kshe5fwes4"
os.environ["POLLING_INTERVAL"] = "0.5"

from swagger_server.services import auth
from swagger_server.models import Auth


app = create_app()
_auth_credentials = Auth(username="test_user", password="test_password")
_auth_token, _api_token = auth.login(_auth_credentials)
_auth_header = {
    "Authorization": "Bearer {}".format(_auth_token),
    "ApiToken": _api_token,
}


@pytest.fixture(scope="package")
def client():
    with app.app.test_client() as c:
        yield c


@pytest.fixture(scope="package")
def auth_header():
    return _auth_header
