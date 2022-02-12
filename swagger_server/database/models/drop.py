from datetime import datetime
from decimal import Decimal
from swagger_server.database.models.edition import EditionModel
from swagger_server.database.models.drop_edition import DropEditionModel
from swagger_server.decorators.factory import factory
from swagger_server.models.update_drop import UpdateDrop
from swagger_server.models.edition_listable import EditionListable
from typing import List
from swagger_server.models.create_drop import CreateDrop
from swagger_server.util import (
    delete_empty_keys,
    format_datetime,
    get_order_by,
)
from sqlalchemy.orm import contains_eager, relationship, subqueryload
from sqlalchemy.sql import func
from swagger_server.models import Drop
from swagger_server.database.models.base_model import BaseModel
from swagger_server.__main__ import db
from dataclasses import dataclass
from swagger_server.database.enums import DropStatus


@dataclass
@factory
class DropModel(BaseModel):
    """
    DropModel: DAO used in conjunction with the Drop model.

    :parent: BaseModel

    Attributes:
        id (int)
        title (str)
        description (str)
        image_url (str)
        status (Status)
        start_time (datetime)
        end_time (datetime)
        created_at (datetime)
        updated_at (datetime)
        publish_time (datetime)
        dapper_drop_id (string)        The flow id of the Drop asigned by Dapper
        editions_quantity (int)     The amount of Editions in the Drop
        uuid (str)                  The uuid of the drop
    """

    __tablename__ = "drops"
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(100), nullable=False)
    description: str = db.Column(db.Text, nullable=True)
    image_url: str = db.Column(db.String(255), nullable=True)
    status: DropStatus = db.Column(db.Enum(DropStatus), nullable=False)
    start_time: datetime = db.Column(db.DateTime, nullable=True)
    end_time: datetime = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    publish_time: datetime = db.Column(db.DateTime, nullable=True)
    dapper_drop_id: int = db.Column(db.String(100), nullable=True)
    drop_editions = relationship("DropEditionModel", cascade="delete")
    editions_quantity: int = db.column_property(
        db.select(func.count(DropEditionModel.drop_id))
        .where(DropEditionModel.drop_id == id)
        .correlate_except(DropEditionModel)
        .scalar_subquery()
    )
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)

    def to_obj(self, include_editions=False, format=True) -> "Drop":
        drop_editions = []
        if include_editions:
            for drop_edition in self.drop_editions:
                drop_editions.append(
                    drop_edition.to_obj(
                        include_drop=False, include_edition=True, format=format
                    )
                )
        drop = Drop(
            id=self.id,
            title=self.title.strip(),
            description=self.description,
            image_url=self.image_url,
            status=self.status.value,
            start_time=format_datetime(self.start_time, format),
            end_time=format_datetime(self.end_time, format),
            publish_time=format_datetime(self.publish_time, format),
            drop_editions=drop_editions,
            editions_quantity=self.editions_quantity,
        )
        return drop

    @classmethod
    def from_obj(cls, obj: CreateDrop or UpdateDrop) -> "DropModel":
        return cls(
            id=getattr(obj, "id", None),
            title=obj.title.strip() if obj.title else None,
            description=obj.description,
            image_url=getattr(obj, "image_url", None),
            status=getattr(obj, "status", None),
            start_time=obj.start_time,
            end_time=obj.end_time,
            publish_time=obj.publish_time,
            dapper_drop_id=getattr(obj, "dapper_drop_id", None),
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
    ) -> List["DropModel"]:
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
            query = query.filter(cls.title.like("%" + keyword + "%"))
        items: List[DropModel]
        total_pages: int = 1
        if page and page_size:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            items = pagination.items
            total_pages = pagination.pages
        else:
            items: List[DropModel] = query.all()
        return items, total_pages

    @classmethod
    def get(cls, item_id: int, include_editions=False) -> "DropModel":
        query = cls.query.filter_by(id=item_id)
        if include_editions:
            query = query.options(
                subqueryload(cls.drop_editions).subqueryload(DropEditionModel.edition)
            )
        item = query.one_or_none()
        return item
