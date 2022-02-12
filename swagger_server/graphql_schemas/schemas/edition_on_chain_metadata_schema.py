from dataclasses import dataclass
from swagger_server.database.enums import (
    EditionRarity,
    EditionType,
    DesignSlot,
)
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.base_schema import BaseSchema


@dataclass
class EditionOnChainMetadataSchema(BaseSchema):
    """EditionOnChainMetadataSchema represents the schema used to model an
    create the correct graphql to create the edition on chain metadata

    :Attribute:
        rarity: Attribute (str)
        celebrity: Attribute (str)
        artist: Attribute (str)
        edition_type: Attribute (str)
        design_slot: Attribute (str)
        publisher: Attribute (str)
        trademark: Attribute (str)
        avatar_wearable_sku: Attribute (str)
    """

    rarity: Attribute = Attribute(key="rarity", value_type=str)
    celebrity: Attribute = Attribute(key="celebrity", value_type=str)
    artist: Attribute = Attribute(key="artist", value_type=str)
    edition_type: Attribute = Attribute(key="type", value_type=str)
    design_slot: Attribute = Attribute(key="designSlot", value_type=str)
    publisher: Attribute = Attribute(key="publisher", value_type=str)
    trademark: Attribute = Attribute(key="trademark", value_type=str)
    avatar_wearable_sku: Attribute = Attribute(key="avatarWearableSKU", value_type=str)

    def __init__(
        self,
        rarity: EditionRarity,
        artist: str,
        celebrity: str,
        edition_type: EditionType,
        design_slot: DesignSlot,
        publisher: str,
        trademark: str,
        avatar_wearable_sku: str,
    ):
        self.rarity.value = rarity.value
        self.artist.value = artist
        self.celebrity.value = celebrity
        self.edition_type.value = edition_type.value
        self.design_slot.value = design_slot.value
        self.publisher.value = publisher
        self.trademark.value = trademark
        self.avatar_wearable_sku.value = avatar_wearable_sku
