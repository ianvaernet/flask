from enum import Enum


class EditionStatus(Enum):
    """
    Type status for editions
    """

    DRAFT = "DRAFT"
    CREATING = "CREATING"
    CREATED = "CREATED"
    MINTED = "MINTED"
    ON_SALE = "ON_SALE"
    ERROR = "ERROR"
