from enum import Enum


class DropStatus(Enum):
    """
    Type status used in drops
    """

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ON_SALE = "ON_SALE"
    FINISHED = "FINISHED"
