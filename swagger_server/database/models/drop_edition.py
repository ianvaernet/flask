from swagger_server.decorators.factory import factory
from swagger_server.util import to_listable_model
from sqlalchemy.orm import contains_eager, relationship
from swagger_server.models import (
    CreateOrUpdateDropEdition,
    DropEdition,
    DropListable,
    EditionListable,
)
from swagger_server.database.models.base_model import BaseModel
from swagger_server.__main__ import db
from dataclasses import dataclass
from swagger_server.util import format_price


@dataclass
@factory
class DropEditionModel(BaseModel):
    """
    DropEditionModel: DAO used in conjunction with the DropEdition model for the many-to-many relationship between Drop and Edition.

    :parent: BaseModel

    Attributes:
        drop_id (int)       The id of the Drop
        edition_id (int)    The id of the Edition that will be part of the Drop
        price (float)       The price of the Edition in the Drop
        uuid (str) The uuid of the drop edition
    """

    __tablename__ = "drop_editions"
    drop_id: int = db.Column(db.Integer, db.ForeignKey("drops.id"), primary_key=True)
    edition_id: int = db.Column(
        db.Integer, db.ForeignKey("editions.id"), primary_key=True
    )
    price: float = db.Column(db.Float, nullable=False)
    drop = relationship("DropModel", back_populates="drop_editions")
    edition = relationship("EditionModel", back_populates="drop_editions")
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)

    def to_obj(
        self, include_drop=True, include_edition=True, format=False
    ) -> "DropEdition":
        drop = None
        edition = None
        if include_drop:
            drop = to_listable_model(
                self.drop.to_obj(include_editions=False, format=format),
                DropListable,
            )
        if include_edition:
            edition = to_listable_model(
                self.edition.to_obj(
                    include_collection=False, include_drops=False, format=format
                ),
                EditionListable,
            )
        drop_edition = DropEdition(
            drop=drop,
            edition=edition,
            price=format_price(self.price, format),
        )
        return drop_edition

    @classmethod
    def from_obj(cls, obj: CreateOrUpdateDropEdition) -> "DropEditionModel":
        return cls(
            drop_id=obj.drop_id,
            edition_id=obj.edition_id,
            price=obj.price,
        )

    @classmethod
    def get(
        cls,
        drop_id: int,
        edition_id: int,
        include_drop: bool = True,
        include_edition: bool = True,
    ) -> "DropEditionModel":
        query = cls.query.filter_by(drop_id=drop_id, edition_id=edition_id)
        if include_drop:
            query = query.join(cls.drop).options(contains_eager(cls.drop))
        if include_edition:
            query = query.join(cls.edition).options(contains_eager(cls.edition))
        item = query.one_or_none()
        return item
