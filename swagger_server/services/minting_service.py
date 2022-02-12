"""minitng service module defines the MintingService class used to handle all
dapper interaction from the nft subsystem
"""

import math
from os import environ
from typing import Any, Tuple
from requests import Response
from swagger_server.exceptions import DapperException, InternalException
from swagger_server.graphql_schemas.queries import Query
from swagger_server.services.graphql_service import GraphQLService
from swagger_server.graphql_schemas.mutations.mutation import Mutation
from swagger_server.graphql_schemas.schemas import (
    EditionOnChainMetadataSchema,
    ImageVideosAndDescriptionMetadataSchema,
)
from swagger_server.graphql_schemas.mutations import (
    MintNftMutation,
    SellItemsMutation,
    UpdateCollectionMutation,
    AddCollectionMutation,
    UpdateEditionMutation,
    AddEditionsMutation,
    AdvanceSeriesMutation,
    UpsertDropMutation,
)
from swagger_server.database.models import (
    EditionModel,
    CollectionModel,
    SerieModel,
    DropModel,
)
from swagger_server.graphql_schemas.responses import (
    SuccessFlowIdResponse,
    MintNftResponse,
    SuccessDapperIdResponse,
)
from swagger_server.services.cms_service import CmsService
from swagger_server.threads import PublishEditionThread
from swagger_server.util import generate_uuid


