from typing import List
import random
from swagger_server.database.models import NftModel, EditionModel
from sqlalchemy.exc import IntegrityError
from swagger_server.util import generate_uuid
from swagger_server.models import ListNfts
from swagger_server.models.nft import Nft
from typing import Tuple


class NftService:
    """Service that contains the bussiness logic to list, create, get all nfts"""

    def __init__(self) -> None:
        pass

    def get_reserved_index_list(
        self,
        minted_nfts: list,
        reserved_amount: float,
    ) -> list:
        """Get the reserved index list"""
        total: int = len(minted_nfts)
        return random.sample(range(0, total), reserved_amount)

    def list_nfts(
        self, filters: dict, keyword: str, page: int, page_size: int
    ) -> ListNfts:
        """Lists all the Nfts that match the filters and keyword

        :param filters: dict
        :param keyword: str
        :param page: int
        :param page_size: int

        :return: ListNfts
        """
        nft_models: List[NftModel]
        total_pages: int
        nft_models, total_pages = NftModel.get_all(filters, keyword, page, page_size)
        nfts: List[Nft] = []
        for nft_model in nft_models:
            nfts.append(nft_model.to_obj())
        return ListNfts(nfts=nfts, total_pages=total_pages)

    def create_nft(
        self, edition_id: int, dapper_flow_id: int, reserved: bool = False
    ) -> NftModel:
        """Creates a new NFT

        :param edition_id: int
        :param dapper_flow_id: int
        :param reserved: bool

        :return: Nft
        """
        nft_model = NftModel()
        nft_model.edition_id = edition_id
        nft_model.dapper_flow_id = dapper_flow_id
        nft_model.reserved = reserved
        nft_model.uuid = generate_uuid()
        try:
            nft_model.add()
            nft_model.commit()
        except IntegrityError as error:
            nft_model.rollback()
        return nft_model.to_obj()

    def bulk_create_nft(
        self,
        minted_nfts: list,
        reserved: list,
        edition: EditionModel,
    ) -> Tuple[list, list]:
        """Persist the nft minted in the database

        :param minted_nfts: list
        :param reserved: int
        :param edition: EditionModel
        """
        reserved_nft_list: list = []
        nft_list: list = []
        for index, minted in enumerate(minted_nfts):
            nft_dict: dict = {
                "edition_id": edition.id,
                "dapper_flow_id": minted["nftFlowID"],
            }
            if index in reserved:
                nft_dict["reserved"] = True
                reserved_nft_list.append(self.create_nft(**nft_dict))
            else:
                nft_list.append(self.create_nft(**nft_dict))
        return (nft_list, reserved_nft_list)
