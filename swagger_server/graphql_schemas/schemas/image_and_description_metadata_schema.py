from dataclasses import dataclass, field
from typing import List
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.enums import EditionImageType
from swagger_server.graphql_schemas.schemas.metadata_schema import MetadataSchema
from swagger_server.graphql_schemas.schemas.image_input_schema import ImageInputSchema


@dataclass
class ImageAndDescriptionMetadataSchema(MetadataSchema):
    """ImageAndDescriptionMetadata class discribe the schema used to add a
    description string as well as a group of images, this can be used as part
    of the offchain metadata for any schema that requires

    :Attributes:
        description: Attribute (str)
        images: list
    """

    description: Attribute = Attribute(key="description", value_type=str)
    images: List[ImageInputSchema] = field(default_factory=list)

    def __init__(
        self,
        description: str,
        images: List[ImageInputSchema] = [],
    ):
        self.description.value = description
        self.images = []

        for image in images:
            image_input: ImageInputSchema = ImageInputSchema()
            filename_list = image.split("/")
            filename = filename_list[-1]
            image_type = EditionImageType.get_by_file_name(filename)
            image_input.url.value = image
            image_input.image_type.value = image_type
            self.images.append(image_input)
