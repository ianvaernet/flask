from http import HTTPStatus
from typing import Tuple

import connexion
from swagger_server.services import auth
from swagger_server.models import Auth, AuthResponse
from swagger_server.decorators import request_handler, logger

"""
controller generated to handled auth operation described at:
https://connexion.readthedocs.io/en/latest/security.html
"""


def check_Bearer(token: str) -> dict:
    """Check the token passed in the Authorization header

    :param token: str
    """
    api_token = connexion.request.headers["ApiToken"]
    auth.validate_token(api_token, token)

    return {"token": token}


def check_ApiToken(api_token: str) -> dict:
    """Check the token passed in the ApiToken header

    :param api_token: str
    """
    token = connexion.request.headers["Authorization"]
    auth.validate_token(api_token, token)

    return {"api_token": api_token}


@request_handler(["body"])
@logger(log_input=False)
def authenticate(body: dict) -> Tuple[object, int, str, str]:
    """Authenticate a user with the genies cms system

    :param body: dict

    :return tuple[ApiResponse, int]
    """
    if connexion.request.is_json:
        auth_credentials: Auth = Auth.from_dict(body)
        token, api_token = auth.login(auth_credentials)

        auth_response: AuthResponse = AuthResponse.from_dict(
            {
                "username": auth_credentials.username,
                "token": token,
                "api_token": api_token,
            }
        )

        message: str = "Authentication Success"

    return auth_response, HTTPStatus.OK, message, None
