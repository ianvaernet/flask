from dataclasses import dataclass

from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.base_schema import BaseSchema


@dataclass
class MintNftOrderInputSchema(BaseSchema):
    """MintNftOrderInput schema represents the basic data structure used for
    defining the quantity to mint of an specific edition

    :Attributes:
        edition_id: Attribute (int)
        quantity: Attribute (int)
    """

    edition_id: Attribute = Attribute(key="editionFlowID", value_type=int)
    quantity: Attribute = Attribute(key="quantity", value_type=int)
