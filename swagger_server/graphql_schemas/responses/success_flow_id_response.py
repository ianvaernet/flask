from dataclasses import dataclass
from swagger_server.graphql_schemas.responses.success_response import SuccessResponse


@dataclass
class SuccessFlowIdResponse(SuccessResponse):
    """Base class used for representing the success and flow_id values"""

    flow_id: int
