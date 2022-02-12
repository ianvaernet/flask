from dataclasses import dataclass, field
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from typing import List
from datetime import datetime


@dataclass
class AddCollectionMutation(Mutation):
    """Add Collection Mutation lets you create a mutation that will create a
    new collection on the dapper systems

    :Attributes:
        mutation_name (str)
        name (Attribute str)
        series_flow_id (Attribute int)
        response_field list
    """

    mutation_name: str = "addCollection"

    name: Attribute = Attribute(key="name", value_type=str)
    series_flow_id: Attribute = Attribute(key="seriesFlowID", value_type=int)
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: list = field(default_factory=lambda: ["success", "flowID"])

    def __init__(self, name: str, series_flow_id: int, idempotency_key: str):
        self.name.value = name
        self.series_flow_id.value = series_flow_id
        self.response_field: list = ["success", "flowID"]
        self.idempotency_key.value = idempotency_key
