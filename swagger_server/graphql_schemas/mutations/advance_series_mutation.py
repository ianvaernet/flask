from dataclasses import dataclass, field
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from swagger_server.graphql_schemas.schemas.metadata_schema import MetadataSchema


@dataclass
class AdvanceSeriesMutation(Mutation):
    """AdvanceSeries schema used to describe the advanceSeries schema for the
    dapper api, this lets you create a new series inside the dapper systems

    :Attributes:
        mutanion_name: str
        name: Attribute (str)
        metadata: Attribute (Attribute(metadata))
        response_field: list
    """

    mutation_name: str = "advanceSeries"

    name: Attribute = Attribute(key="name", value_type=str)
    # This is commented because dapper deleted this fields
    # metadata: Attribute = Attribute(key="metadata", value_type=MetadataSchema)
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: list = field(default_factory=lambda: ["success", "flowID"])

    def __init__(
        self,
        name: str,
        # description: str,
        idempotency_key: str,
    ):
        self.name.value = name
        # metadata = MetadataSchema(description)
        # self.metadata.value = metadata
        self.response_field: list = ["success", "flowID"]
        self.idempotency_key.value = idempotency_key
