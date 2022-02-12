from dataclasses import dataclass


@dataclass
class SuccessResponse:
    """Base class used for representing the success and flow_id values"""

    success: bool
