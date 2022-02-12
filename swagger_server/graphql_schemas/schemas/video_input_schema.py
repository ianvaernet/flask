from dataclasses import dataclass
from swagger_server.graphql_schemas.attribute import Attribute


@dataclass
class VideoInputSchema:
    """VideoInputSchema class defines the data structure used to describe any
    video file

    :Attributes:
        video_type: Attribute (str)
        url: Attribute (str)
        video_lenght: Attribute (float)
    """

    video_type: Attribute = Attribute(key="type", value_type=str)
    url: Attribute = Attribute(key="url", value_type=str)
    video_length: Attribute = Attribute(key="videoLength", value_type=float)

    def __init__(self, video_type: str = "", url: str = "", video_length: float = 0.0):
        self.video_type.value = video_type
        self.url.value = url
        self.video_length.value = video_length
