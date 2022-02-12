from typing import List
from dataclasses import dataclass, field
from swagger_server.graphql_schemas.queries.query import Query
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.schemas import SearchEditionsFiltersSchema

response_fields = ["count", "editions{id}"]


@dataclass
class SearchEditionsQuery(Query):
    """Get all the Editions that match the provided filters
    :Attributes:
        mutation_name: str
        filters: Attribute (SearchEditionsFiltersSchema)
        response_field: list
    """

    mutation_name: str = "searchEditions"
    filters: Attribute = Attribute(
        key="filters", value_type=SearchEditionsFiltersSchema
    )
    response_field: list = field(default_factory=lambda: response_fields)

    def __init__(self, flow_ids: List[int]):
        self.filters.value = SearchEditionsFiltersSchema(flow_ids=flow_ids)
        self.response_field = response_fields
