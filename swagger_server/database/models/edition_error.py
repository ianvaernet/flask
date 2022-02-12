from swagger_server.decorators.factory import factory
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from dataclasses import dataclass
from swagger_server.database.models import BaseModel
from swagger_server.__main__ import db
from datetime import datetime
from swagger_server.models import EditionError
from swagger_server.util import delete_empty_keys, format_datetime


@dataclass
@factory
class EditionErrorModel(BaseModel):
    """
    EditionErrorModel: DAO used in conjunction with the Edition Error model.

    :parent: BaseModel

    Attributes:
        id (int)
        edition_id (int)
        type (str)
        error (str)
        created_at (datetime)
        updated_at (datetime)
    """

    __tablename__ = "editions_errors"
    id: int = db.Column(db.Integer, primary_key=True)
    edition_id: int = db.Column(
        db.Integer, db.ForeignKey("editions.id"), nullable=False
    )
    type: str = db.Column(db.String(100), nullable=True)
    error: str = db.Column(db.Text, nullable=False)
    suggested_solution: str = db.Column(db.String(500), nullable=True)
    edition = relationship("EditionModel", back_populates="errors")
    created_at: datetime = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    def to_obj(
        self,
    ) -> "EditionError":
        error = EditionError(
            id=self.id,
            edition_id=self.edition_id,
            error_date=format_datetime(self.created_at),
            type=self.type,
            error=self.error,
            suggested_solution=self.suggested_solution,
        )

        return error

    @classmethod
    def get(
        cls,
        id: int,
    ) -> "EditionErrorModel":
        query = cls.query.filter_by(id=id)
        item = query.one_or_none()
        return item

    @classmethod
    def get_all(
        cls, filters: dict = {}, page: int = 0, page_size: int = 0
    ) -> "EditionErrorModel":
        filters = delete_empty_keys(filters)
        query = cls.query.order_by(cls.created_at.desc())
        total_pages: int = 1
        if filters:
            if "edition_id" in filters.keys():
                query = query.filter_by(edition_id=filters["edition_id"])
        if page and page_size:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            items = pagination.items
            total_pages = pagination.pages
        else:
            items = query.all()
        return items, total_pages