class MintingService(GraphQLService):
    """MintingService layer used to handle all the connexions with the
    dapper minting api
    """

    api_url: str
    api_key: str
    temp_file_name: str = "video.mp4"
    __series_service: Any
    __editions_service: Any

    def __init__(
        self,
        cms: CmsService,
    ) -> None:
        self.cms = cms
        self.api_url = environ.get("DAPPER_URL")
        self.api_key = environ.get("DAPPER_API_KEY")

    def set_series_service(self, series_service):
        """Set the series service

        :param series_service: SeriesService
        """
        self.__series_service = series_service

    def set_editions_service(self, editions_service):
        """Set the editions service

        :param editions_service: EditionsService
        """
        self.__editions_service = editions_service

    def mutate(self, mutation: Mutation):
        """Execute a GraphQL mutation against Dapper's api

        :param mutation: Mutation
        """
        mutation_str = mutation.to_mutation()
        return self.exec(mutation_str)

    def query(self, query: Query) -> Response:
        """Execute a GraphQL query against Dapper's api

        :param query: Query
        """
        query_str = query.to_query()
        result = self.exec(query_str)
        return result

    def create_serie(
        self,
        serie: SerieModel,
    ) -> Tuple[bool, int]:
        """Create a new Series inside Dapper's system

        :param serie: SerieModel

        :return: Tuple[bool, int]
        """
        mutation = AdvanceSeriesMutation(
            name=serie.name,
            idempotency_key=serie.uuid,
            # description=serie.description, Commented due to changes in dapper api
        )
        result_json = self.mutate(mutation)
        result_dict = result_json["data"][mutation.mutation_name]
        success = self.success(result_dict["success"])
        response = SuccessFlowIdResponse(success, result_dict["flowID"])
        return success, response.flow_id

    def create_collection(
        self,
        collection: CollectionModel,
    ) -> Tuple[bool, int]:
        """Create a new Collection inside Dapper's system

        :param collection: CollectionModel

        :return: Tuple[bool, int]
        """
        serie = collection.serie
        mutation = AddCollectionMutation(
            name=collection.name,
            series_flow_id=serie.dapper_flow_id,
            idempotency_key=collection.uuid,
        )
        result_json = self.mutate(mutation)
        result_dict = result_json["data"][mutation.mutation_name]
        success = self.success(result_dict["success"])
        response = SuccessFlowIdResponse(
            success,
            result_dict["flowID"],
        )
        if success:
            success = self.update_collection(response.flow_id, collection)
        return success, response.flow_id

    def update_collection(
        self, collection_flow_id: int, collection: CollectionModel
    ) -> bool:
        """Update off chain metadata of an existing Collection in Dapper's system

        :param collection_flow_id: int
        :param collection: CollectionModel

        :return: bool
        """
        if not collection_flow_id:
            raise InternalException(
                title="The Collection must have a dapper_flow_id in order to update it"
            )
        mutation = UpdateCollectionMutation(
            collection_id=collection_flow_id,
            description=collection.description,
            idempotency_key=generate_uuid(),
        )
        result_json = self.mutate(mutation)
        result_dict = result_json["data"][mutation.mutation_name]
        success = self.success(result_dict["success"])
        return success

    def create_edition(self, edition: EditionModel) -> Tuple[bool, int]:
        """Create a new edition inside Dapper's system

        :param edition: EditionModel

        :return: Tuple[bool, int]
        """
        edition_on_chain_metadata = EditionOnChainMetadataSchema(
            rarity=edition.rarity,
            artist=edition.artist,
            celebrity=edition.celebrity,
            edition_type=edition.type,
            design_slot=edition.design_slot,
            publisher=edition.publisher,
            trademark=edition.trademark,
            avatar_wearable_sku=edition.avatar_wearable_sku,
        )
        mutation = AddEditionsMutation(
            name=edition.name,
            collection_id=edition.collection.dapper_flow_id,
            onchain_metadata=edition_on_chain_metadata,
            idempotency_key=edition.uuid,
        )
        result_json = self.mutate(mutation)
        result_dict = result_json["data"][mutation.mutation_name]
        success: bool = self.success(result_dict["success"])
        response = SuccessFlowIdResponse(success, result_dict["flowID"])
        if success:
            thread = PublishEditionThread(self, self.__editions_service)
            thread.start(edition.id, response.flow_id)
        return success, response.flow_id

    def update_edition(self, dapper_edition_id: str, edition: EditionModel) -> bool:
        """Update off chain metadata of an existing Edition's in Dapper's system

        :param dapper_edition_id: str
        :param edition: EditionModel

        :return: bool
        """
        if not dapper_edition_id:
            raise InternalException(
                title="The Edition must have a dapper_edition_id in order to update it"
            )
        edition_extra_data = edition.get_assets_extras()
        wearable: dict = (
            edition_extra_data.to_dict()
            if edition_extra_data
            else {"images": [], "videos": []}
        )
        metadata = ImageVideosAndDescriptionMetadataSchema(
            edition.description,
            wearable["images"],
            wearable["videos"],
        )
        mutation = UpdateEditionMutation(
            edition_id=dapper_edition_id,
            off_chain_metadata=metadata,
            idempotency_key=generate_uuid(),
        )
        result_json = self.mutate(mutation)
        result_dict = result_json["data"][mutation.mutation_name]
        success: bool = self.success(result_dict["success"])
        return success

    def create_drop(self, drop: DropModel) -> Tuple[bool, int]:
        """Create a new Drop inside Dapper's system

        :param drop: DropModel

        :return: Tuple[bool, int]
        """
        drop_editions = drop.drop_editions
        mutation = UpsertDropMutation(
            title=drop.title,
            description=drop.description,
            image_url=drop.image_url,
            drop_editions=drop_editions,
            start_time=drop.start_time,
            end_time=drop.end_time,
            idempotency_key=drop.uuid,
        )
        result_json = self.mutate(mutation)
        result_dict = result_json["data"][mutation.mutation_name]
        drop_id = result_dict["dropID"]
        response = SuccessDapperIdResponse(
            True,
            drop_id,
        )
        return response.status, response.dapper_id

    def update_drop(self, drop_flow_id: int, drop: DropModel) -> Tuple[bool, int]:
        """Update an existing Drop in Dapper's system

        :param drop_flow_id: int
        :param drop: DropModel

        :return: Tuple[bool, int]
        """
        drop_editions = drop.drop_editions
        mutation = UpsertDropMutation(
            id=drop_flow_id,
            title=drop.title,
            description=drop.description,
            image_url=drop.image_url,
            drop_editions=drop_editions,
            start_time=drop.start_time,
            end_time=drop.end_time,
            idempotency_key=generate_uuid(),
        )
        self.mutate(mutation)
        return True

    def mint(
        self, edition: EditionModel, quantity: int, reserved_percentage: int
    ) -> Tuple[bool, list, list]:
        """Mint NFTs through Dapper's API

        :param edition: EditionModel
        :param quantity: int
        :param reserved_percentage: int

        :return: Tuple[bool, list, list]
        """
        reserved_amount = int(math.ceil((reserved_percentage / 100) * quantity))
        mutation = MintNftMutation(
            edition_id=edition.dapper_flow_id,
            quantity=quantity,
            idempotency_key=generate_uuid(),
        )
        result_json = self.mutate(mutation)
        result_dict = result_json["data"][mutation.mutation_name]
        success = self.success(result_dict["success"])
        response = MintNftResponse(
            status=success,
            result=result_dict["mintedNFTs"],
            edition_id=edition.id,
        )
        return success, response.minted_nfts, reserved_amount

    def sell_items(
        self,
        minted_nfts: list,
        edition: EditionModel,
    ) -> bool:
        """Put items on sale in Dapper's store

        :param minted_nfts: list
        :param edition: EditionModel

        :return: bool
        """

        def get_nft_ids(nft: dict) -> int:
            return nft["nftFlowID"]

        minted_list: list = list(map(get_nft_ids, minted_nfts))
        mutation = SellItemsMutation(
            nft_name=edition.name,
            nft_storage_name=environ.get("NFT_STORAGE_NAME"),
            nft_flow_ids=minted_list,
            ft_name=environ.get("FT_NAME"),
            ft_storage_name=environ.get("FT_STORAGE_NAME"),
            price=edition.price,
            idempotency_key=generate_uuid(),
        )
        result_json = self.mutate(mutation)
        result_dict = result_json["data"][mutation.mutation_name]
        success = self.success(result_dict["success"])
        return success
