from enum import Enum


def get_by_file_name(klass: object, base: str, default: str, filename):
    filename_array = filename.split(".")
    name = filename_array[0]
    upper_case_same = name.upper()
    enum_str = base + upper_case_same

    try:
        return klass[enum_str]
    except KeyError:
        return klass[default]


class EditionImageType(Enum):
    """Type enum for edition image types"""

    EDITION_IMAGE_TYPE_NIL = "EDITION_IMAGE_TYPE_NIL"
    EDITION_IMAGE_TYPE_HERO = "EDITION_IMAGE_TYPE_HERO"
    EDITION_IMAGE_TYPE_WEARABLE = "EDITION_IMAGE_TYPE_WEARABLE"
    EDITION_IMAGE_TYPE_MANNEQUIN_FULL = "EDITION_IMAGE_TYPE_MANNEQUIN_FULL"
    EDITION_IMAGE_TYPE_MANNEQUIN_ZOOM = "EDITION_IMAGE_TYPE_MANNEQUIN_ZOOM"
    EDITION_IMAGE_TYPE_CONTAINER = "EDITION_IMAGE_TYPE_CONTAINER"

    @classmethod
    def get_by_file_name(cls, filename: str):
        base_str = "EDITION_IMAGE_TYPE_"
        default = "EDITION_IMAGE_TYPE_NIL"
        return get_by_file_name(cls, base_str, default, filename)


class EditionVideoType(Enum):
    """Type enum for edition image types"""

    EDITION_VIDEO_TYPE_NIL = "EDITION_VIDEO_TYPE_NIL"
    EDITION_VIDEO_TYPE_UNBOXING = "EDITION_VIDEO_TYPE_UNBOXING"

    @classmethod
    def get_by_file_name(cls, filename: str):
        base_str = "EDITION_VIDEO_TYPE"
        default = "EDITION_VIDEO_TYPE_NIL"
        return get_by_file_name(cls, base_str, default, filename)
