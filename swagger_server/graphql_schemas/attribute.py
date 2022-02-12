from dataclasses import dataclass
from typing import Any
from swagger_server.graphql_schemas.attribute_descriptor import (
    create_attribute_descriptor,
)


@dataclass(eq=True)
class Attribute:
    """Attribute class lets us define a custom dynamic type with tho possibility
    of defining how each attribute will be formatted at the moment of creating
    the graphql schema.
    We can define a value_type at the moment of calling the constructor and
    this will be used for type checking for the attribute value when we are
    ready to assign it.

    :Attributes:
        key: str
        value: Any
    """

    key: str
    value: Any = None
    value_type: Any = str

    def to_dict(self) -> dict:
        """convert the Attribute into a valid dapper graphql dictionary

        :return: dict
        """
        return {self.key: self.value, "type": self.value_type}

    def __init__(self, key: str, value_type: str):
        self.key = key
        descriptor = create_attribute_descriptor(value_type)
        self.value = descriptor()
        self.value_type = value_type

    def __hash__(self):
        return hash(self.key)
