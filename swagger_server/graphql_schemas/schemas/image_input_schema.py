from swagger_server.graphql_schemas.attribute import Attribute
from dataclasses import dataclass


@dataclass
class ImageInputSchema:
    """Image imput schema this schema can be used in any mutation that needs to
    add an image with type and an specific url

    :Attributes:
        image_type: Attribute (str)
        url: Attribute (str)
    """

    image_type: Attribute = Attribute(key="type", value_type=str)
    url: Attribute = Attribute(key="url", value_type=str)
