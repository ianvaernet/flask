from dataclasses import dataclass, field
from swagger_server.graphql_schemas.schemas import EditionOnChainMetadataSchema
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from swagger_server.graphql_schemas.attribute import Attribute

response_fields: list = ["success", "flowID"]


@dataclass
class AddEditionsMutation(Mutation):
    """Class add edition mutation used to describe the Graphql mutation used to
    create new instances of Edition inside the dapper api.

    Attributes:
    """

    mutation_name: str = "addEdition"

    name: Attribute = Attribute(key="name", value_type=str)
    collection_id: Attribute = Attribute(key="collectionFlowID", value_type=int)
    onchain_metadata: Attribute = Attribute(
        key="onchainMetadata", value_type=EditionOnChainMetadataSchema
    )
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: list = field(default_factory=lambda: response_fields)

    def __init__(
        self,
        name: str,
        collection_id: int,
        onchain_metadata: EditionOnChainMetadataSchema,
        idempotency_key: str,
    ):
        self.collection_id.value = collection_id
        self.name.value = name
        self.onchain_metadata.value = onchain_metadata
        self.response_field: list = response_fields
        self.idempotency_key.value = idempotency_key
