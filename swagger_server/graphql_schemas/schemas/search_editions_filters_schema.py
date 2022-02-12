from dataclasses import dataclass, field
from typing import List
from dataclasses import dataclass
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.base_schema import BaseSchema


@dataclass
class SearchEditionsFiltersSchema(BaseSchema):
    """SearchEditionsFiltersSchema represents the schema used to apply filters to the searchEditions query

    :Attribute:
        byFlowIDs: Attribute (List[int])
    """

    byFlowIDs: Attribute = Attribute(key="byFlowIDs", value_type=List[int])

    def __init__(self, flow_ids: List[int]):
        self.byFlowIDs.value = flow_ids
