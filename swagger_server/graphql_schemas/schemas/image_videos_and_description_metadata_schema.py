from dataclasses import dataclass, field
from typing import List
from swagger_server.util import (
    download_file,
    get_metadata_from_file,
    delete_file,
)
from swagger_server.graphql_schemas.enums import EditionVideoType
from swagger_server.graphql_schemas.schemas.video_input_schema import VideoInputSchema
from swagger_server.graphql_schemas.schemas.image_and_description_metadata_schema import (
    ImageAndDescriptionMetadataSchema,
)


@dataclass
class ImageVideosAndDescriptionMetadataSchema(ImageAndDescriptionMetadataSchema):
    """ImageVideosAndDescriptionMetadata extends the
    ImageAndDescriptionMetadata to be able to add a list of videos also

    :Attributes:
        videos: list
    """

    videos: List[VideoInputSchema] = field(default_factory=list)

    def __init__(self, description: str, images: dict = [], videos: dict = []):
        self.description.value = description
        self.videos = []

        for video in videos:
            video_input: VideoInputSchema = VideoInputSchema()
            file = download_file(video, "temp.mp4")
            tags = get_metadata_from_file(file)
            delete_file(file)
            filename_list = video.split("/")
            filename = filename_list[-1]
            video_input.url.value = video
            video_input.video_type.value = EditionVideoType.get_by_file_name(filename)
            video_input.video_length.value = tags.duration
            self.videos.append(video_input)

        super().__init__(description, images)
