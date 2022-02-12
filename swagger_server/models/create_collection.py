# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.base_collection import BaseCollection  # noqa: F401,E501
from swagger_server.models.collection_off_chain_metadata import (
    CollectionOffChainMetadata,
)  # noqa: F401,E501
from swagger_server import util


class CreateCollection(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(
        self,
        name: str = None,
        off_chain_metadata: CollectionOffChainMetadata = None,
        short_word: str = None,
        publish_time: datetime = None,
        serie_id: int = None,
    ):  # noqa: E501
        """CreateCollection - a model defined in Swagger

        :param name: The name of this CreateCollection.  # noqa: E501
        :type name: str
        :param off_chain_metadata: The off_chain_metadata of this CreateCollection.  # noqa: E501
        :type off_chain_metadata: CollectionOffChainMetadata
        :param short_word: The short_word of this CreateCollection.  # noqa: E501
        :type short_word: str
        :param publish_time: The publish_time of this CreateCollection.  # noqa: E501
        :type publish_time: datetime
        :param serie_id: The serie_id of this CreateCollection.  # noqa: E501
        :type serie_id: int
        """
        self.swagger_types = {
            "name": str,
            "off_chain_metadata": CollectionOffChainMetadata,
            "short_word": str,
            "publish_time": datetime,
            "serie_id": int,
        }

        self.attribute_map = {
            "name": "name",
            "off_chain_metadata": "off_chain_metadata",
            "short_word": "short_word",
            "publish_time": "publish_time",
            "serie_id": "serie_id",
        }
        self._name = name
        self._off_chain_metadata = off_chain_metadata
        self._short_word = short_word
        self._publish_time = publish_time
        self._serie_id = serie_id

    @classmethod
    def from_dict(cls, dikt) -> "CreateCollection":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The CreateCollection of this CreateCollection.  # noqa: E501
        :rtype: CreateCollection
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self) -> str:
        """Gets the name of this CreateCollection.


        :return: The name of this CreateCollection.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this CreateCollection.


        :param name: The name of this CreateCollection.
        :type name: str
        """
        if name is None:
            raise ValueError(
                "Invalid value for `name`, must not be `None`"
            )  # noqa: E501

        self._name = name

    @property
    def off_chain_metadata(self) -> CollectionOffChainMetadata:
        """Gets the off_chain_metadata of this CreateCollection.


        :return: The off_chain_metadata of this CreateCollection.
        :rtype: CollectionOffChainMetadata
        """
        return self._off_chain_metadata

    @off_chain_metadata.setter
    def off_chain_metadata(self, off_chain_metadata: CollectionOffChainMetadata):
        """Sets the off_chain_metadata of this CreateCollection.


        :param off_chain_metadata: The off_chain_metadata of this CreateCollection.
        :type off_chain_metadata: CollectionOffChainMetadata
        """

        self._off_chain_metadata = off_chain_metadata

    @property
    def short_word(self) -> str:
        """Gets the short_word of this CreateCollection.


        :return: The short_word of this CreateCollection.
        :rtype: str
        """
        return self._short_word

    @short_word.setter
    def short_word(self, short_word: str):
        """Sets the short_word of this CreateCollection.


        :param short_word: The short_word of this CreateCollection.
        :type short_word: str
        """
        if short_word is None:
            raise ValueError(
                "Invalid value for `short_word`, must not be `None`"
            )  # noqa: E501

        self._short_word = short_word

    @property
    def publish_time(self) -> datetime:
        """Gets the publish_time of this CreateCollection.


        :return: The publish_time of this CreateCollection.
        :rtype: datetime
        """
        return self._publish_time

    @publish_time.setter
    def publish_time(self, publish_time: datetime):
        """Sets the publish_time of this CreateCollection.


        :param publish_time: The publish_time of this CreateCollection.
        :type publish_time: datetime
        """

        self._publish_time = publish_time

    @property
    def serie_id(self) -> int:
        """Gets the serie_id of this CreateCollection.


        :return: The serie_id of this CreateCollection.
        :rtype: int
        """
        return self._serie_id

    @serie_id.setter
    def serie_id(self, serie_id: int):
        """Sets the serie_id of this CreateCollection.


        :param serie_id: The serie_id of this CreateCollection.
        :type serie_id: int
        """
        if serie_id is None:
            raise ValueError(
                "Invalid value for `serie_id`, must not be `None`"
            )  # noqa: E501

        self._serie_id = serie_id
