from dataclasses import dataclass, field
from datetime import datetime
from swagger_server.graphql_schemas.attribute import Attribute
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from swagger_server.graphql_schemas.schemas.drop_editions_schema import (
    DropEditionsSchema,
)
from typing import List
from datetime import datetime


@dataclass
class UpsertDropMutation(Mutation):
    """UpsertDropMutation class models the mutation used for creating and
    updating any drop in the Dapper api.

    :Attributes:
        mutation_name: str
        id: Attribute (str)
        title: Attribute (str)
        description: Attribute (str)
        image_url: Attribute (str)
        drop_price: Attribute (float)
        drop_editions: Attribute (list)
        start_time: Attribute (datetime)
        end_time: Attribute (datetime)
        response_field: str
    """

    mutation_name: str = "upsertDrop"

    id: Attribute = Attribute(key="id", value_type=str)
    title: Attribute = Attribute(key="title", value_type=str)
    description: Attribute = Attribute(key="description", value_type=str)
    image_url: Attribute = Attribute(key="imageURL", value_type=str)
    start_time: Attribute = Attribute(key="startTime", value_type="time")
    end_time: Attribute = Attribute(key="endTime", value_type="time")
    drop_editions: Attribute = Attribute(key="dropEditionPrices", value_type=list)
    idempotency_key: Attribute = Attribute(key="idempotencyKey", value_type=str)

    response_field: str = "dropID"

    def __init__(
        self,
        title: str,
        description: str,
        image_url: str,
        drop_editions: List,
        start_time: datetime,
        end_time: datetime,
        idempotency_key: str,
        id: int = None,
    ):
        self.id.value = str(id) if id else None
        drop_editions_list = []
        self.title.value = title
        self.image_url.value = image_url
        self.end_time.value = end_time.strftime("%Y-%m-%dT%H:%M:%SZ") if end_time else None
        self.start_time.value = start_time.strftime("%Y-%m-%dT%H:%M:%SZ") if start_time else None
        self.description.value = description
        for drop_edition in drop_editions:
            drop_edition_schema = DropEditionsSchema(
                drop_edition.edition.dapper_edition_id,
                drop_edition.price,
            )
            drop_editions_list.append(drop_edition_schema)
        self.drop_editions.value = drop_editions_list
        self.idempotency_key.value = idempotency_key
