from swagger_server.models.update_collection import UpdateCollection
from swagger_server.database.models import BaseModel
from typing import List
from sqlalchemy.orm import contains_eager, relationship
from sqlalchemy.sql import func
from swagger_server.models import (
    Collection,
    CreateCollection,
    CollectionOffChainMetadata,
    EditionListable,
    SerieListable,
)
from swagger_server.__main__ import db
from dataclasses import dataclass
from swagger_server.database.enums import CollectionStatus
from swagger_server.decorators.factory import factory
from datetime import datetime
from swagger_server.util import (
    delete_empty_keys,
    format_datetime,
    to_listable_model,
    get_order_by,
)


@dataclass
@factory
class CollectionModel(BaseModel):
    """
    CollectionModel: DAO used in conjunction with the Collection model.

    :parent: BaseModel

    Attributes:
        id (int)
        name (str)
        description (str)
        short_word (str)                One word name for the Collection, used to generate the SKU of wearables in the CMS
        status (Status)
        publish_time (datetime)
        created_at (datetime)
        updated_at (datetime)
        dapper_flow_id (int)            The flow id of the Collection asigned by Dapper
        serie_id (int)                  The id of the associated Serie
        wearables_count (int)           The amount of wearables in the Collection (cannot be deleted if this is > 0)
        has_published_editions (bool)   Whether the Collection has published Editions (short_word cannot be updated if this is true)
        uuid (str)                      The uuid of the Collection
    """

    __tablename__ = "collections"
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    description: str = db.Column(db.Text, nullable=True)
    short_word: str = db.Column(db.String(50), nullable=False, unique=True)
    status: CollectionStatus = db.Column(db.Enum(CollectionStatus), nullable=False)
    publish_time: datetime = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    dapper_flow_id: int = db.Column(db.Integer, nullable=True)
    serie_id: int = db.Column(db.Integer, db.ForeignKey("series.id"), nullable=False)
    wearables_count: int = db.Column(db.Integer, nullable=False, default=0)
    has_published_editions: bool = db.Column(db.Boolean, nullable=False, default=False)
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)
    serie = relationship("SerieModel", back_populates="collections")
    editions = relationship("EditionModel")

    def to_obj(
        self, include_serie=True, include_editions=False, format=True
    ) -> "Collection":
        serie = None
        editions = []
        if include_serie:
            serie = to_listable_model(self.serie.to_obj(format=format), SerieListable)
        if include_editions:
            for edition in self.editions:
                editions.append(
                    to_listable_model(
                        edition.to_obj(include_collection=False, format=format),
                        EditionListable,
                    )
                )

        off_chain_metadata = CollectionOffChainMetadata(description=self.description)

        collection = Collection(
            id=self.id,
            name=self.name.strip(),
            off_chain_metadata=off_chain_metadata,
            short_word=self.short_word.strip(),
            status=self.status.value,
            publish_time=format_datetime(self.publish_time, format),
            serie=serie,
            editions=editions,
            wearables_count=self.wearables_count,
            has_published_editions=self.has_published_editions,
        )

        return collection

    @classmethod
    def from_obj(cls, obj: CreateCollection or UpdateCollection) -> "CollectionModel":
        off_chain_metadata = obj.off_chain_metadata
        return cls(
            id=getattr(obj, "id", None),
            name=obj.name.strip() if obj.name else None,
            description=getattr(off_chain_metadata, "description", None),
            short_word=obj.short_word.strip() if obj.short_word else None,
            status=getattr(obj, "status", None),
            publish_time=obj.publish_time,
            dapper_flow_id=getattr(obj, "dapper_flow_id", None),
            serie_id=obj.serie_id,
        )

    @classmethod
    def get_all(
        cls,
        filters: dict = {},
        keyword: str = "",
        page: int = 0,
        page_size: int = 0,
        include_serie=True,
        order: str = "desc",
        order_by: str = "created_at",
    ) -> List["CollectionModel"]:
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
            if "serie_id" in filters.keys():
                query = query.filter_by(serie_id=filters["serie_id"])
        if keyword:
            query = query.filter(
                db.or_(
                    cls.name.like("%" + keyword + "%"),
                    cls.short_word.like("%" + keyword + "%"),
                )
            )
        if include_serie:
            query = query.join(cls.serie).options(contains_eager(cls.serie))
        items: List[CollectionModel]
        total_pages: int = 1
        if page and page_size:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            items = pagination.items
            total_pages = pagination.pages
        else:
            items = query.all()
        return items, total_pages

    @classmethod
    def get(
        cls, item_id: int, include_serie=True, include_editions=False
    ) -> "CollectionModel":
        query = cls.query.filter_by(id=item_id)
        if include_serie:
            query = query.join(cls.serie).options(contains_eager(cls.serie))
        if include_editions:
            query = query.join(cls.editions, isouter=True).options(
                contains_eager(cls.editions)
            )
        item = query.one_or_none()
        return item
