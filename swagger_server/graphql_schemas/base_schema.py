import json
import sys
import abc
import re
from typing import Callable
from dataclasses import asdict, is_dataclass
from functools import reduce
from swagger_server.util import print_to_err


class BaseSchema(metaclass=abc.ABCMeta):
    """Base metaclass that discribes the schemas used to define any mutation
    query or schema.
    """

    @staticmethod
    def __to_str_reducer(instance: object, fields: dict) -> Callable:
        """Generate the reducer function used to create the graphql query based
        on a mutation, query or schema

        :param instance: object
        :param fields: dict

        :returns Callable
        """

        def reducer(acumulator: str, value: dict) -> str:
            """convert the dictionaries to the required string to form the
            graphql query

            :param acumulator: str
            :param value: dict

            :return: str
            """
            nonlocal fields

            value_type = value[1]
            value = value[0]
            temp_str: str = ""
            value_str: str = ""
            for key in value:
                if isinstance(value[key], str):
                    value_str = '"{value}"'.format(value=value[key])
                elif isinstance(value[key], list):
                    try:
                        attrs = (getattr(instance, key)).value
                    except AttributeError:
                        for key_name in fields:
                            field = fields[key_name]
                            if type(field) is dict and field["key"] in value.keys():
                                attrs = (getattr(instance, key_name)).value
                    array = []
                    temp_str = ""
                    for attr in attrs:
                        if isinstance(attr, int):
                            body = str(attr)
                        else:
                            body = attr.to_query_body()
                        temp_str += body + ","
                    value_str = "[ {body} ]".format(body=temp_str)
                elif isinstance(value[key], dict):
                    try:
                        attr = (getattr(instance, key)).value
                        body = attr.to_query_body()
                        value_str = body
                    except AttributeError:
                        if "ID" in key:
                            key = key.replace("ID", "Id")
                        attr_name = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
                        attr = (getattr(instance, attr_name)).value
                        body = attr.to_query_body()
                        value_str = body

                else:
                    value_str = value[key]
                if (
                    value_type is str
                    and value_str.isupper()
                    and " " not in value_str
                ):
                    value_str = value_str.replace('"', "")
                temp_str = "{key}: {value},".format(key=key, value=value_str)
            if not acumulator:
                acumulator = ""
            acumulator += temp_str
            return acumulator

        return reducer

    @staticmethod
    def __attribute_to_dict_mapper(fields: dict) -> Callable:
        """Generate the mapper function to convert an attribute to a dictionary
        to be able to then create the valid query

        :param fields: dict

        :returns: Callable
        """

        def attribute_to_dict(attribute):
            """convert an attribute to the required dict

            :param attribute: Attribute|any
            """
            nonlocal fields
            if isinstance(fields[attribute], dict) or is_dataclass(fields[attribute]):
                return (
                    {fields[attribute]["key"]: fields[attribute]["value"]},
                    fields[attribute]["value_type"],
                )

        return attribute_to_dict

    def to_query_body(self) -> str:
        """Method used to convert a mutation to the required query

        :return: str
        """
        fields = asdict(self)
        mapper = self.__class__.__attribute_to_dict_mapper(fields)
        reducer = BaseSchema.__to_str_reducer(self, fields)
        attributes = list(map(mapper, fields))
        filtered_list = [
            attribute
            for attribute in attributes
            if attribute and list(attribute[0].values())[0]
        ]
        body = reduce(reducer, filtered_list, "")
        return "{{{body}}}".format(body=body)
