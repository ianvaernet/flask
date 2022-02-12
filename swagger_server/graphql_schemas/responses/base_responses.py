from dataclasses import dataclass


@dataclass
class SuccessResponse:
    """Base class used for representing the success value"""

    status: bool


@dataclass
class SuccessFlowIdResponse(SuccessResponse):
    """Base class used for representing the success and flow_id values"""

    flow_id: int


@dataclass
class SuccessDapperIdResponse(SuccessResponse):
    """Base class used for representing the success and dapper_id values"""

    dapper_id: str
