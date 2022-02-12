from swagger_server.models.update_serie import UpdateSerie
from swagger_server.util import (
    delete_empty_keys,
    format_datetime,
    to_listable_model,
    get_order_by,
)
from typing import List
from sqlalchemy.orm import contains_eager, relationship
from sqlalchemy.sql import func
from swagger_server.models import Serie, CreateSerie, CollectionListable
from swagger_server.database.models import BaseModel
from swagger_server.__main__ import db
from dataclasses import dataclass
from swagger_server.database.enums import SerieStatus
from swagger_server.decorators.factory import factory
from datetime import datetime


@dataclass
@factory
class SerieModel(BaseModel):
    """
    SerieModel: DAO used in conjunction with the Serie model.

    :parent: BaseModel

    Attributes:
        id (int)
        name (str)
        description (str)
        short_word (str)                One word name for the Serie, used to generate the SKU of wearables in the CMS
        status (Status)
        publish_time (datetime)
        created_at (datetime)
        updated_at (datetime)
        dapper_flow_id (int)            The flow id of the Serie asigned by Dapper
        collections_count (int)         The amount of collections in the Serie (cannot be deleted if this is > 0)
        has_published_editions (bool)   Whether the Serie has published Editions (short_word cannot be updated if this is true)
        uuid (str)                      The uuid of the Serie
    """

    __tablename__ = "series"
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    description: str = db.Column(db.Text, nullable=True)
    short_word: str = db.Column(db.String(50), nullable=False, unique=True)
    status: SerieStatus = db.Column(db.Enum(SerieStatus), nullable=False)
    publish_time: datetime = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    dapper_flow_id: int = db.Column(db.Integer, nullable=True)
    collections = relationship("CollectionModel")
    collections_count: int = db.Column(db.Integer, nullable=False, default=0)
    has_published_editions: bool = db.Column(db.Boolean, nullable=False, default=False)
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)

    def to_obj(self, include_collections=False, format=True) -> Serie:
        collections = []
        if include_collections:
            for collection in self.collections:
                collections.append(
                    to_listable_model(
                        collection.to_obj(include_serie=False, format=format),
                        CollectionListable,
                    )
                )
        serie = Serie(
            id=self.id,
            name=self.name.strip(),
            description=self.description,
            short_word=self.short_word.strip(),
            status=self.status.value,
            publish_time=format_datetime(self.publish_time, format),
            collections=collections,
            collections_count=self.collections_count,
            has_published_editions=self.has_published_editions,
        )
        return serie

    @classmethod
    def from_obj(cls, obj: CreateSerie or UpdateSerie) -> "SerieModel":
        return cls(
            id=getattr(obj, "id", None),
            name=obj.name.strip() if obj.name else None,
            description=obj.description,
            short_word=obj.short_word.strip() if obj.short_word else None,
            status=getattr(obj, "status", None),
            publish_time=obj.publish_time,
            dapper_flow_id=getattr(obj, "dapper_flow_id", None),
        )

    @classmethod
    def get_all(
        cls,
        filters: dict = {},
        keyword: str = "",
        page: int = 0,
        page_size: int = 0,
        order: str = "desc",
        order_by: str = "created_at",
    ) -> List["SerieModel"]:
        filters = delete_empty_keys(filters)
        query = cls.query.order_by(get_order_by(cls, order_by, order))
        if filters:
            if "status" in filters.keys():
                if len(filters["status"]) > 1:
                    status_filters = []
                    for status in filters["status"]:
                        status_filters.append(cls.status == status)
                    query = query.filter(db.or_(*status_filters))
                else:
                    query = query.filter_by(status=filters["status"][0])
        if keyword:
            query = query.filter(
                db.or_(
                    cls.name.like("%" + keyword + "%"),
                    cls.short_word.like("%" + keyword + "%"),
                )
            )
        items: List[SerieModel]
        total_pages: int = 1
        if page and page_size:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            items = pagination.items
            total_pages = pagination.pages
        else:
            items = query.all()
        return items, total_pages

    @classmethod
    def get(cls, item_id: int, include_collections=False) -> "SerieModel":
        query = cls.query.filter_by(id=item_id)
        if include_collections:
            query = query.join(cls.collections, isouter=True).options(
                contains_eager(cls.collections)
            )
        item = query.one_or_none()
        return item
