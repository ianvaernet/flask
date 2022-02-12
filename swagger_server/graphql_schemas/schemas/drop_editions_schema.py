from dataclasses import dataclass
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.base_schema import BaseSchema


@dataclass
class DropEditionsSchema(BaseSchema):
    """DropEditionsSchema class defines the data structure used to describe any
    a drop edition

    :Attributes:
        edition_id: Attribute (str)
        drop_price: Attribute (float)
    """

    edition_id: Attribute = Attribute(key="editionID", value_type=str)
    drop_price: Attribute = Attribute(key="dropPrice", value_type=str)

    def __init__(self, edition_id: str, drop_price: float = 0.0):
        self.edition_id.value = edition_id
        self.drop_price.value = str(drop_price)
