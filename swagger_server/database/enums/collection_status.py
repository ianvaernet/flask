from enum import Enum


class CollectionStatus(Enum):
    """
    Type status used in collections
    """

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    INACTIVE = "INACTIVE"
