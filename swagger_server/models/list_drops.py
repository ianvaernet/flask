# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.drop_listable import DropListable  # noqa: F401,E501
from swagger_server import util


class ListDrops(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(
        self, drops: List[DropListable] = None, total_pages: int = None
    ):  # noqa: E501
        """ListDrops - a model defined in Swagger

        :param drops: The drops of this ListDrops.  # noqa: E501
        :type drops: List[DropListable]
        :param total_pages: The total_pages of this ListDrops.  # noqa: E501
        :type total_pages: int
        """
        self.swagger_types = {"drops": List[DropListable], "total_pages": int}

        self.attribute_map = {"drops": "drops", "total_pages": "total_pages"}
        self._drops = drops
        self._total_pages = total_pages

    @classmethod
    def from_dict(cls, dikt) -> "ListDrops":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ListDrops of this ListDrops.  # noqa: E501
        :rtype: ListDrops
        """
        return util.deserialize_model(dikt, cls)

    @property
    def drops(self) -> List[DropListable]:
        """Gets the drops of this ListDrops.


        :return: The drops of this ListDrops.
        :rtype: List[DropListable]
        """
        return self._drops

    @drops.setter
    def drops(self, drops: List[DropListable]):
        """Sets the drops of this ListDrops.


        :param drops: The drops of this ListDrops.
        :type drops: List[DropListable]
        """

        self._drops = drops

    @property
    def total_pages(self) -> int:
        """Gets the total_pages of this ListDrops.


        :return: The total_pages of this ListDrops.
        :rtype: int
        """
        return self._total_pages

    @total_pages.setter
    def total_pages(self, total_pages: int):
        """Sets the total_pages of this ListDrops.


        :param total_pages: The total_pages of this ListDrops.
        :type total_pages: int
        """

        self._total_pages = total_pages
