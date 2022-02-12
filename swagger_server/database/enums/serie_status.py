from enum import Enum


class SerieStatus(Enum):
    """
    Type status used in series
    """

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
