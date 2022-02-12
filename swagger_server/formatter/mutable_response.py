from swagger_server.models.base_model_ import Model


def mutable_response(obj: Model) -> "MutableResponse":
    """Create a new mutable response capable of adding new data to the
    to the response

    :param obj: Model
    """

    class MutableResponse:
        """Mutable Response lets you add new entries to the body dictionary

        :Attributes:
            __body (dict)
        """

        __body: dict

        def __init__(self):
            self.__body = obj.to_dict()

        def append(self, key: str, value: object) -> "MutableResponse":
            """Append a new key:value to the body dictionary

            :param key: str
            :param value: object
            """
            self.__body[key] = value
            return self

        def to_dict(self) -> dict:
            """return the body dictionary"""
            return self.__body

    return MutableResponse()
