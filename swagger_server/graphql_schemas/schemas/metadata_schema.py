from dataclasses import dataclass
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.base_schema import BaseSchema


@dataclass
class MetadataSchema(BaseSchema):
    """Metadata class used for describing the most basic metadata schema

    :Attributes:
        description: Attribute (str)
    """

    description: Attribute = Attribute(key="description", value_type=str)

    def __init__(self, description: str):
        self.description.value = description
