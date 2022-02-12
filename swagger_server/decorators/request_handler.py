from typing import List
from swagger_server.models import ApiResponse
from collections.abc import Callable
from connexion.exceptions import ConnexionException
from swagger_server.exceptions import DapperException, ActiveSerieException
from http import HTTPStatus


def request_handler(params=[]) -> Callable:
    """Convert the tuple returned by the controller function into an Api
    Response and return it as connexion expects

    :param params: List

    :return: Callable
    """

    def decorator(func: Callable) -> Callable:
        def func_wrapper(*args, **kwargs) -> Callable:
            response_dict: dict
            new_kwargs: dict = {}
            for param in params:
                if param in kwargs.keys():
                    new_kwargs[param] = kwargs[param]
            try:
                res, code, message, error = func(*args, **new_kwargs)
                data: list | dict
                if type(res) == list or type(res) == dict or not res:
                    data = res
                else:
                    data = res.to_dict()
                response_dict = {
                    "code": code,
                    "error": error,
                    "data": data,
                    "message": message,
                }
            except ConnexionException as e:
                response_dict = {
                    "code": e.status,
                    "error": e.title,
                    "data": "",
                    "message": e.detail,
                }
            except DapperException as e:
                response_dict = {
                    "code": HTTPStatus.BAD_REQUEST,
                    "error": "Dapper Exception",
                    "data": "",
                    "message": e,
                }
            except ActiveSerieException as e:
                response_dict = {
                    "code": HTTPStatus.BAD_REQUEST,
                    "error": "Active Series Exception",
                    "data": "",
                    "message": e,
                }
            except Exception as e:
                response_dict = {
                    "code": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "error": "GENERAL ERROR",
                    "data": "",
                    "message": e,
                }
            response: ApiResponse = ApiResponse.from_dict(response_dict)
            return response, response.code

        return func_wrapper

    return decorator
