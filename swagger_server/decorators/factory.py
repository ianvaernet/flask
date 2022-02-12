import faker
import random
from dataclasses import fields
from random import randint
from enum import Enum
from datetime import datetime
from swagger_server.database.models.base_model import BaseModel
from collections.abc import Callable
from typing import Any
from collections import deque
from enum import Enum
from decimal import Decimal
from swagger_server.util import generate_uuid


def __handle_enum(enum: "Enum") -> Callable:
    """Return the lambda function used to get the default value for an
    enumeration

    :param enum: Enum

    :return: Callable
    """
    return lambda: list(enum)[0]


__fkr: "Faker" = faker.Faker()
__dispatch_table: dict = {
    str: lambda: __fkr.text(21),
    int: lambda: randint(0, 1000),
    float: lambda: random.uniform(10.5, 750.5),
    Decimal: lambda: random.uniform(10.5, 750.5),
    Enum: __handle_enum,
    datetime: lambda: datetime.now(),
    bool: lambda: random.choice([True, False]),
}


def factory(cls):
    """Factory decorator that adds the factory method to a dataclass

    :param cls: the class to apply the decorator
    """

    def __to_db(self):
        """save the created entity to the database"""
        self.add()
        self.commit()

    def factory_has_many(self, relationships: dict = {}):
        """create a one to many relations (create n instances of the related

        :param relationships: dict
        """
        if isinstance(self, BaseModel):
            # Check if the class is a database model to write it to the
            # database
            self.__to_db()
        for relation, relation_to_klass in relationships.items():
            for klass, qty_key in relation_to_klass.items():
                for _ in range(qty_key["qty"]):
                    klass.factory(
                        keys={
                            qty_key["key"]: self.id,
                        }
                    )

    def factory_has_one(self, relationships: dict = {}):
        """Create a relation belongs to one, has one

        :param relationships: dict
        """
        for key, model in relationships.items():
            model_instance = model.factory()
            setattr(self, key, model_instance.id)

    def factory(cls, has_one: dict = {}, keys: dict = {}) -> cls:
        """Create a new instance of a dataclass

        :param has_one: dict, the dictionary of relations has_one
        :param keys: dict, the dictionary of keys to force

        :return instance
        """
        instance = cls()  # Create a new empty instance

        def __handle_field(field: tuple) -> "tuple[str, Callable[[], Any]]":
            nonlocal instance
            nonlocal keys
            nonlocal has_one
            field_name: str = field.name

            if field_name == "id":
                return

            if field_name == "uuid":
                setattr(instance, field_name, generate_uuid())

            if field_name in keys:
                # If the field name is found in the keys array then it will
                # use the value passed in the keys parameters for that specific
                # field
                setattr(instance, field_name, keys[field_name])
                return

            if field_name in has_one:
                # If the key is found in the has_one dictionary then it's a
                # relation and an instance of the relation must be created and
                # assign
                instance.factory_has_one(has_one)
                return

            field_type: object = field.type
            generator: Callable[[], Any] = (
                __dispatch_table[Enum](field_type)
                if issubclass(field_type, Enum)
                else __dispatch_table[field_type]
            )
            # Get the data generator based on the attribute type
            setattr(instance, field_name, generator())
            # Set the attribute to the instance

        field_tuple: tuple = fields(instance)
        deque(map(__handle_field, field_tuple))
        # Let's execute the map function
        if isinstance(instance, BaseModel):
            instance.__to_db()
        return instance

    setattr(cls, "factory", classmethod(factory))
    setattr(cls, "factory_has_many", factory_has_many)
    setattr(cls, "factory_has_one", factory_has_one)
    setattr(cls, "__to_db", __to_db)
    return cls
