import random
from dataclasses import dataclass
from swagger_server.database.models import NftModel
from swagger_server.services import nft_service


@dataclass
class MintNftResponse:

    status: bool
    minted_nfts: list
    edition_id: int

    def __init__(self, status: bool, result: list, edition_id: int):
        self.status = status
        self.minted_nfts = result
        self.edition_id = edition_id
