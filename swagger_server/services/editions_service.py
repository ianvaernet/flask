import json
import os
from datetime import datetime
from swagger_server.database.models import (
    SerieModel,
    CollectionModel,
    EditionModel,
    AssetsExtras,
    EditionErrorModel,
)
from swagger_server.database.enums import CollectionStatus, EditionStatus
from swagger_server.models import (
    BatchUpdateEditions,
    Collection,
    EditionError,
)
from swagger_server.models.enums import Entity
from swagger_server.util import (
    publish_time_is_updated,
    validate_price,
    validate_required_fields,
    generate_uuid,
    validate_update,
)
from swagger_server.exceptions import (
    ConflictException,
    EditionNotFoundException,
    ForbiddenException,
    BadRequestException,
    EditionEnumerationValidationException,
)
from typing import Any, List, Tuple
from swagger_server.services.cms_service import CmsService
from swagger_server.services.scheduler_service import SchedulerService
from swagger_server.services import MintingService, NftService, DataDefinitionsService


class EditionsService:
    """Service that contains the bussiness logic to list, create, get, update, delete, publish, mint and sell Editions"""

    __cms_service: CmsService
    __collections_service: Any
    __series_service: Any
    __minting_service: MintingService
    __nft_service: NftService
    __data_definition_service: DataDefinitionsService
    __scheduler_service: SchedulerService

    def __init__(
        self,
        cms_service: CmsService,
        collections_service,
        series_service,
        minting_service: MintingService,
        nft_service: NftService,
        data_definition_service: DataDefinitionsService,
        scheduler_service: SchedulerService,
    ) -> None:
        self.__cms_service = cms_service
        self.__collections_service = collections_service
        self.__series_service = series_service
        self.__minting_service = minting_service
        self.__nft_service = nft_service
        self.__data_definition_service = data_definition_service
        self.__scheduler_service = scheduler_service

    def list_editions(
        self,
        filters: dict = None,
        keyword: str = None,
        page: int = None,
        page_size: int = None,
        order: str = "desc",
        order_by: str = "created_at",
    ) -> Tuple[List[EditionModel], int]:
        """Lists all the Editions that match the filters and keyword

        :param filters: dict
        :param keyword: str
        :param page: int
        :param page_size: int
        :param order: str
        :param order_by: str

        :return: Tuple[List[EditionModel], int]
        """
        edition_models: List[EditionModel]
        total_pages: int
        edition_models, total_pages = EditionModel.get_all(
            filters, keyword, page, page_size, order, order_by
        )
        return edition_models, total_pages

    def __update_publish_extra_data(
        self,
        files: List[str],
        avatar_wearable_id: int,
    ):
        """
        Update publish extra data

        :param files: list[str]
        :param avatar_wearable_id: int

        :return: None
        """
        wearable_videos: list[str] = os.getenv("WEARABLE_VIDEOS").split(",")
        wearable_images: list[str] = os.getenv("WEARABLE_IMAGES").split(",")
        images: list[str] = []
        videos: list[str] = []
        for file in files:
            file_name = file.split("/")[-1]
            if file_name in wearable_images:
                images.append(file)
            elif file_name in wearable_videos:
                videos.append(file)

        values: dict = {
            "avatar_wearable_id": avatar_wearable_id,
            "images": json.dumps(images),
            "videos": json.dumps(videos),
            "uuid": generate_uuid(),
        }
        new_extra_data: AssetsExtras = AssetsExtras(**values)
        assets_extras: AssetsExtras = AssetsExtras.get(avatar_wearable_id)
        if not assets_extras:
            new_extra_data.add()
        else:
            assets_extras.update(new_extra_data)

    def __validate_edition_enumeration(self, edition: EditionModel) -> None:
        """Validates the edition enumeration

        :param edition: EditionModel

        :return: None
        """
        enumerations: dict = self.__data_definition_service.get_enumerations()
        design_slots: list = enumerations["EDITION_DESIGN_SLOT"]
        types: list = enumerations["EDITION_TYPE"]
        rarities: list = enumerations["EDITION_RARITY"]
        if edition.design_slot and edition.design_slot not in design_slots:
            raise EditionEnumerationValidationException(
                title="Invalid DESIGN SLOT",
                detail=f"Invalid DESIGN_SLOT={edition.design_slot}. Valid ones={design_slots}",
            )

        if edition.type and edition.type not in types:
            raise EditionEnumerationValidationException(
                title="Invalid TYPE",
                detail=f"Invalid TYPE={edition.type}. Valid ones={types}",
            )

        if edition.rarity and edition.rarity not in rarities:
            raise EditionEnumerationValidationException(
                title="Invalid RARITY",
                detail=f"Invalid RARITY={edition.rarity}. Valid ones={rarities}",
            )

    def create_edition(self, new_edition: EditionModel) -> None:
        """Creates a new Edition

        :param new_edition: EditionModel

        :return: None
        """
        self.__validate_edition_enumeration(new_edition)
        asset = self.__cms_service.get_wearable_data(new_edition.avatar_wearable_id)
        new_edition.status = EditionStatus.DRAFT
        new_edition.avatar_wearable_sku = asset["sku"]
        new_edition.collection_id = asset["collection_id"]
        new_edition.uuid = generate_uuid()
        validate_price(new_edition.price)
        self.__validate_publish_time(new_edition)
        new_edition.add()
        self.__update_publish_extra_data(
            files=asset["file_list"],
            avatar_wearable_id=new_edition.avatar_wearable_id,
        )
        new_edition.flush()
        if publish_time_is_updated(new_edition):
            self.__create_or_update_publish_job(new_edition)

    def get_edition(
        self,
        id: int,
        include_collection: bool = True,
        include_drops: bool = False,
        include_nfts: bool = False,
    ) -> EditionModel:
        """Gets a single Edition by its id

        :param id: int
        :param include_collection: bool
        :param include_drops: bool
        :param include_nfts: bool

        :return: EditionModel
        """
        edition_model: EditionModel = EditionModel.get(
            id,
            include_collection=include_collection,
            include_drops=include_drops,
            include_nfts=include_nfts,
        )
        if not edition_model:
            raise EditionNotFoundException(id)
        return edition_model

    def update_edition(
        self,
        id: int,
        updated_edition: EditionModel,
    ) -> Tuple[EditionModel, str]:
        """Updates an Edition by its id

        :param id: int
        :param updated_edition: EditionModel

        :return: Tuple[EditionModel, str]
        """
        message = ""
        publish_time_was_updated = False
        current_edition: EditionModel = self.get_edition(id)
        validate_price(updated_edition.price)
        if (
            current_edition.status == EditionStatus.DRAFT
            or current_edition.status == EditionStatus.ERROR
        ):
            if (
                updated_edition.avatar_wearable_id
                and updated_edition.avatar_wearable_id
                != current_edition.avatar_wearable_id
            ):
                asset = self.__cms_service.get_wearable_data(
                    updated_edition.avatar_wearable_id
                )
                self.__update_publish_extra_data(
                    files=asset["file_list"],
                    avatar_wearable_id=updated_edition.avatar_wearable_id,
                )
                updated_edition.avatar_wearable_sku = asset["sku"]
                updated_edition.collection_id = asset["collection_id"]
            self.__validate_publish_time(updated_edition, current_edition)
            publish_time_was_updated = (
                not updated_edition.dapper_flow_id
                and publish_time_is_updated(updated_edition, current_edition)
            )
            self.__validate_edition_enumeration(updated_edition)
        else:
            if (
                current_edition.status == EditionStatus.CREATING
                and not updated_edition.dapper_edition_id
            ):
                raise BadRequestException(
                    "The Edition is being created",
                    "The Edition cannot be updated during its creation",
                )
            tried_to_update_on_chain_data = validate_update(
                original_model=current_edition,
                updated_model=updated_edition,
                not_updateable_fields=[
                    "name",
                    "publish_time",
                    "avatar_wearable_id",
                    "artist",
                    "avatar_wearable_sku",
                    "celebrity",
                    "design_slot",
                    "publisher",
                    "rarity",
                    "trademark",
                    "type",
                ],
            )
            if tried_to_update_on_chain_data:
                message += "The name, publish_time, avatar_wearable_id and on_chain_metadata cannot be updated because the Edition has already been published. "
            if current_edition.status == EditionStatus.ON_SALE:
                tried_to_update_sale_data = validate_update(
                    original_model=current_edition,
                    updated_model=updated_edition,
                    not_updateable_fields=["price", "reserve_percentage"],
                )
                if tried_to_update_sale_data:
                    message += "The price and reserve_percentage cannot be updated because the Edition is already on sale."
            if (
                updated_edition.description
                and updated_edition.description != current_edition.description
            ):
                self.__minting_service.update_edition(
                    current_edition.dapper_edition_id, updated_edition
                )
        current_edition.update(updated_edition)
        if publish_time_was_updated:
            self.__create_or_update_publish_job(current_edition)
        return current_edition, message

    def batch_update_editions(self, batch_update_editions: BatchUpdateEditions) -> str:
        """Batch update Editions by avatar_wearable_id

        :return: str
        """
        editions: list[EditionModel] = self.list_editions(
            filters={"avatar_wearable_id": batch_update_editions.avatar_wearable_id}
        )[0]
        collection: CollectionModel = self.__collections_service.get_collection(
            batch_update_editions.collection_id, include_serie=False
        )
        files: list[str] = batch_update_editions.file_list
        self.__update_publish_extra_data(
            files,
            avatar_wearable_id=batch_update_editions.avatar_wearable_id,
        )

        updated_editions = 0
        if len(editions) > 0 and editions[0].collection_id != collection.id:
            self.__collections_service.update_collection(
                editions[0].collection_id,
                CollectionModel(),
                wearables_count_difference=-1,
            )
            self.__collections_service.update_collection(
                collection.id, CollectionModel(), wearables_count_difference=1
            )
        for edition in editions:
            if (
                edition.status != EditionStatus.DRAFT
                and edition.status != EditionStatus.ERROR
            ):
                raise ForbiddenException(
                    "Editions already published",
                    "There are Editions with that avatar_wearable_id that have already been published",
                )
            updated_editions += 1
            updated_edition = EditionModel(
                avatar_wearable_sku=edition.avatar_wearable_sku,
                collection_id=batch_update_editions.collection_id,
            )
            self.update_avatar_wearable_sku(
                updated_edition, Entity.COLLECTION, collection.short_word
            )
            self.update_avatar_wearable_sku(
                updated_edition, Entity.ASSET, batch_update_editions.short_word
            )
            self.update_edition(edition.id, updated_edition)
        return f"{updated_editions} editions successfully updated"

    def delete_edition(self, id: int) -> None:
        """Deletes an Edition by its id

        :param id: int

        :return: None
        """
        edition_model: EditionModel = self.get_edition(id, include_collection=False)
        if (
            edition_model.status != EditionStatus.DRAFT
            and edition_model.status != EditionStatus.ERROR
        ):
            raise ForbiddenException(
                "Edition already published",
                "The Edition cannot be deleted because it has already been published",
            )
        if edition_model.publish_time and edition_model.publish_time > datetime.now():
            self.__scheduler_service.remove_job(f"publish_edition_{str(id)}")
        edition_model.delete()

    def __validate_for_publish(
        self, edition: EditionModel, publish_now: bool = False
    ) -> None:
        """Validates that the Edition is ready to be published

        :param edition: EditionModel
        :param publish_now: bool

        :return: None
        """
        if (
            edition.status != EditionStatus.DRAFT
            and edition.status != EditionStatus.ERROR
        ):
            raise BadRequestException(detail="The Edition has already been published")
        required_keys = [
            "name",
            "description",
            "artist",
            "avatar_wearable_sku",
            "celebrity",
            "design_slot",
            "publisher",
            "rarity",
            "trademark",
            "type",
            "price",
            "reserve_percentage",
            "status",
            "avatar_wearable_id",
            "collection_id",
        ]
        validate_required_fields(edition, required_keys)
        if not edition.collection:
            raise BadRequestException(
                detail="The Edition must belong to an existing Collection"
            )
        if publish_now:
            if (
                edition.collection.status != CollectionStatus.PUBLISHED
                or not edition.collection.dapper_flow_id
            ):
                raise BadRequestException(
                    detail="The Edition must belong to a published Collection"
                )
            if self.list_editions(filters={"status": [EditionStatus.CREATING]})[0]:
                raise ConflictException(title="There is another Edition being created")

    def publish_edition(self, id: int) -> None:
        """Publishes an Edition by its id

        :param id: int

        :return: None
        """
        edition_model: EditionModel = self.get_edition(id, include_collection=True)
        self.__validate_for_publish(edition_model, True)
        self.__collections_service.update_has_published_editions(
            edition_model.collection
        )
        self.__series_service.update_serie(
            edition_model.collection.serie_id, SerieModel(has_published_editions=True)
        )
        success, dapper_flow_id = self.__minting_service.create_edition(edition_model)
        if success:
            updated_edition = EditionModel(
                status=EditionStatus.CREATING,
                dapper_flow_id=dapper_flow_id,
            )
            if (
                not edition_model.publish_time
                or edition_model.publish_time > datetime.now()
            ):
                updated_edition.publish_time = datetime.now()
            self.update_edition(id, updated_edition)

    def update_avatar_wearable_sku(
        self, edition_model: EditionModel, entity: Entity, new_short_word: str
    ) -> None:
        """Used to update the avatar_wearable_sku of an Edition when the short_word of an entity (Serie, Collection or Asset) is changed

        :param edition_model: EditionModel
        :param entity: str ("serie" or "collection" or "asset")
        :param new_short_word: str

        :return: None
        """
        sku = edition_model.avatar_wearable_sku.split("-")
        if entity == Entity.SERIE:
            sku[1] = new_short_word
        elif entity == Entity.COLLECTION:
            sku[2] = new_short_word
        elif entity == Entity.ASSET:
            sku[3] = new_short_word
        edition_model.avatar_wearable_sku = str.join("-", sku)

    def __validate_publish_time(
        self, new_edition: EditionModel, current_edition: EditionModel = None
    ) -> None:
        """If it isn't an internal update (manually published), validates that:
        - The publish_time is not in the past
        - The publish_time is after its Collection's publish_time (which can't be None)
        - The Edition hasn't any Drop with a publish_time before its own publish_time

        :param new_edition: EditionModel
        :param current_edition: EditionModel

        :return: None
        """
        if new_edition.dapper_flow_id:
            return

        tzinfo = new_edition.publish_time.tzinfo if new_edition.publish_time else None
        collection_is_updated = (
            new_edition.collection_id
            and new_edition.collection_id
            != getattr(current_edition, "collection_id", None)
        )
        publish_time_is_set = current_edition and current_edition.publish_time

        if collection_is_updated:
            collection: Collection = self.__collections_service.get_collection(
                new_edition.collection_id, include_serie=False, include_editions=False
            )
        else:
            collection: CollectionModel = current_edition.collection

        if publish_time_is_updated(new_edition, current_edition):
            if new_edition.publish_time < datetime.now(tzinfo):
                raise BadRequestException(
                    detail="The publish_time cannot be in the past"
                )
            if not collection.publish_time:
                raise BadRequestException(
                    detail="The Edition's publish_time cannot be set until the publish_time of its Collection is set"
                )
            if (
                collection.publish_time.replace(tzinfo=tzinfo)
                > new_edition.publish_time
            ):
                raise BadRequestException(
                    detail="The Edition's publish_time cannot be before the publish_time of its Collection"
                )
            if current_edition and current_edition.drop_editions:
                drops_with_publish_time_before_edition = []
                for drop_edition in current_edition.drop_editions:
                    if (
                        drop_edition.drop.publish_time
                        and drop_edition.drop.publish_time.replace(tzinfo=tzinfo)
                        < new_edition.publish_time
                    ):
                        drops_with_publish_time_before_edition.append(
                            drop_edition.drop.title
                        )
                if drops_with_publish_time_before_edition:
                    raise BadRequestException(
                        detail="The Edition's publish_time cannot be after the publish_time of its Drops: "
                        + str(drops_with_publish_time_before_edition)
                    )
        elif collection_is_updated and publish_time_is_set:
            if not collection.publish_time:
                raise BadRequestException(
                    detail="The Edition's publish_time cannot be set until the publish_time of its Collection is set"
                )
            if (
                collection.publish_time.replace(tzinfo=tzinfo)
                > current_edition.publish_time
            ):
                raise BadRequestException(
                    detail="The Edition's publish_time cannot be before the publish_time of its Collection"
                )

    def mint(
        self,
        edition: EditionModel,
        quantity: int,
        try_mint: int = 0,
        try_sell: int = 0,
        mint_success: bool = False,
        sell_success: bool = False,
        minted_nfts: List = [],
        reserved_amount: int = 0,
    ) -> Tuple[bool, list, list]:
        """Minting an Edition by its id

        :param edition: Edition
        :param quantity: int
        :param try_sell: int
        :param try_mint: int
        :param mint_success: bool
        :param sell_success: bool
        :param minted_nfts: List
        :param reserved_amount: int

        :return: Tuple[bool, list, list]
        """
        limit = int(os.environ.get("DAPPER_TRY"))

        if try_mint >= limit or try_sell >= limit:
            raise Exception("Error minting edition: too many tries")

        reserved: list = []
        reserved_index: list = []
        to_sell: list = []
        updated_edition: EditionModel

        if (
            edition.status != EditionStatus.CREATED
            and edition.status != EditionStatus.MINTED # ON_SALE
        ):
            raise BadRequestException(detail="The Edition must be published")

        try:
            try_mint += 1
            if not mint_success:
                (
                    mint_success,
                    minted_nfts,
                    reserved_amount,
                ) = self.__minting_service.mint(
                    edition=edition,
                    quantity=quantity,
                    reserved_percentage=edition.reserve_percentage,
                )
                if not mint_success:
                    raise Exception("Minted not processed")
                updated_edition = EditionModel(
                    status=EditionStatus.MINTED,
                )
                self.update_edition(edition.id, updated_edition)
                self.__nft_service.bulk_create_nft(minted_nfts, [], edition)


            #try_sell += 1
            #if mint_success and not sell_success:
            #    if not reserved_index:
            #        reserved_index: list = self.__nft_service.get_reserved_index_list(
            #            minted_nfts, reserved_amount
            #        )
            #    for index, minted in enumerate(minted_nfts):
            #        if index in reserved_index:
            #            reserved.append(minted)
            #        else:
            #            to_sell.append(minted)

            #    sell_success: bool = self.__minting_service.sell_items(
            #        minted_nfts=to_sell,
            #        edition=edition,
            #    )

            ##if sell_success:
            #    self.__nft_service.bulk_create_nft(minted_nfts, reserved_index, edition)
            #    if edition.status == EditionStatus.CREATED:
            #        updated_edition = EditionModel(
            #            status=EditionStatus.ON_SALE,
            #        )
            #        self.update_edition(edition.id, updated_edition)
            #    return sell_success, minted_nfts, reserved_amount
            #else:
            #    raise Exception("Sell items not processed")
        except:
            self.mint(
                edition,
                quantity,
                try_mint,
                try_sell,
                mint_success,
                sell_success,
                minted_nfts,
                reserved_amount,
            )

    def __create_or_update_publish_job(self, edition: EditionModel):
        """Creates or updates the publish job of an Edition

        :param edition: EditionModel

        :return: None
        """
        self.__validate_for_publish(edition)
        id = edition.id
        self.__scheduler_service.add_job(
            id=f"publish_edition_{str(id)}",
            func="swagger_server.controllers.editions_controller:publish_edition",
            args=[id],
            trigger="date",
            run_date=edition.publish_time,
            replace_existing=True,
        )

    def list_errors(
        self, filters: dict = None, page: int = None, page_size: int = None
    ) -> Tuple[List[EditionErrorModel], int]:
        """Lists all the Edition Errors

        :param filters: dict
        :param page: int
        :param page_size: int

        :return: Tuple[List[EditionErrorModel], int]
        """
        edition_error_models: List[EditionErrorModel]
        total_pages: int
        edition_error_models, total_pages = EditionErrorModel.get_all(
            filters, page, page_size
        )
        return edition_error_models, total_pages

    def create_error(
        self,
        edition_id: int,
        error: str,
        type: str = "Unknown",
        suggested_solution: str = "Try again",
    ) -> EditionError:
        """Creates a new Edition Error

        :param edition_id: int
        :param type: str
        :param error: str

        :return: EditionError
        """
        edition_error_model = EditionErrorModel(
            edition_id=edition_id,
            error=error,
            type=type,
            suggested_solution=suggested_solution,
        )
        edition_error_model.add()
        return edition_error_model.to_obj()
