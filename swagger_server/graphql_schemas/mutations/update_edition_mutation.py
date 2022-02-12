from dataclasses import dataclass
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from swagger_server.graphql_schemas.schemas import (
    ImageVideosAndDescriptionMetadataSchema,
)


@dataclass
class UpdateEditionMutation(Mutation):
    """UpdateEditionMutation class represents the required mutation to update
    the offchain metadata for an specific edition

    :Attributes:
        mutation_name: str
        edition_id: Attribute (str)
        off_chain_metadata: Attribute (ImageAndDescriptionMetadata)
        response_field: str
    """

    mutation_name: str = "updateEdition"

    edition_id: Attribute = Attribute(key="editionID", value_type=str)
    offchain_metadata: Attribute = Attribute(
        key="offchainMetadata", value_type=ImageVideosAndDescriptionMetadataSchema
    )
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: str = "success"

    def __init__(
        self,
        edition_id: str,
        off_chain_metadata: ImageVideosAndDescriptionMetadataSchema,
        idempotency_key: str,
    ):
        self.edition_id.value = edition_id
        self.offchain_metadata.value = off_chain_metadata
        self.idempotency_key.value = idempotency_key
