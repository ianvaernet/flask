# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class BaseDrop(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(
        self,
        title: str = None,
        description: str = None,
        image_url: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        publish_time: datetime = None,
    ):  # noqa: E501
        """BaseDrop - a model defined in Swagger

        :param title: The title of this BaseDrop.  # noqa: E501
        :type title: str
        :param description: The description of this BaseDrop.  # noqa: E501
        :type description: str
        :param image_url: The image_url of this BaseDrop.  # noqa: E501
        :type image_url: str
        :param start_time: The start_time of this BaseDrop.  # noqa: E501
        :type start_time: datetime
        :param end_time: The end_time of this BaseDrop.  # noqa: E501
        :type end_time: datetime
        :param publish_time: The publish_time of this BaseDrop.  # noqa: E501
        :type publish_time: datetime
        """
        self.swagger_types = {
            "title": str,
            "description": str,
            "image_url": str,
            "start_time": datetime,
            "end_time": datetime,
            "publish_time": datetime,
        }

        self.attribute_map = {
            "title": "title",
            "description": "description",
            "image_url": "image_url",
            "start_time": "start_time",
            "end_time": "end_time",
            "publish_time": "publish_time",
        }
        self._title = title
        self._description = description
        self._image_url = image_url
        self._start_time = start_time
        self._end_time = end_time
        self._publish_time = publish_time

    @classmethod
    def from_dict(cls, dikt) -> "BaseDrop":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BaseDrop of this BaseDrop.  # noqa: E501
        :rtype: BaseDrop
        """
        return util.deserialize_model(dikt, cls)

    @property
    def title(self) -> str:
        """Gets the title of this BaseDrop.


        :return: The title of this BaseDrop.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title: str):
        """Sets the title of this BaseDrop.


        :param title: The title of this BaseDrop.
        :type title: str
        """

        self._title = title

    @property
    def description(self) -> str:
        """Gets the description of this BaseDrop.


        :return: The description of this BaseDrop.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this BaseDrop.


        :param description: The description of this BaseDrop.
        :type description: str
        """

        self._description = description

    @property
    def image_url(self) -> str:
        """Gets the image_url of this BaseDrop.


        :return: The image_url of this BaseDrop.
        :rtype: str
        """
        return self._image_url

    @image_url.setter
    def image_url(self, image_url: str):
        """Sets the image_url of this BaseDrop.


        :param image_url: The image_url of this BaseDrop.
        :type image_url: str
        """

        self._image_url = image_url

    @property
    def start_time(self) -> datetime:
        """Gets the start_time of this BaseDrop.


        :return: The start_time of this BaseDrop.
        :rtype: datetime
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time: datetime):
        """Sets the start_time of this BaseDrop.


        :param start_time: The start_time of this BaseDrop.
        :type start_time: datetime
        """

        self._start_time = start_time

    @property
    def end_time(self) -> datetime:
        """Gets the end_time of this BaseDrop.


        :return: The end_time of this BaseDrop.
        :rtype: datetime
        """
        return self._end_time

    @end_time.setter
    def end_time(self, end_time: datetime):
        """Sets the end_time of this BaseDrop.


        :param end_time: The end_time of this BaseDrop.
        :type end_time: datetime
        """

        self._end_time = end_time

    @property
    def publish_time(self) -> datetime:
        """Gets the publish_time of this BaseDrop.


        :return: The publish_time of this BaseDrop.
        :rtype: datetime
        """
        return self._publish_time

    @publish_time.setter
    def publish_time(self, publish_time: datetime):
        """Sets the publish_time of this BaseDrop.


        :param publish_time: The publish_time of this BaseDrop.
        :type publish_time: datetime
        """

        self._publish_time = publish_time
