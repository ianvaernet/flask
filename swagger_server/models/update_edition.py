# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.base_edition import BaseEdition  # noqa: F401,E501
from swagger_server.models.create_or_update_edition_on_chain_metadata import (
    CreateOrUpdateEditionOnChainMetadata,
)  # noqa: F401,E501
from swagger_server.models.edition_off_chain_metadata import (
    EditionOffChainMetadata,
)  # noqa: F401,E501
from swagger_server import util


class UpdateEdition(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(
        self,
        name: str = None,
        off_chain_metadata: EditionOffChainMetadata = None,
        publish_time: datetime = None,
        avatar_wearable_id: int = None,
        on_chain_metadata: CreateOrUpdateEditionOnChainMetadata = None,
        price: float = None,
        reserve_percentage: int = None,
    ):  # noqa: E501
        """UpdateEdition - a model defined in Swagger

        :param name: The name of this UpdateEdition.  # noqa: E501
        :type name: str
        :param off_chain_metadata: The off_chain_metadata of this UpdateEdition.  # noqa: E501
        :type off_chain_metadata: EditionOffChainMetadata
        :param publish_time: The publish_time of this UpdateEdition.  # noqa: E501
        :type publish_time: datetime
        :param avatar_wearable_id: The avatar_wearable_id of this UpdateEdition.  # noqa: E501
        :type avatar_wearable_id: int
        :param on_chain_metadata: The on_chain_metadata of this UpdateEdition.  # noqa: E501
        :type on_chain_metadata: CreateOrUpdateEditionOnChainMetadata
        :param price: The price of this UpdateEdition.  # noqa: E501
        :type price: float
        :param reserve_percentage: The reserve_percentage of this UpdateEdition.  # noqa: E501
        :type reserve_percentage: int
        """
        self.swagger_types = {
            "name": str,
            "off_chain_metadata": EditionOffChainMetadata,
            "publish_time": datetime,
            "avatar_wearable_id": int,
            "on_chain_metadata": CreateOrUpdateEditionOnChainMetadata,
            "price": float,
            "reserve_percentage": int,
        }

        self.attribute_map = {
            "name": "name",
            "off_chain_metadata": "off_chain_metadata",
            "publish_time": "publish_time",
            "avatar_wearable_id": "avatar_wearable_id",
            "on_chain_metadata": "on_chain_metadata",
            "price": "price",
            "reserve_percentage": "reserve_percentage",
        }
        self._name = name
        self._off_chain_metadata = off_chain_metadata
        self._publish_time = publish_time
        self._avatar_wearable_id = avatar_wearable_id
        self._on_chain_metadata = on_chain_metadata
        self._price = price
        self._reserve_percentage = reserve_percentage

    @classmethod
    def from_dict(cls, dikt) -> "UpdateEdition":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The UpdateEdition of this UpdateEdition.  # noqa: E501
        :rtype: UpdateEdition
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self) -> str:
        """Gets the name of this UpdateEdition.


        :return: The name of this UpdateEdition.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this UpdateEdition.


        :param name: The name of this UpdateEdition.
        :type name: str
        """

        self._name = name

    @property
    def off_chain_metadata(self) -> EditionOffChainMetadata:
        """Gets the off_chain_metadata of this UpdateEdition.


        :return: The off_chain_metadata of this UpdateEdition.
        :rtype: EditionOffChainMetadata
        """
        return self._off_chain_metadata

    @off_chain_metadata.setter
    def off_chain_metadata(self, off_chain_metadata: EditionOffChainMetadata):
        """Sets the off_chain_metadata of this UpdateEdition.


        :param off_chain_metadata: The off_chain_metadata of this UpdateEdition.
        :type off_chain_metadata: EditionOffChainMetadata
        """

        self._off_chain_metadata = off_chain_metadata

    @property
    def publish_time(self) -> datetime:
        """Gets the publish_time of this UpdateEdition.


        :return: The publish_time of this UpdateEdition.
        :rtype: datetime
        """
        return self._publish_time

    @publish_time.setter
    def publish_time(self, publish_time: datetime):
        """Sets the publish_time of this UpdateEdition.


        :param publish_time: The publish_time of this UpdateEdition.
        :type publish_time: datetime
        """

        self._publish_time = publish_time

    @property
    def avatar_wearable_id(self) -> int:
        """Gets the avatar_wearable_id of this UpdateEdition.


        :return: The avatar_wearable_id of this UpdateEdition.
        :rtype: int
        """
        return self._avatar_wearable_id

    @avatar_wearable_id.setter
    def avatar_wearable_id(self, avatar_wearable_id: int):
        """Sets the avatar_wearable_id of this UpdateEdition.


        :param avatar_wearable_id: The avatar_wearable_id of this UpdateEdition.
        :type avatar_wearable_id: int
        """

        self._avatar_wearable_id = avatar_wearable_id

    @property
    def on_chain_metadata(self) -> CreateOrUpdateEditionOnChainMetadata:
        """Gets the on_chain_metadata of this UpdateEdition.


        :return: The on_chain_metadata of this UpdateEdition.
        :rtype: CreateOrUpdateEditionOnChainMetadata
        """
        return self._on_chain_metadata

    @on_chain_metadata.setter
    def on_chain_metadata(
        self, on_chain_metadata: CreateOrUpdateEditionOnChainMetadata
    ):
        """Sets the on_chain_metadata of this UpdateEdition.


        :param on_chain_metadata: The on_chain_metadata of this UpdateEdition.
        :type on_chain_metadata: CreateOrUpdateEditionOnChainMetadata
        """

        self._on_chain_metadata = on_chain_metadata

    @property
    def price(self) -> float:
        """Gets the price of this UpdateEdition.


        :return: The price of this UpdateEdition.
        :rtype: float
        """
        return self._price

    @price.setter
    def price(self, price: float):
        """Sets the price of this UpdateEdition.


        :param price: The price of this UpdateEdition.
        :type price: float
        """

        self._price = price

    @property
    def reserve_percentage(self) -> int:
        """Gets the reserve_percentage of this UpdateEdition.


        :return: The reserve_percentage of this UpdateEdition.
        :rtype: int
        """
        return self._reserve_percentage

    @reserve_percentage.setter
    def reserve_percentage(self, reserve_percentage: int):
        """Sets the reserve_percentage of this UpdateEdition.


        :param reserve_percentage: The reserve_percentage of this UpdateEdition.
        :type reserve_percentage: int
        """

        self._reserve_percentage = reserve_percentage