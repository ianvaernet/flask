from dataclasses import dataclass, field
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from typing import List
from datetime import datetime


@dataclass
class CloseCollectionMutation(Mutation):
    """Close Collection Mutation lets you close a collection related to the current
    series on the dapper systems

    :Attributes:
        mutation_name (str)
        flow_id (Attribute int)
        response_field str
        idempotency_key str
    """

    mutation_name: str = "closeCollection"

    flow_id: Attribute = Attribute(key="flowID", value_type=int)
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: str = "success"

    def __init__(self, flow_id: int, idempotency_key: str):
        self.flow_id.value = flow_id
        self.idempotency_key.value = idempotency_key
