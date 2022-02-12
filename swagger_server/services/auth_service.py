import os

import jwt
from requests import Response
from connexion.exceptions import AuthenticationProblem
from swagger_server.services.cms_service import CmsService
from swagger_server.models import Auth


class AuthService:
    """The authentication service that will validate all the request tokens
    with the genies cms instance

    Attributes:
        _cms_validate_token_url (str)
        _cms (CmsService)
    """

    __cms: CmsService
    __jwt_secret: str
    __jwt_algorithm: str

    def __init__(self, cms_service):
        self.__cms = cms_service
        self.__jwt_secret = os.getenv("JWT_SECRET")
        self.__jwt_algorithm = os.getenv("JWT_ALGORITHM")

    def __raise_authentication_problem(self, message: str):
        """raise an AuthenticationProblem exception

        :param message: str
        """
        raise AuthenticationProblem(401, "Authorization Problem", message)

    def validate_token(self, api_token: str, token: str) -> bool:
        """Validate the token passed as the Authorization header and api_token passed as ApiToken header with the
        genies cms backend

        :param api_token: str
        :param token: str

        :return bool
        """
        claims: dict = self.decode_token(api_token)
        if not claims or "role" not in claims or claims["role"] is None:
            self.__raise_authentication_problem(
                "Invalid JWT Token, it may be missing key claims"
            )

        headers: dict = {
            "Authorization": "Bearer {}".format(token),
            "ApiToken": api_token,
        }

        id: int = claims["user_id"]

        body: dict = {
            "email": claims["email"],
            "role": claims["role"],
        }

        response: Response = self.__cms.post(
            "api/v1/users/{id}/check".format(id=id), body, headers
        )

        if response.status_code == 200:
            return True
        self.__raise_authentication_problem("CMS Authentication problem")

    def decode_token(self, token: str) -> dict:
        """Decode the token to validate that the tokenis well formed and then
        use it to validate the token with the cms backend

        :param token: str

        :return dict
        """
        try:
            return jwt.decode(
                token, key=self.__jwt_secret, algorithms=[self.__jwt_algorithm]
            )
        except Exception as e:
            raise AuthenticationProblem(
                401,
                "Authorization Problem NFT Subsystem cannot decode the token",
                str(e),
            )

    def login(self, credentials: Auth) -> dict:
        """ " Login a user in to the cms system

        :param username: str
        :param password: str

        :return str, The token
        """

        username: str = credentials.username
        password: str = credentials.password
        return self.__cms.login(username, password)
