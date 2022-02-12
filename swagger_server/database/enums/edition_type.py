from enum import Enum


class EditionType(Enum):
    """Type enum for editions

    Define the different types that an edition can be.
    """

    EDITION_TYPE_AVATAR_NIL = "EDITION_TYPE_AVATAR_NIL"
    EDITION_TYPE_AVATAR_STATUE = "EDITION_TYPE_AVATAR_STATUE"
    EDITION_TYPE_AVATAR_WEARABLE = "EDITION_TYPE_AVATAR_WEARABLE"
