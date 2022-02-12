from enum import Enum


class EditionVideo(Enum):
    """Type of Edition image used to publish it to Dapper API"""

    EDITION_VIDEO_TYPE_NIL = "EDITION_VIDEO_TYPE_NIL"
    EDITION_VIDEO_TYPE_UNBOXING = "EDITION_VIDEO_TYPE_UNBOXING"

    @classmethod
    def _missing_(cls, value):
        if value.find("unboxing") != -1:
            return cls("EDITION_VIDEO_TYPE_UNBOXING")
        else:
            return cls("EDITION_IMAGE_TYPE_NIL")
