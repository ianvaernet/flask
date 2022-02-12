# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.api_response import ApiResponse  # noqa: F401,E501
from swagger_server.models.edition_types import EditionTypes  # noqa: F401,E501
from swagger_server import util


class InlineResponse20010(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(
        self,
        code: int = None,
        message: str = None,
        data: EditionTypes = None,
        error: str = None,
    ):  # noqa: E501
        """InlineResponse20010 - a model defined in Swagger

        :param code: The code of this InlineResponse20010.  # noqa: E501
        :type code: int
        :param message: The message of this InlineResponse20010.  # noqa: E501
        :type message: str
        :param data: The data of this InlineResponse20010.  # noqa: E501
        :type data: EditionTypes
        :param error: The error of this InlineResponse20010.  # noqa: E501
        :type error: str
        """
        self.swagger_types = {
            "code": int,
            "message": str,
            "data": EditionTypes,
            "error": str,
        }

        self.attribute_map = {
            "code": "code",
            "message": "message",
            "data": "data",
            "error": "error",
        }
        self._code = code
        self._message = message
        self._data = data
        self._error = error

    @classmethod
    def from_dict(cls, dikt) -> "InlineResponse20010":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200_10 of this InlineResponse20010.  # noqa: E501
        :rtype: InlineResponse20010
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code(self) -> int:
        """Gets the code of this InlineResponse20010.


        :return: The code of this InlineResponse20010.
        :rtype: int
        """
        return self._code

    @code.setter
    def code(self, code: int):
        """Sets the code of this InlineResponse20010.


        :param code: The code of this InlineResponse20010.
        :type code: int
        """

        self._code = code

    @property
    def message(self) -> str:
        """Gets the message of this InlineResponse20010.


        :return: The message of this InlineResponse20010.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this InlineResponse20010.


        :param message: The message of this InlineResponse20010.
        :type message: str
        """

        self._message = message

    @property
    def data(self) -> EditionTypes:
        """Gets the data of this InlineResponse20010.


        :return: The data of this InlineResponse20010.
        :rtype: EditionTypes
        """
        return self._data

    @data.setter
    def data(self, data: EditionTypes):
        """Sets the data of this InlineResponse20010.


        :param data: The data of this InlineResponse20010.
        :type data: EditionTypes
        """

        self._data = data

    @property
    def error(self) -> str:
        """Gets the error of this InlineResponse20010.


        :return: The error of this InlineResponse20010.
        :rtype: str
        """
        return self._error

    @error.setter
    def error(self, error: str):
        """Sets the error of this InlineResponse20010.


        :param error: The error of this InlineResponse20010.
        :type error: str
        """

        self._error = error
