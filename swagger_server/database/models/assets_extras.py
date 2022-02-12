from swagger_server.decorators.factory import factory
from sqlalchemy.sql import func
from dataclasses import dataclass
from swagger_server.database import db
from datetime import datetime
from swagger_server.database.models import BaseModel
import json


@dataclass
@factory
class AssetsExtras(BaseModel):
    """ """

    __tablename__ = "assets_extras"

    avatar_wearable_id: int = db.Column(db.Integer, primary_key=True)
    uuid: str = db.Column(db.String(100), nullable=False, unique=True)
    images: str = db.Column(db.String(16000000), nullable=False)
    videos: str = db.Column(db.String(16000000), nullable=False)

    created_at: datetime = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: datetime = db.Column(
        db.DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    def to_obj(
        self,
        format=True,
    ) -> "AssetsExtras":
        assets_extras = AssetsExtras(
            avatar_wearable_id=self.avatar_wearable_id,
            uuid=self.uuid,
            images=self.images,
            videos=self.videos,
        )
        return assets_extras

    def to_dict(self) -> dict:
        return {
            "avatar_wearable_id": self.avatar_wearable_id,
            "images": json.loads(self.images),
            "videos": json.loads(self.videos),
        }

    @classmethod
    def get(
        cls,
        item_id: int,
    ) -> "AssetsExtras":
        query = cls.query.filter_by(avatar_wearable_id=item_id)
        item = query.one_or_none()
        return item
