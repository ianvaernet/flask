from sqlalchemy.orm import contains_eager, relationship
from swagger_server.database.enums import NftStatus
from swagger_server.decorators.factory import factory
from swagger_server.models import Nft
from swagger_server.database.models import BaseModel, CollectionModel, SerieModel
from swagger_server.__main__ import db
from dataclasses import dataclass
from swagger_server.util import delete_empty_keys


@dataclass
@factory
class NftModel(BaseModel):
    """
    NftModel: DAO used in conjunction with the Nft model.

    :parent: BaseModel

    Attributes:
        id (int)
        reserved (bool)
        status (NftStatus)
        dapper_flow_id (int)        The flow id of the NFT asigned by Dapper
        edition_id (int)            The id of the associated Edition
        uuid (str)                  The uuid of the NFT
    """

    __tablename__ = "nfts"
    id: int = db.Column(db.Integer, primary_key=True)
    reserved: bool = db.Column(db.Boolean, nullable=False, default=False)
    status: NftStatus = db.Column(
        db.Enum(NftStatus), nullable=False, default=NftStatus.MINTED
    )
    dapper_flow_id: int = db.Column(db.Integer, nullable=True)
    edition_id: str = db.Column(
        db.Integer, db.ForeignKey("editions.id"), nullable=False
    )
    edition = relationship("EditionModel", back_populates="nfts")
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)

    def to_obj(self) -> "Nft":
        nft = Nft(
            id=self.id,
            reserved=self.reserved,
            status=self.status.value,
            serial_number=self.dapper_flow_id,
            edition_name=self.edition.name,
            avatar_wearable_sku=self.edition.avatar_wearable_sku,
        )
        return nft

    @classmethod
    def from_obj(cls, obj: Nft) -> "NftModel":
        return cls(
            id=getattr(obj, "id", None),
            reserved=obj.reserved,
            status=obj.status,
            dapper_flow_id=obj.dapper_flow_id,
            edition_id=obj.edition_id,
        )

    @classmethod
    def get_all(
        cls, filters: dict = {}, keyword: str = "", page: int = 0, page_size: int = 0
    ):
        from swagger_server.database.models.edition import EditionModel

        filters = delete_empty_keys(filters)
        query = (
            cls.query.join(cls.edition)
            .join(EditionModel.collection)
            .join(CollectionModel.serie)
            .options(
                contains_eager(cls.edition)
                .load_only(
                    EditionModel.name,
                    EditionModel.rarity,
                    EditionModel.avatar_wearable_sku,
                )
                .contains_eager(EditionModel.collection)
                .load_only(CollectionModel.name, CollectionModel.short_word)
                .contains_eager(CollectionModel.serie)
                .load_only(SerieModel.name, SerieModel.short_word)
            )
        )
        if filters:
            if "status" in filters.keys():
                if len(filters["status"]) > 1:
                    status_filters = []
                    for status in filters["status"]:
                        status_filters.append(cls.status == status)
                    query = query.filter(db.or_(*status_filters))
                else:
                    query = query.filter(cls.status == filters["status"][0])
            if "reserved" in filters.keys():
                query = query.filter(cls.reserved == filters["reserved"])
            if "rarity" in filters.keys():
                query = query.filter(EditionModel.rarity == filters["rarity"])
            if "collection_id" in filters.keys():
                query = query.filter(CollectionModel.id == filters["collection_id"])
            if "serie_id" in filters.keys():
                query = query.filter(SerieModel.id == filters["serie_id"])
        if keyword:
            query = query.filter(
                db.or_(
                    cls.dapper_flow_id.like("%" + keyword + "%"),
                    EditionModel.name.like("%" + keyword + "%"),
                    CollectionModel.name.like("%" + keyword + "%"),
                    CollectionModel.short_word.like("%" + keyword + "%"),
                    SerieModel.name.like("%" + keyword + "%"),
                    SerieModel.short_word.like("%" + keyword + "%"),
                )
            )
        items: list[NftModel]
        total_pages: int = 1
        if page and page_size:
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            items = pagination.items
            total_pages = pagination.pages
        else:
            items = query.all()
        return items, total_pages
