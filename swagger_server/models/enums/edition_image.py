from enum import Enum


class EditionImage(Enum):
    """Type of Edition image used to publish it to Dapper API"""

    EDITION_IMAGE_TYPE_NIL = "EDITION_IMAGE_TYPE_NIL"
    EDITION_IMAGE_TYPE_HERO = "EDITION_IMAGE_TYPE_HERO"
    EDITION_IMAGE_TYPE_WEARABLE = "EDITION_IMAGE_TYPE_WEARABLE"
    EDITION_IMAGE_TYPE_MANNEQUIN_FULL = "EDITION_IMAGE_TYPE_MANNEQUIN_FULL"
    EDITION_IMAGE_TYPE_MANNEQUIN_ZOOM = "EDITION_IMAGE_TYPE_MANNEQUIN_ZOOM"
    EDITION_IMAGE_TYPE_CONTAINER = "EDITION_IMAGE_TYPE_CONTAINER"

    @classmethod
    def _missing_(cls, value):
        if value.find("hero") != -1:
            return cls("EDITION_IMAGE_TYPE_HERO")
        elif value.find("zoom") != -1:
            return cls("EDITION_IMAGE_TYPE_MANNEQUIN_ZOOM")
        elif value.find("mannequin") != -1:
            return cls("EDITION_IMAGE_TYPE_MANNEQUIN_FULL")
        elif value.find("container") != -1:
            return cls("EDITION_IMAGE_TYPE_CONTAINER")
        elif value.find("wearable") != -1:
            return cls("EDITION_IMAGE_TYPE_WEARABLE")
        else:
            return cls("EDITION_IMAGE_TYPE_NIL")
