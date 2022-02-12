import os
from typing import Tuple
import jwt

from connexion.exceptions import AuthenticationProblem
from swagger_server.models import Auth
from swagger_server.decorators.logger import logger

JWT_ALGORITHM = "HS256"


class AuthServiceMock:
    """The authentication mock service that will validate all the request tokens
    for testing purposes

    Attributes:
        _cms_validate_token_url (str)
        _cms (CmsService)
    """

    _cms_validate_token_url: str
    _jwt_secret: str

    def __init__(self, cms_service):
        self._cms = cms_service
        self._jwt_secret = os.getenv("JWT_SECRET")
        self._cms_validate_token_url = os.getenv("CMS_VALIDATE_TOKEN")

    def _raise_authentication_problem(self, message: str):
        raise AuthenticationProblem(401, "Authorization Problem", message)

    def validate_token(self, api_token: str, token: str) -> bool:
        """Validate the token passed as the Authorization header and api_token passed as ApiToken header

        :param api_token: str
        :param token: str

        :return bool
        """
        claims: dict = self.decode_token(api_token)
        if not claims or "role" not in claims or claims["role"] is None:
            self.__raise_authentication_problem(
                "Invalid JWT Token, it may be missing key claims"
            )
        return True

    def decode_token(self, token: str) -> dict:
        """Decode the token to validate that the tokenis well formed and then
        use it to validate the token with the cms backend

        :param token: str

        :return dict
        """
        try:
            return jwt.decode(
                token, key=os.getenv("JWT_SECRET"), algorithms=[JWT_ALGORITHM]
            )
        except Exception as e:
            raise AuthenticationProblem(401, "Authorization Problem", str(e))

    @logger(log_input=False)
    def login(self, credentials: Auth) -> Tuple[str, str]:
        """ " Login a user in to the cms system

        :param username: str
        :param password: str

        :return Tuple[str, str]
        """

        username: str = credentials.username
        token = jwt.encode(
            {"username": username}, key=os.getenv("JWT_SECRET"), algorithm=JWT_ALGORITHM
        )
        api_token: str = jwt.encode(
            {
                "user_id": 1234,
                "organization_id": 10,
                "email": username,
                "role": "Admin",
            },
            key=os.getenv("JWT_SECRET"),
            algorithm=JWT_ALGORITHM,
        )
        return token, api_token
