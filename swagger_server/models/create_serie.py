# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.base_serie import BaseSerie  # noqa: F401,E501
from swagger_server import util


class CreateSerie(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(
        self,
        name: str = None,
        description: str = None,
        short_word: str = None,
        publish_time: datetime = None,
    ):  # noqa: E501
        """CreateSerie - a model defined in Swagger

        :param name: The name of this CreateSerie.  # noqa: E501
        :type name: str
        :param description: The description of this CreateSerie.  # noqa: E501
        :type description: str
        :param short_word: The short_word of this CreateSerie.  # noqa: E501
        :type short_word: str
        :param publish_time: The publish_time of this CreateSerie.  # noqa: E501
        :type publish_time: datetime
        """
        self.swagger_types = {
            "name": str,
            "description": str,
            "short_word": str,
            "publish_time": datetime,
        }

        self.attribute_map = {
            "name": "name",
            "description": "description",
            "short_word": "short_word",
            "publish_time": "publish_time",
        }
        self._name = name
        self._description = description
        self._short_word = short_word
        self._publish_time = publish_time

    @classmethod
    def from_dict(cls, dikt) -> "CreateSerie":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CreateSerie of this CreateSerie.  # noqa: E501
        :rtype: CreateSerie
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self) -> str:
        """Gets the name of this CreateSerie.


        :return: The name of this CreateSerie.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this CreateSerie.


        :param name: The name of this CreateSerie.
        :type name: str
        """
        if name is None:
            raise ValueError(
                "Invalid value for `name`, must not be `None`"
            )  # noqa: E501

        self._name = name

    @property
    def description(self) -> str:
        """Gets the description of this CreateSerie.


        :return: The description of this CreateSerie.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this CreateSerie.


        :param description: The description of this CreateSerie.
        :type description: str
        """

        self._description = description

    @property
    def short_word(self) -> str:
        """Gets the short_word of this CreateSerie.


        :return: The short_word of this CreateSerie.
        :rtype: str
        """
        return self._short_word

    @short_word.setter
    def short_word(self, short_word: str):
        """Sets the short_word of this CreateSerie.


        :param short_word: The short_word of this CreateSerie.
        :type short_word: str
        """
        if short_word is None:
            raise ValueError(
                "Invalid value for `short_word`, must not be `None`"
            )  # noqa: E501

        self._short_word = short_word

    @property
    def publish_time(self) -> datetime:
        """Gets the publish_time of this CreateSerie.


        :return: The publish_time of this CreateSerie.
        :rtype: datetime
        """
        return self._publish_time

    @publish_time.setter
    def publish_time(self, publish_time: datetime):
        """Sets the publish_time of this CreateSerie.


        :param publish_time: The publish_time of this CreateSerie.
        :type publish_time: datetime
        """

        self._publish_time = publish_time
