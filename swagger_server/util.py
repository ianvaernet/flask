import datetime
import requests
from decimal import Decimal
from os import path, remove

import sys
import six
import enum
import uuid

from swagger_server import type_util
from flask import request
from tinytag import TinyTag


from swagger_server.exceptions.bad_request_exception import BadRequestException


def get_order_by(cls, order_by: str = "created_at", order: str = "desc"):
    attr = getattr(cls, order_by, "created_at")
    method_result = getattr(attr, order, "desc")()
    return method_result


def snake_to_pascal(string: str) -> str:
    """Convert an string from snake_case to PascalCase"""
    return string.lower().replace("_", " ").title().replace(" ", "")


def custom_asdict_factory(data):
    def convert_value(obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        return obj

    return dict((k, convert_value(v)) for k, v in data)


def get_jwt_token():
    return request.headers.get("Authorization")


def get_api_token():
    return request.headers.get("ApiToken")


def download_file(url: str, filename: str):
    http = requests.Session()
    response = http.get(url, allow_redirects=True)
    f = open("/tmp/{}".format(filename), "w+b")
    f.write(response.content)
    f.close()
    return "/tmp/{}".format(filename)


def get_metadata_from_file(file: str):
    return TinyTag.get(file)


def delete_file(file: str):
    if path.isfile(file):
        remove(file)
    else:
        raise Exception("Missing file")


def delete_empty_keys(dictionary: dict = {}) -> dict:
    """Deletes the keys of a dictionary whose values are empty strings or None

    :param dictionary: dict

    :return: dict
    """
    return {
        key: value for key, value in dictionary.items() if value != None and value != ""
    }


def format_datetime(date: datetime or None, format: bool = True) -> str or None:
    """If format flag is True, returns the date as a string with the format like Oct. 21, 2021 - 06:00 a.m.

    :param datetime: The datetime to format
    :type datetime: datetime

    :return: str or None
    """
    if format and isinstance(date, datetime.datetime):
        return (
            date.strftime("%b. %d, %Y - %I:%M %p")
            .replace("AM", "a.m.")
            .replace("PM", "p.m.")
        )
    return date


def format_price(price: Decimal or None, format: bool = True) -> str or None:
    """If format flag is True, returns the price as a string with $, thousands separator and 2 decimals

    :param price: The price to format
    :type price: Decimal

    :return: str
    """
    if format and isinstance(price, (Decimal, float)):
        return "${:,.2f}".format(price)
    return price


def print_to_err(*args):
    """Print to the flask server dev log

    :param obj: object
    """

    print(*args, file=sys.stderr)


def to_listable_model(model, listable_class):
    """Transforms a model into the listable version of it (with less properties)

    :param model: Model
    :param listable_class: class literal

    :return: Model
    """
    listable_model = listable_class()
    for attr in listable_model.to_dict().keys():
        value = getattr(model, attr)
        setattr(listable_model, attr, value)
    return listable_model


def publish_time_is_updated(new_model, current_model=None) -> bool:
    """Determines if the publish_time is updated

    :param new_model: BaseModel
    :param current_model: BaseModel

    :return: bool
    """
    if not new_model.publish_time:
        return False
    tzinfo = new_model.publish_time.tzinfo
    return (
        not getattr(current_model, "publish_time", None)
        or current_model.publish_time.replace(tzinfo=tzinfo) != new_model.publish_time
    )


def validate_price(price: Decimal or None) -> None:
    """Validates that the price is a positive number and throws a BadRequestException if it's not

    :param price: The price to validate

    :return: None
    """
    if price is not None and price < 0:
        raise BadRequestException(detail="The price must be greater than or equal to 0")


def validate_short_word(short_word: str or None) -> None:
    """Validates that the short_word is just one alphanumerical word (without spaces or special characters) with a maximum of 30 characters and throws a BadRequestException if it's not

    :param short_word: The short_word to validate

    :return: None
    """
    if short_word:
        if not short_word.isalnum():
            raise BadRequestException(
                detail="The short_word must contain only alphanumerical characters"
            )
        if len(short_word) > 30:
            raise BadRequestException(
                detail="The short_word must be less than or equal to 30 characters"
            )


def validate_required_fields(model, required_keys: list) -> None:
    """Validates if the required_keys in model are not empty and raises a BadRequestException if they are

    :param model: Model
    :param required_fields: list

    :return: None
    """
    empty_required_fields = []
    for key in required_keys:
        if (
            getattr(model, key) is None
            or getattr(model, key) == ""
            or getattr(model, key) == []
        ):
            empty_required_fields.append(key)
    if len(empty_required_fields) > 0:
        raise BadRequestException(
            detail="Some fields required to publish don't have a value: {empty_fields}".format(
                empty_fields=empty_required_fields
            )
        )


def validate_update(original_model, updated_model, not_updateable_fields: list) -> bool:
    """If the not_updatable_fields in updated_model are different from the original_model, sets those fields to the original value and returns True

    :param original_model: BaseModel
    :param updated_model: BaseModel
    :param not_updateable_fields: list

    :return: bool
    """
    tried_to_update_fields = False
    for attr in not_updateable_fields:
        original_value = original_model.__getattribute__(attr)
        updated_value = updated_model.__getattribute__(attr)
        if (
            updated_value
            and updated_value != original_value
            and (
                type(updated_value) is not datetime.datetime
                or updated_value.replace(tzinfo=None) != original_value
            )
        ):
            updated_model.__setattr__(attr, original_value)
            tried_to_update_fields = True
    return tried_to_update_fields


def _deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param data: dict, list or str.
    :param klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if klass in six.integer_types or klass in (float, str, bool, bytearray):
        return _deserialize_primitive(data, klass)
    elif klass == object:
        return _deserialize_object(data)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datetime(data)
    elif type_util.is_generic(klass):
        if type_util.is_list(klass):
            return _deserialize_list(data, klass.__args__[0])
        if type_util.is_dict(klass):
            return _deserialize_dict(data, klass.__args__[1])
    else:
        return deserialize_model(data, klass)


def _deserialize_primitive(data, klass):
    """Deserializes to primitive type.

    :param data: data to deserialize.
    :param klass: class literal.

    :return: int, long, float, str, bool.
    :rtype: int | long | float | str | bool
    """
    try:
        value = klass(data)
    except UnicodeEncodeError:
        value = six.u(data)
    except TypeError:
        value = data
    return value


def _deserialize_object(value):
    """Return an original value.

    :return: object.
    """
    return value


def deserialize_date(string):
    """Deserializes string to date.

    :param string: str.
    :type string: str
    :return: date.
    :rtype: date
    """
    try:
        from dateutil.parser import parse

        return parse(string).date()
    except ImportError:
        return string


def deserialize_datetime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param string: str.
    :type string: str
    :return: datetime.
    :rtype: datetime
    """
    try:
        from dateutil.parser import parse

        return parse(string)
    except ImportError:
        return string


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param data: dict, list.
    :type data: dict | list
    :param klass: class literal.
    :return: model object.
    """
    instance = klass()

    if not instance.swagger_types:
        return data

    for attr, attr_type in six.iteritems(instance.swagger_types):
        if (
            data is not None
            and instance.attribute_map[attr] in data
            and isinstance(data, (list, dict))
        ):
            value = data[instance.attribute_map[attr]]
            setattr(instance, attr, _deserialize(value, attr_type))

    return instance


def _deserialize_list(data, boxed_type):
    """Deserializes a list and its elements.

    :param data: list to deserialize.
    :type data: list
    :param boxed_type: class literal.

    :return: deserialized list.
    :rtype: list
    """
    return [_deserialize(sub_data, boxed_type) for sub_data in data]


def _deserialize_dict(data, boxed_type):
    """Deserializes a dict and its elements.

    :param data: dict to deserialize.
    :type data: dict
    :param boxed_type: class literal.

    :return: deserialized dict.
    :rtype: dict
    """
    return {k: _deserialize(v, boxed_type) for k, v in six.iteritems(data)}


def generate_uuid():
    """Generates an uuid

    :return: uuid of the object
    :rtype: string
    """
    return uuid.uuid4().hex
