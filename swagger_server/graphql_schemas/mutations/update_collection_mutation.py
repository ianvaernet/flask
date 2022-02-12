from dataclasses import dataclass
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from swagger_server.graphql_schemas.schemas import ImageAndDescriptionMetadataSchema
from typing import List
from datetime import datetime


@dataclass
class UpdateCollectionMutation(Mutation):
    """UpdateCollectionMutation class represents a dapper update collection
    mutation used to change the offchain metadata for an specific collection

    :Attributes:
        mutation_name: str
        collection_id: Attribute (str)
        metadata: Attribute (ImageAndDescriptionMetadata)

        response_field: str
    """

    mutation_name: str = "updateCollection"

    collection_id: Attribute = Attribute(key="id", value_type=str)
    metadata: Attribute = Attribute(
        key="metadata", value_type=ImageAndDescriptionMetadataSchema
    )
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: str = "success"

    def __init__(
        self,
        collection_id: int,
        description: str,
        idempotency_key: str,
        images=[],
    ):
        self.collection_id.value = str(collection_id)
        metadata_instance = ImageAndDescriptionMetadataSchema(
            description=description,
            images=images,
        )

        self.metadata.value = metadata_instance
        self.idempotency_key.value = idempotency_key
