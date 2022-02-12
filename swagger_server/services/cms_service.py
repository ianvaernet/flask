import os
import requests
from requests import Response, Session
from swagger_server.exceptions import NotFoundException
from swagger_server.models.enums.edition_image import EditionImage
from swagger_server.models.enums.edition_video import EditionVideo
from swagger_server.util import get_jwt_token, get_api_token


class CmsService:
    """Client to consume the cms resources

    Attributes:
        __cms_host (str)
        __cms_login_url (str)
        __cms_validate_token_url (str)
        __http (Session)
    """

    __cms_host: str
    __cms_login_url: str
    __http: Session

    def __init__(self):
        self.__cms_host = os.getenv("CMS_HOST")
        self.__cms_login_url = os.getenv("CMS_LOGIN_URL")
        self.__http = requests.Session()
        self.__http.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def get(self, url: str, headers: dict) -> Response:
        """perform a get request to the cms backend

        :param url: str
        :param headers: dict

        :return: dict
        """
        response: Response = self.__http.get(
            "{host}/{url}".format(host=self.__cms_host, url=url), headers=headers
        )
        return response

    def post(self, url: str, json: dict, headers={}) -> Response:
        """Perfeom a post request to the cms backend

        :param url: str
        :param json: dict
        :param headers: dict

        :return: dict
        """
        response: Response = self.__http.post(
            "{host}/{url}".format(host=self.__cms_host, url=url),
            json=json,
            headers=headers,
            allow_redirects=False,
        )
        return response

    def login(self, username: str, password: str) -> str:
        """Login a user in the cms subsystem

        :param username: str
        :param password: str

        :return: str
        """

        json: dict = {"username": username, "password": password}

        response: Response = self.post(
            self.__cms_login_url,
            json=json,
        )

        response_json = response.json()

        token: str = response_json["data"]["tokens"]["AccessToken"]
        api_token: str = response_json["data"]["tokens"]["ApiToken"]
        return token, api_token

    def get_wearable_data(self, id: int) -> dict:
        """Get SKU, collection_id, images and videos of the wearable with the specified id from the CMS

        :param id: int

        :return: dict
        """
        headers = {
            "Authorization": get_jwt_token(),
            "ApiToken": get_api_token(),
        }
        response = self.get("api/v1/assets/{id}".format(id=id), headers)
        response_json = response.json()
        if response_json["status"] != 200:
            raise NotFoundException(
                detail="There is no Avatar Wearable with the ID={id}".format(id=id)
            )
        asset = response_json["data"]["asset"]
        avatar_wearable_sku: str = asset["uuid"]
        return {
            "sku": avatar_wearable_sku,
            "collection_id": asset["collection_id"],
            "file_list": asset["file_list"],
        }
