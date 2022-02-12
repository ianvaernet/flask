from enum import Enum


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
        filename_array = filename.split(".")
        name = filename_array[0]
        upper_case_same = name.upper()
        enum_str = base_str + upper_case_same

        try:
            return cls[enum_str]
        except KeyError:
            return cls["EDITION_IMAGE_TYPE_NIL"]
