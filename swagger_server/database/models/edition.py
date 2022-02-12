from swagger_server.models.update_edition import UpdateEdition
from swagger_server.decorators.factory import factory
from typing import List, Tuple
from swagger_server.util import (
    delete_empty_keys,
    format_datetime,
    format_price,
    to_listable_model,
    get_order_by,
)
from sqlalchemy.orm import contains_eager, relationship, subqueryload
from sqlalchemy.sql import func
from dataclasses import dataclass
from swagger_server.models import (
    CollectionListable,
    CreateEdition,
    Edition,
    EditionOffChainMetadata,
    EditionOnChainMetadata,
)
from swagger_server.database.models import (
    BaseModel,
    CollectionModel,
    AssetsExtras,
)
from swagger_server.database.models.drop_edition import DropEditionModel
from swagger_server.database.models.nft import NftModel
from swagger_server.__main__ import db
from swagger_server.database.enums import (
    EditionRarity,
    EditionStatus,
    EditionType,
    DesignSlot,
)
from datetime import datetime
from decimal import Decimal
import math


@dataclass
@factory
class EditionModel(BaseModel):
    """
    EditionModel: DAO used in conjunction with the Edition model.

    :parent: BaseModel

    Attributes:
        id (int)
        name (str)
        description (str)
        artist (str)
        avatar_wearable_sku (sku)   The SKU of the wearable associated
        celebrity(str)              The celebrity name
        design_slot (DesignSlot)    The slot where the wearable will be used
        publisher (str)
        rarity (EditionRarity)
        trademark (str)
        type (EditionType)
        price (decimal)
        reserve_percentage (int)    The percentage that the user will like to
                                    reserve at the moment of selling
        status (EditionStatus)
        publish_time (datetime)
        created_at (datetime)
        updated_at (datetime)
        avatar_wearable_id (int)    The id of the associated wearable in the CMS
        dapper_flow_id (int)        The flow id of the Edition assigned by Dapper.
        dapper_edition_id (int)     The id of the Edition in Dapper database.
        collection_id (int)         The id of the associated Collection
        uuid (str)                  The uuid of the Edition
    """

    __tablename__ = "editions"
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    description: str = db.Column(db.Text, nullable=True)
    artist: str = db.Column(db.String(100), nullable=True)
    avatar_wearable_sku: str = db.Column(db.String(100), nullable=False)
    celebrity: str = db.Column(db.String(100), nullable=True)
    design_slot: DesignSlot = db.Column(db.Enum(DesignSlot), nullable=True)
    publisher: str = db.Column(db.String(100), nullable=True)
    rarity: EditionRarity = db.Column(db.Enum(EditionRarity), nullable=True)
    trademark: str = db.Column(db.String(100), nullable=True)
    type: EditionType = db.Column(
        db.Enum(EditionType),
        nullable=True,
        default=EditionType.EDITION_TYPE_AVATAR_WEARABLE,
    )
    price: Decimal = db.Column(db.Numeric(precision=20, scale=2), nullable=True)
    reserve_percentage: int = db.Column(db.Integer, nullable=True)
    status: EditionStatus = db.Column(db.Enum(EditionStatus), nullable=False)
    publish_time: datetime = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: datetime = db.Column(
        db.DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    avatar_wearable_id: int = db.Column(db.Integer, nullable=False)
    dapper_flow_id: int = db.Column(db.Integer, nullable=True)
    dapper_edition_id: str = db.Column(db.String(100), nullable=True)
    collection_id: int = db.Column(
        db.Integer, db.ForeignKey("collections.id"), nullable=False
    )
    collection = relationship("CollectionModel", back_populates="editions")
    drop_editions = relationship("DropEditionModel")
    errors = relationship("EditionErrorModel")
    nfts = relationship("NftModel")
    nfts_minted: int = db.column_property(
        db.select(func.count(NftModel.id))
        .where(NftModel.edition_id == id)
        .correlate_except(NftModel)
        .scalar_subquery()
    )
    nfts_for_sale: int = db.column_property(
        nfts_minted * (100 - reserve_percentage) / 100
    )
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)

    def to_obj(
        self,
        include_collection=True,
        include_drops=False,
        include_nfts=False,
        format=True,
    ) -> "Edition":
        collection = None
        drop_editions = []
        nfts = []
        if include_collection:
            collection = to_listable_model(
                self.collection.to_obj(include_serie=False, format=format),
                CollectionListable,
            )
        if include_drops:
            for drop_edition in self.drop_editions:
                drop_editions.append(
                    drop_edition.to_obj(
                        include_drop=True, include_edition=False, format=format
                    )
                )
        if include_nfts:
            for nft in self.nfts:
                nfts.append(nft.to_obj())

        off_chain_metadata = EditionOffChainMetadata(description=self.description)

        on_chain_metadata = EditionOnChainMetadata(
            artist=self.artist,
            avatar_wearable_sku=self.avatar_wearable_sku,
            celebrity=self.celebrity,
            design_slot=self.design_slot.value if self.design_slot else None,
            publisher=self.publisher,
            rarity=self.rarity.value if self.rarity else None,
            trademark=self.trademark,
            type=self.type.value if self.type else None,
        )

        edition = Edition(
            id=self.id,
            name=self.name.strip(),
            off_chain_metadata=off_chain_metadata,
            on_chain_metadata=on_chain_metadata,
            price=format_price(self.price, format),
            reserve_percentage="{percentage}% ({qty})".format(
                percentage=self.reserve_percentage,
                qty=int(self.nfts_minted - self.nfts_for_sale)
                if self.nfts_minted and self.nfts_for_sale
                else 0,
            )
            if format
            else self.reserve_percentage,
            status=self.status.value,
            publish_time=format_datetime(self.publish_time, format),
            avatar_wearable_id=self.avatar_wearable_id,
            collection=collection,
            drop_editions=drop_editions,
            nfts=nfts,
            nfts_minted=self.nfts_minted,
            nfts_for_sale=math.ceil(self.nfts_for_sale) if self.nfts_for_sale else 0,
        )

        return edition

    @classmethod
    def from_obj(cls, obj: CreateEdition or UpdateEdition) -> "EditionModel":
        return cls(
            id=getattr(obj, "id", None),
            name=obj.name.strip() if obj.name else None,
            description=getattr(obj.off_chain_metadata, "description", None),
            artist=getattr(obj.on_chain_metadata, "artist", None),
            avatar_wearable_sku=getattr(
                obj.on_chain_metadata, "avatar_wearable_sku", None
            ),
            celebrity=getattr(obj.on_chain_metadata, "celebrity", None),
            design_slot=getattr(obj.on_chain_metadata, "design_slot", None),
            publisher=getattr(obj.on_chain_metadata, "publisher", None),
            rarity=getattr(obj.on_chain_metadata, "rarity", None),
            trademark=getattr(obj.on_chain_metadata, "trademark", None),
            type=getattr(obj.on_chain_metadata, "type", None),
            price=obj.price,
            reserve_percentage=obj.reserve_percentage,
            status=getattr(obj, "status", None),
            publish_time=obj.publish_time,
            avatar_wearable_id=obj.avatar_wearable_id,
            dapper_flow_id=getattr(obj, "dapper_flow_id", None),
            dapper_edition_id=getattr(obj, "dapper_edition_id", None),
            collection_id=getattr(obj, "collection_id", None),
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
    ) -> Tuple[List["CollectionModel"], int]:
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
            if "available" in filters.keys():
                edition_ids_in_drops = db.session.query(
                    DropEditionModel.edition_id
                ).distinct(DropEditionModel.edition_id)
                if filters["available"]:
                    # This should be ON_SALE
                    query = query.filter_by(status=EditionStatus.MINTED).filter(
                        cls.id.not_in(edition_ids_in_drops)
                    )
                else:
                    query = query.filter(cls.id.in_(edition_ids_in_drops))
            if "rarity" in filters.keys():
                query = query.filter_by(rarity=filters["rarity"])
            if "type" in filters.keys():
                query = query.filter_by(type=filters["type"])
            if "design_slot" in filters.keys():
                query = query.filter_by(design_slot=filters["design_slot"])
            if "min_price" in filters.keys():
                query = query.filter(cls.price >= filters["min_price"])
            if "max_price" in filters.keys():
                query = query.filter(cls.price <= filters["max_price"])
            if "avatar_wearable_id" in filters.keys():
                query = query.filter_by(
                    avatar_wearable_id=filters["avatar_wearable_id"]
                )
        if keyword:
            query = query.filter(
                db.or_(
                    cls.name.like("%" + keyword + "%"),
                    cls.artist.like("%" + keyword + "%"),
                    cls.celebrity.like("%" + keyword + "%"),
                    cls.publisher.like("%" + keyword + "%"),
                    cls.trademark.like("%" + keyword + "%"),
                    cls.avatar_wearable_sku.like("%" + keyword + "%"),
                )
            )
        items: List[EditionModel]
        total_pages: int = 1
        if page and page_size:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            items = pagination.items
            total_pages = pagination.pages
        else:
            items = query.all()
        return items, total_pages

    @classmethod
    def filter_query(
        cls,
        query,
        include_collection=True,
        include_drops=False,
        include_nfts=False,
    ):
        if include_collection:
            query = query.join(cls.collection).options(contains_eager(cls.collection))
        if include_drops:
            query = query.options(
                subqueryload(cls.drop_editions).subqueryload(DropEditionModel.drop)
            )
        if include_nfts:
            query = query.join(cls.nfts, isouter=True).options(contains_eager(cls.nfts))
        return query

    @classmethod
    def get(
        cls,
        id: int,
        include_collection=True,
        include_drops=False,
        include_nfts=False,
    ) -> "EditionModel":
        query = cls.query.filter_by(id=id)
        query = cls.filter_query(query, include_collection, include_drops, include_nfts)
        item = query.one_or_none()
        return item

    @classmethod
    def get_by_dapper_edition_id(
        cls,
        dapper_edition_id: int,
        include_collection=True,
        include_drops=False,
        include_nfts=False,
    ) -> "EditionModel":
        query = cls.query.filter_by(dapper_edition_id=dapper_edition_id)
        query = cls.filter_query(query, include_collection, include_drops, include_nfts)
        item = query.one_or_none()
        return item

    def get_assets_extras(
        self,
    ) -> AssetsExtras:
        return AssetsExtras.get(self.avatar_wearable_id)
